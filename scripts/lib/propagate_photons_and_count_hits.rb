#!/usr/bin/env ruby
require 'fiedl/log'
require 'optparse'

options = {}
OptionParser.new do |opts|
  opts.banner = "Usage: ../lib/propagate_photons_and_count_hits.rb [options]"

  opts.on "--input-file=FILENAME", "e.g. tmp/photons_from_angle_180.i3" do |input_file|
    options[:input_file] = input_file
  end
  opts.on "--number-of-runs=INTEGER" do |number_of_runs|
    options[:number_of_runs] = number_of_runs.to_i
  end
  opts.on "--number-of-parallel-runs=INTEGER", "Number of runs to send to clsim in parallel. Too few will make the simulation slow. Too many may not work on the hardware." do |number_of_parallel_runs|
    options[:number_of_parallel_runs] = number_of_parallel_runs.to_i
  end
  opts.on "--scattering-factor=FLOAT", "Hole ice scattering factor, e.g. 0.6" do |factor|
    options[:scattering_factor] = factor.to_f
  end
  opts.on "--absorption-factor=FLOAT", "Hole ice absorption factor, e.g. 0.6" do |factor|
    options[:absorption_factor] = factor.to_f
  end
  opts.on "--save-photon-paths" do
    options[:save_photon_paths] = true
  end
  opts.on "--hole-ice=METHOD", "none (default), approximation, simulation" do |method|
    options[:hole_ice] = method.to_sym
  end
  opts.on "--seed=INTEGER", "the random ganerator seed, e.g. 123456" do |seed|
    options[:seed] = seed.to_i
  end
  opts.on "--gcd-file=FILENAME", "e.g. $I3_TESTDATA/sim/GeoCalibDetectorStatus_IC86.55380_corrected.i3.gz" do |gcd_file|
    options[:gcd_file] = gcd_file
  end
  opts.on "--ice-model=FILENAME", "e.g. $I3_SRC/clsim/resources/ice/spice_mie" do |filename|
    options[:ice_model_file] = filename
  end
  opts.on "--output-i3-file=FILENAME", "e.g. tmp/dom_hits.i3" do |output_file|
    options[:output_i3_file] = output_file
  end
  opts.on "--output-text-file=FILENAME", "e.g. results/dom_hits.txt. Each line represents a run contains the number of dom hits." do |filename|
    options[:output_text_file] = filename
  end
  opts.on "--fallback=HANDLER", "HANDLER: gpu-1-parallel OR cpu OR sleep OR skip" do |handler|
    options[:fallback] = handler
  end
  opts.on "--log-file=FILENAME", "e.g. tmp/clsim.log" do |filename|
    options[:log_file] = filename
  end
  opts.on "--show-log", "whether to display the clsim log" do
    options[:show_clsim_log] = true
  end
  opts.on "--cpu", "use the cpu rather than the gpu for the simulation" do
    options[:cpu] = true
  end

end.parse!

options[:fallback] ||= 'cpu'
options[:log_file] ||= "tmp/clsim.log"
raise "No log file defined" unless options[:log_file]

log.head "Propagate photons with clsim"
log.info "This script starts clsim to propagate photons and count the dom hits."
log.info "This is done #{options[:number_of_runs]} times in batches of #{options[:number_of_parallel_runs]}."
log.info "Each run produces one line in the results file."
log.info ""
log.configuration options

number_of_loops = options[:number_of_runs] / options[:number_of_parallel_runs]

