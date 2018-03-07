#!/usr/bin/env ruby
require 'fiedl/log'
require 'optparse'
require 'pp'
require 'descriptive_statistics'
require 'pawgen'

options = {}
OptionParser.new do |opts|
  opts.banner = "Usage: bundle exec ruby run.rb [options]"

  opts.on "--cluster", "Configure for running on the cluster: Skip plotting." do
    options[:cluster] = true
  end

  opts.on "--resume" do
    options[:resume] = true
  end
  opts.on "--skip-propagation" do
    options[:skip_propagation] = true
  end

  opts.on "--scattering-factor=SCA", "Something between 0.0 and 1.0." do |sca|
    options[:scattering_factor] = sca.to_f
  end
  opts.on "--absorption-factor=ABS", "Something between 0.0 and 1.0." do |abs|
    options[:absorption_factor] = abs.to_f
  end
  opts.on "--distance=DST", "Distance to shoot photons from to the dom in metres, e.g. 1.0" do |dst|
    options[:distance] = dst.to_f
  end
  opts.on "--number-of-photons=NUM", "e.g. 1e5" do |num|
    options[:number_of_photons] = num.to_f
  end
  opts.on "--number-of-runs=NUM", "e.g. 10" do |num|
    options[:number_of_runs] = num.to_f
  end
  opts.on "--number-of-parallel-runs=NUM", "e.g. 5" do |num|
    options[:number_of_parallel_runs] = num.to_f
  end
  opts.on "--angles=LIST", "e.g. 0,45,90,180" do |list|
    options[:angles] = list.split(",").map(&:to_i)
  end
  opts.on "--plane-wave", "Start photons from a plane rather than a point." do
    options[:plane_wave] = true
  end
  opts.on "--cylinder-shift=METRES", "Shift the hole-ice cylinder x position by this value in metres to study asymmetries." do |metres|
    options[:cylinder_shift] = metres
  end
end.parse!



log.head "Angular Acceptance Experiments"
log.info "README: https://github.com/fiedl/diplomarbeit/tree/master/scripts/AngularAcceptance"

# Check requirements
#
log.section "Check requirements"
(log.error 'Environment variable $I3_PORTS is not set, which is needed for clsim working with geant4.'; raise('Requirements not met.')) unless ENV['I3_PORTS']
(log.error 'Environment variable $I3_TESTDATA is not set.'; raise('Requirements not met.')) unless ENV['I3_TESTDATA']
(log.error "$I3_TESTDATA (#{ENV['I3_TESTDATA']}) does not exist in the file system."; raise('Requirements not met.')) unless File.exists?(ENV['I3_TESTDATA'])
(log.error 'Environment variable $I3_SRC is not set.'; raise('Requirements not met.')) unless ENV['I3_SRC']
(log.error "$I3_SRC (#{ENV['I3_SRC']}) does not exist in the file system."; raise('Requirements not met.')) unless File.exists?(ENV['I3_SRC'])
(log.error "IceSim not loaded. Please navigate to your icecube-simulation build and run \`./env-shell.sh\`. If you've followed the [install guide](...), just run \`ice-env\`."; raise('Requirements not met.')) unless ENV['I3_SHELL']
log.success "OK."


# Clean-up
#
log.section "Clean-up"
if options[:resume]
  log.info "Skipping clean-up because using --resume."
else
  shell "rm -r tmp/*"
  shell "mkdir -p tmp"
end


# Run id
log.section "Run id"
pwgen = PawGen.new.set_length!(8).exclude_ambiguous!
run_id_options = {
  run_id: "Run-#{Time.now.year}-#{pwgen.anglophonemic}",
  started_at: Time.now.to_s
}
log.configuration run_id_options
options.merge! run_id_options


# Detector geometry
#
log.section "Detector geometry"
dom_radius = 0.16510
detector_geometry_options = {
  gcd_file: "$I3_TESTDATA/sim/GeoCalibDetectorStatus_IC86.55380_corrected.i3.gz",
  ice_model_file: "$I3_SRC/clsim/resources/ice/spice_mie",
  seed: 123456,
  hole_ice_cylinder_positions: [
    # For the z-ranges, see: https://github.com/fiedl/hole-ice-study/issues/34
    [-256.02301025390625 + options[:cylinder_shift].to_f, -521.281982421875, 0],  # bubble column of the hole ice
    [-256.02301025390625 + dom_radius + 0.02, -521.281982421875, 500.0],          # cable
  ],
  hole_ice_cylinder_radii: [
    0.08,
    0.02
  ]
}
log.configuration detector_geometry_options
options.merge! detector_geometry_options


# Create geometry file with hole-ice cylinder
#
log.section "Create geometry file with hole-ice cylinder"
options.merge!({
  gcd_file_with_hole_ice: "tmp/gcd_with_hole_ice.i3",
  create_gcd_log: "tmp/create_gcd_with_hole_ice.log"
})

shell "python #{__dir__}/lib/create_gcd_file_with_hole_ice.py \\
  --input-gcd-file=#{options[:gcd_file]} \\
  --output-gcd-file=#{options[:gcd_file_with_hole_ice]} \\
  " + options[:hole_ice_cylinder_positions].enum_for(:each_with_index).collect { |pos, index|
    "--cylinder-x=#{options[:hole_ice_cylinder_positions][index][0]} \\
    --cylinder-y=#{options[:hole_ice_cylinder_positions][index][1]} \\
    --cylinder-z=#{options[:hole_ice_cylinder_positions][index][2]} \\
    --cylinder-radius=#{options[:hole_ice_cylinder_radii][index]} \\
    "
  }.join + "> #{options[:create_gcd_log]} 2>&1"

log.ensure_file options[:gcd_file_with_hole_ice], show_log: options[:create_gcd_log]


# Create photon frames
#
log.section "Create photon frames"

photon_frames_options = {
  dom_index: [1, 1],
  dom_position: [-256.02301025390625, -521.281982421875, 500],
  distance: options[:distance] || 1.0,
  angles: options[:angles] || [0,10,20,30,32,45,60,75,90,105,120,135,148,160,170,180],
  number_of_photons: options[:number_of_photons] || 1e5,
  number_of_runs: options[:number_of_runs] || 2,
  number_of_parallel_runs: options[:number_of_parallel_runs] || 2
}
options.merge! photon_frames_options

if options[:resume]
  log.warning "Skipping creating photon frames because using --resume."

  if (n = Dir.glob("tmp/photons_from_angle_*.i3").count) != (options[:number_of_angles] || options[:angles].count)
    log.error "There are #{n} tmp/photons_from_angle_*.i3 files, but expecting #{options[:number_of_angles]} angles."
    raise "Number of tmp/photons_from_angle_*.i3 files does not match."
  end
else

  log.configuration photon_frames_options

  # shell "python lib/create_qframe_i3_file_with_photons_from_angle.py \\
  #   --photon-position=#{options[:dom_position].join(',')} \\
  #   --photon-direction-theta=1.2 \\
  #   --photon-direction-phi=0 \\
  #   --number-of-photons=#{options[:number_of_photons]} \\
  #   --number-of-runs=#{options[:number_of_runs]} \\
  #   --output-file=tmp/generated_photons.i3
  # "

  shell "ruby lib/create_qframe_i3_files_with_photons_from_all_angles.rb \\
    --dom-position=#{options[:dom_position].join(',')} \\
    --distance=#{options[:distance]} \\
    #{"--angles=#{options[:angles].join(',')}" if options[:angles]} \\
    #{"--number-of-angles=#{options[:number_of_angles]}" if options[:number_of_angles]} \\
    --gcd-file=#{options[:gcd_file_with_hole_ice]} \\
    --output-file-pattern=tmp/photons_from_angle_ANGLE.i3 \\
    --number-of-photons-per-angle=#{options[:number_of_photons]} \\
    --number-of-runs=#{options[:number_of_parallel_runs]} \\
    #{"--plane-wave" if options[:plane_wave]} \\
    #{"--plane-wave-size=#{options[:distance]}" if options[:plane_wave]} \\
    --seed=#{options[:seed]}
  "
end
if options[:angles]
  log.ensure_file "tmp/photons_from_angle_#{options[:angles].first.to_s.rjust(3, "0")}.i3"
else
  log.ensure_file "tmp/photons_from_angle_000.i3"
end


# Propagate the photons with clsim.
#
log.section "Propagate photons with clsim"
global_propagation_options = {
  hole_ice: :simulation,  # false, :approximation, :simulation
  scattering_factor: options[:scattering_factor] || 0.02,
  absorption_factor: options[:absorption_factor] || 1.0,
  save_photon_paths: false,
  propagation_log_file: "tmp/propagation.log",
  clsim_error_fallback: 'skip' # or: gpu-1-parallel OR cpu OR sleep OR skip
}
options.merge! global_propagation_options
log.configuration global_propagation_options

if options[:skip_propagation]
  log.warning "Skipping propagation due to --skip-propagation."