(1..number_of_loops).each do |current_loop|
  log.section "Simulation: Loop #{current_loop} of #{number_of_loops}"
  log.info Time.now.to_s

  seed = options[:seed] + current_loop * options[:number_of_parallel_runs]
  log.info "Seed: #{seed}"

  i3_files = [options[:gcd_file], options[:input_file]] - [nil]

  log_command = if options[:show_clsim_log]
    "2>&1 | tee #{options[:log_file]}"
  else
    ">> #{options[:log_file]} 2>&1"
  end

  shell "python #{__dir__}/propagate_photons_with_clsim.py \\
    --scattering-factor=#{options[:scattering_factor]} \\
    --absorption-factor=#{options[:absorption_factor]} \\
    --ice-model=#{options[:ice_model_file]} \\
    --seed=#{seed} \\
    --output-i3-file=#{options[:output_i3_file]} \\
    --output-text-file=#{options[:output_text_file]}.temp \\
    --use-gpus=#{options[:cpu] ? 'False' : 'True'} \\
    --save-photon-paths=#{options[:save_photon_paths] ? 'True' : 'False'} \\
    --number-of-parallel-runs=#{options[:number_of_parallel_runs]} \\
    --use-hole-ice-approximation=#{(options[:hole_ice] == :approximation) ? 'True' : 'False'} \\
    --use-hole-ice-simulation=#{(options[:hole_ice] == :simulation) ? 'True' : 'False'} \\
    #{i3_files.join(' ')} \\
    #{log_command}
  "

  def raise_if_log_file_contains(error_string, options)
    if File.read(options[:log_file]).include?(error_string)
      log.error "Simulation has failed with #{error_string}"
      shell "rm #{options[:output_text_file]}"
      shell "tail -n 30 #{options[:log_file]}"
      raise "Simulation has failed with #{error_string}"
    end
  end

  raise_if_log_file_contains "Abort trap", options
  raise_if_log_file_contains "RuntimeError", options

  if File.read(options[:log_file]).include?("unknown particle id from OpenCL")
    log.warning "'unknown particle id from OpenCL' from clsim".bold

    # shell "rm #{options[:output_text_file]}.temp #{options[:log_file]}"

    def check_log_file_for_errors(options)
      if File.read(options[:log_file]).include? "ERROR"
        log.error "clsim Simulation has failed with the following errors:"
        shell "grep FATAL #{options[:log_file]}"
        shell "grep ERROR #{options[:log_file]}"

        if File.read(options[:log_file]).include? "unknown particle id from OpenCL"
          log.error "unknown particle id from OpenCL".bold
          log.error "But the fallback has already failed. This case is not handled, yet."
        end

        shell "rm #{options[:output_text_file]}"
        raise "clsim simulation has failed: unknown particle id from OpenCL"
      end

      if File.read(options[:log_file]).include? "SIMULATION RESULT\n[]"
        log.error "clsim Simulation has finished without writing down the number of hits."
        log.error "This case is not handled, yet."

        shell "rm #{options[:output_text_file]}"
        raise "clsim simulation has failed: SIMULATION RESULT []"
      end
    end

    if options[:fallback] == nil or options[:fallback] == ""
      check_log_file_for_errors(options)

    elsif options[:fallback] == 'gpu-1-parallel'
      log.warning "Trying to rerun this loop with 1 parallel event only."

      (1..options[:number_of_parallel_runs]).each do |current_sub_loop|
        log.info "\nFallback run with 1 parallel frame only. Loop #{current_sub_loop} of #{options[:number_of_parallel_runs]}.".blue
        shell "python #{__dir__}/propagate_photons_with_clsim.py \\
          --scattering-factor=#{options[:scattering_factor]} \\
          --absorption-factor=#{options[:absorption_factor]} \\
          --ice-model=#{options[:ice_model_file]} \\
          --seed=#{seed + current_sub_loop} \\
          --output-i3-file=#{options[:output_i3_file]} \\
          --output-text-file=#{options[:output_text_file]}.temp.part \\
          --use-gpus=True \\
          --save-photon-paths=False \\
          --number-of-parallel-runs=1 \\
          --number-of-frames=#{4 + 1} \\
          #{i3_files.join(' ')} \\
          >> #{options[:log_file]} 2>&1
        "
        check_log_file_for_errors(options)
        shell "cat #{options[:output_text_file]}.temp.part >> #{options[:output_text_file]}.temp"
      end

    elsif options[:fallback] == 'cpu'
      log.warning "Trying to rerun this loop with CPU rather than GPU."

      shell "python #{__dir__}/propagate_photons_with_clsim.py \\
        --scattering-factor=#{options[:scattering_factor]} \\
        --absorption-factor=#{options[:absorption_factor]} \\
        --ice-model=#{options[:ice_model_file]} \\
        --seed=#{seed} \\
        --output-i3-file=#{options[:output_i3_file]} \\
        --output-text-file=#{options[:output_text_file]}.temp \\
        --use-gpus=False \\
        --save-photon-paths=False \\
        --number-of-parallel-runs=1 \\
        #{i3_files.join(' ')} \\
        >> #{options[:log_file]} 2>&1
      "
      check_log_file_for_errors(options)

    elsif options[:fallback] == 'sleep'
      log.warning "Trying to give the GPU some time and then rerun."

      sleep_seconds = 120
      log.info "Sleeping for #{sleep_seconds} seconds."
      sleep sleep_seconds

      shell "python #{__dir__}/propagate_photons_with_clsim.py \\
        --scattering-factor=#{options[:scattering_factor]} \\
        --absorption-factor=#{options[:absorption_factor]} \\
        --ice-model=#{options[:ice_model_file]} \\
        --seed=#{seed} \\
        --output-i3-file=#{options[:output_i3_file]} \\
        --output-text-file=#{options[:output_text_file]}.temp \\
        --use-gpus=True \\
        --save-photon-paths=False \\
        --number-of-parallel-runs=#{options[:number_of_parallel_runs]} \\
        #{i3_files.join(' ')} \\
        >> #{options[:log_file]} 2>&1
      "
      check_log_file_for_errors(options)

    elsif options[:fallback] == 'skip'
      log.warning "Skipping this loop."

    else
      log.error "Fallback mode #{options[:fallback]} not handled. Skipping this loop."
    end
  end

  shell "cat #{options[:output_text_file]}.temp >> #{options[:output_text_file]}"
end