else
  log.info ""
  log.info 'To monitor the progress, try `tail -f tmp/propagation.log`.'

  Dir.glob('tmp/photons_from_angle_*.i3').each do |photons_from_angle_i3_file|
    angle = photons_from_angle_i3_file.split("/").last.gsub("photons_from_angle_", "").gsub(".i3", "")

    log.info ""
    log.info "Propagating #{photons_from_angle_i3_file} with clsim ...".blue
    log.info Time.now.to_s

    propagation_options = {
      input_file: photons_from_angle_i3_file,
      seed: options[:seed] + 100 * angle.to_i,
      output_i3_file: photons_from_angle_i3_file.gsub("tmp/", "tmp/propagated_"),
      output_text_file: photons_from_angle_i3_file.gsub(".i3", "_dom_hits.txt"),
      output_separate_data_file: "tmp/angle_hits_and_photons_#{angle}.txt",
      output_mean_data_file: "tmp/angle_mean_hits_std_deviation_and_photons_#{angle}.txt",
      clsim_log_file: "tmp/clsim_#{angle}.log",
    }

    if options[:resume] && File.exists?(propagation_options[:output_text_file]) && File.read(propagation_options[:output_text_file]).split("\n").count == options[:number_of_runs]
      log.warning "Skipping recreating existing file #{propagation_options[:output_text_file]} because using --resume."
    else
      shell "rm #{propagation_options[:output_text_file]}" if options[:resume]

      shell "ruby lib/propagate_photons_and_count_hits.rb \\
        --input-file=#{propagation_options[:input_file]} \\
        --number-of-runs=#{options[:number_of_runs]} \\
        --number-of-parallel-runs=#{options[:number_of_parallel_runs]} \\
        --fallback=#{options[:clsim_error_fallback]} \\
        --hole-ice=#{options[:hole_ice]} \\
        --scattering-factor=#{options[:scattering_factor]} \\
        --absorption-factor=#{options[:absorption_factor]} \\
        #{'--save-photon-paths' if options[:save_photon_paths]} \\
        --seed=#{propagation_options[:seed]} \\
        --ice-model=#{options[:ice_model_file]} \\
        --output-i3-file=#{propagation_options[:output_i3_file]} \\
        --output-text-file=#{propagation_options[:output_text_file]} \\
        --log-file=#{propagation_options[:clsim_log_file]} \\
        > #{options[:propagation_log_file]} 2>&1
      "
      log.ensure_file propagation_options[:output_i3_file], show_log: [options[:propagation_log_file], propagation_options[:clsim_log_file]].join(" ")
    end
    log.ensure_file propagation_options[:output_text_file], show_log: [options[:propagation_log_file], propagation_options[:clsim_log_file]].join(" ")

    if File.exist?(propagation_options[:clsim_log_file])
      if File.readlines(propagation_options[:clsim_log_file]).grep(/error/).size > 0
        log.error "clsim log #{propagation_options[:clsim_log_file]} contains errors"
        shell "tail -n 20 #{propagation_options[:clsim_log_file]}"
        raise "clsim errors"
      end
    else
      log.warning "File #{propagation_options[:clsim_log_file]} does not exist. Maybe the propagation for this angle has been skipped."
    end

    log.info "Calculating and writing data.".blue
    hits_series = File.read(propagation_options[:output_text_file]).strip.split("\n").collect do |hits|
      hits.strip.to_i
    end

    if hits_series.any?
      hits_mean = hits_series.mean
      hits_standard_deviation = hits_series.standard_deviation

      File.open(propagation_options[:output_separate_data_file], 'w') do |file|
        hits_series.each do |number_of_hits|
          file.write "#{angle} #{number_of_hits} #{options[:number_of_photons]}\n"
        end
      end
      log.ensure_file propagation_options[:output_separate_data_file]

      File.open(propagation_options[:output_mean_data_file], 'w') do |file|
        file.write "#{angle} #{hits_mean} #{hits_standard_deviation} #{options[:number_of_photons]}\n"
      end
      log.ensure_file propagation_options[:output_mean_data_file]
    end
  end
  log.info Time.now.to_s
  options[:propagation_finished_at] = Time.now.to_s
end

# Plotting dom hits against angle.
#
log.section "Plotting dom hits against angle"

shell "cat tmp/angle_mean_hits_std_deviation_and_photons_*.txt \\
  |grep -v '   ' \\
  > tmp/angle_hits_deviation_and_photons.txt"
log.ensure_file "tmp/angle_hits_deviation_and_photons.txt"

if options[:cluster]
  log.warning "Skipping plot because running on the cluster. To plot later, use lib/plot.rb."
else
  gnuplot_commands = "
    set term png
    set title 'Angular Acceptance #{options[:run_id]}'
    set xlabel 'cos(/Symbol h)'
    set ylabel 'relative sensitivity'
    set logscale y
    plot 'tmp/angle_hits_deviation_and_photons.txt' \\
      using (cos(\$1 / 360 * 2 * pi)):(\$2 / \$4):(\$3 / \$4) \\
      with errorbars \\
      title 'Distance #{options[:distance]}m' \\
      ps 5
  "
  File.open("tmp/plot.gnuplot", 'w') { |file| file.write gnuplot_commands }
  log.ensure_file "tmp/plot.gnuplot"
  log.info gnuplot_commands

  shell "gnuplot tmp/plot.gnuplot > tmp/plot.png"
  log.ensure_file "tmp/plot.png"
end


# Writing histograms.
#
log.section "Writing hits histograms"
log.info "These histograms can be used to check whether the"
log.info "variance of the simulated hits is plausible."
shell "mkdir tmp/histograms"
histogram_options = {
  hits_histograms_input_files: "tmp/photons_from_angle_*_dom_hits.txt",
  hits_histograms_input_columns: "hits",
  hits_histograms_output_file_pattern: "tmp/histograms/hits_histogram_ANGLE.png",
  hits_histograms_min_bin: 0,
  hits_histograms_max_bin: 300,
  hits_histograms_log: "tmp/hits_histograms.log"
}
log.configuration histogram_options
options.merge! histogram_options

if options[:cluster]
  log.warning "Skipping creating histograms because running on the cluster. To create them later, use lib/create_histograms_for_hits.rb."
else
  shell "ruby lib/create_histograms_for_hits.rb \\
    --input-files=#{options[:hits_histograms_input_files]} \\
    --input-columns=#{options[:hits_histograms_input_columns]} \\
    --output-file-pattern=#{options[:hits_histograms_output_file_pattern]} \\
    --min-bin=#{options[:hits_histograms_min_bin]} \\
    --max-bin=#{options[:hits_histograms_max_bin]} \\
    > #{options[:hits_histograms_log]}
  "
  log.ensure_file options[:hits_histograms_log]
  log.ensure_file "tmp/histograms/hits_histogram_000.png"
end

# Writing down used options.
#
log.section "Exporting options"
pp options
File.open("tmp/options.txt", 'a') { |file| PP.pp(options, file) }
log.ensure_file "tmp/options.txt"


# Generate plots.
#
log.section "Comparing to reference plot"
if options[:cluster]
  log.warning "Skipping comparison plots because running on the cluster."
else
  shell "ruby lib/plot.rb ./tmp"
end


# Read in options, which might have been changed
# by the plots script.
#
options = eval(File.read("tmp/options.txt"))


# Writing README
#
log.section "Writing README"
readme_content = "# Angular Acceptance Simulation #{options[:run_id]}
#{Time.now.to_s}

## Plot

```gnuplot
#{gnuplot_commands}
```

![plot](plot.png)

## Configuration

```ruby
#{options.pretty_inspect}
```

## Comparison to reference plot

![with reference plot](plot_with_reference.png)

```ruby
#{File.read(options[:chi_squared_results_file])}
```

## Hits histograms

These histograms may help to check if the variances of the
hits for each angle look plausible.

" + Dir.glob(options[:hits_histograms_output_file_pattern].gsub("ANGLE", "*")).collect { |histogram|
  "<img src=\"histograms/#{histogram.split('/').last}\" width=\"30%\" />"
}.join("\n") + "

This README has been generated by `scripts/AngularAcceptance/run.rb`
"
File.open("tmp/README.md", 'w') { |file| file.write readme_content }
log.ensure_file "tmp/README.md"


# Exporting data
#
log.section "Exporting results"
shell "rm -r results/current/*"
shell "mkdir -p results/current/data"
shell "cp tmp/*.txt results/current/data/"
shell "cp tmp/plot.png tmp/plot.gnuplot results/current/"
shell "cp #{options[:chi_squared_nu_plot_file]} results/current/"
shell "cp #{options[:chi_squared_results_file]} results/current/data/"
shell "cp -r tmp/histograms results/current/"
shell "cp tmp/*.log results/current/"
shell "cp tmp/README.md results/current/"
log.ensure_file "results/current"
shell "ls results/current"

log.success "Finished."
