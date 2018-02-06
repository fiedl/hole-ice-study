#!/usr/bin/env ruby
require 'fiedl/log'
require 'optparse'
require 'pp'
require 'descriptive_statistics'
require 'csv'

options = {}
OptionParser.new do |opts|
  opts.banner = "Usage: bundle exec ruby run.rb [options]"

  opts.on "--skip-simulation" do
    options[:skip_simulation] = true
  end

  opts.on "--cluster", "--submit-to-cluster", "Run the script as array job on the cluster" do
    options[:submit_to_cluster] = true
  end

  opts.on "--plot", "Create plots for existing data" do
    options[:plot] = true
  end
end.parse!

log.head "Parameter Scan"
log.info "README: https://github.com/fiedl/hole-ice-study/tree/master/scripts/ParameterScan"

if options[:plot]
  log.warning "Skipping simulation due to --plot option."
else

  # Parameter range configuration
  #
  options.merge!({
    scattering_factor_range: [0.01, 0.1, 0.5, 1.0, 10.0],
    absorption_factor_range: [0.01, 0.1, 0.5, 1.0, 10.0],
    distance_range: [1.0, 10.0],
    number_of_photons: 1e5,
    number_of_runs: 2,
    number_of_parallel_runs: 2
  })

  log.info "This script will iterate over the following configuration"
  log.info "and perform an angular acceptance scan aiming to determine"
  log.info "the parameter configuration with best accordance to the"
  log.info "reference plot (minimizing chi squared)."
  log.info ""
  log.info "Configuration:"
  log.configuration options

  number_of_jobs = options[:scattering_factor_range].count *
      options[:absorption_factor_range].count *
      options[:distance_range].count
  current_cluster_node_index = ENV['SGE_TASK_ID']

  if current_cluster_node_index
    log.info "\nThis is " + "cluster node #{current_cluster_node_index}".bold + " of #{number_of_jobs}.\n"
  end

  if options[:skip_simulation]
    log.warning "Skipping simulation due to paraeter --skip-simulation. Continue with plotting."
  else
    log.info "There are #{number_of_jobs} parameter configurations in total."

    if options[:submit_to_cluster]

      shell "qsub \\
          -l gpu \\
          -l tmpdir_size=10G \\
          -l s_rt=0:30:00 \\
          -l h_rss=2G \\
          -m ae \\
          -t 1-#{number_of_jobs} \\
        batch-job.sh \\
      "

      log.info "The results will be copied into 'cluster-results/*' by the"
      log.info "'batch-job.sh' script."

    elsif not options[:submit_to_cluster]

      parameter_set_index = 0
      options[:distance_range].each do |dst|
        options[:scattering_factor_range].each do |sca|
          options[:absorption_factor_range].each do |abs|

            parameter_set_index += 1

            need_to_perform_this_job = ((not current_cluster_node_index) or
                (current_cluster_node_index.to_i == parameter_set_index))

            if need_to_perform_this_job
              log.section "Parameters: sca=#{sca}, abs=#{abs}, dst=#{dst}"

              results_directory = "results/sca#{sca}_abs#{abs}_dst#{dst}"

              if File.exists?(results_directory)
                log.warning "Skipping already existing run #{results_directory}."
              else
                shell "mkdir -p #{results_directory} tmp"
                shell "cd ../AngularAcceptance && ./run.rb \\
                  --scattering-factor=#{sca} \\
                  --absorption-factor=#{abs} \\
                  --distance=#{dst} \\
                  --number-of-photons=#{options[:number_of_photons]} \\
                  --number-of-runs=#{options[:number_of_runs]} \\
                  --number-of-parallel-runs=#{options[:number_of_parallel_runs]}
                  > ../ParameterScan/tmp/angular_acceptance_script.log \\
                  2> ../ParameterScan/tmp/angular_acceptance_script.err"

                log.ensure_file "tmp/angular_acceptance_script.log"

                if File.stat("tmp/angular_acceptance_script.err").size > 0
                  log.error "\nThis angular acceptance script run has produced errors:"
                  shell "cat tmp/angular_acceptance_script.err"
                  shell "tail -n 20 tmp/angular_acceptance_script.log"
                  log.info "\n\n"
                end

                shell "mv tmp/angular_acceptance_script.* #{results_directory}/"
                shell "mv ../AngularAcceptance/results/current/* #{results_directory}/"
              end
            end

          end
        end
      end

    end
  end

  if options[:submit_to_cluster]

    log.success "These are your current cluster jobs:"
    shell "qstat -u $(whoami)"

  end
end

if options[:plot] or (not options[:submit_to_cluster] and not current_cluster_node_index)

  log.section "Finding the best parameters via minimal chi-squared"
  log.info "Collecting data from simulation results."
  results_files = (Dir.glob("results/**/options.txt") + Dir.glob("cluster-results/**/options.txt"))
  results = results_files.collect do |options_file|
    configuration = eval(File.read(options_file))
    {
      scattering_factor: configuration[:scattering_factor],
      distance: configuration[:distance],
      absorption_factor: configuration[:absorption_factor]
    }.merge(configuration[:chi_squared_results].values.first)
  end

  log.info "Writing results into table data file."
  shell "mkdir -p results tmp"
  #CSV.open("results/results.csv", "wb", col_sep: " ") do |csv|
  #  csv << results.first.keys
  #  results.each do |result|
  #    csv << result.values if result[:distance] == 10.0
  #  end
  #end
  #log.ensure_file "results/results.csv"
  #
  log.info "Plotting 3d plot for separate distances."
  distances = results.collect { |result| result[:distance] }.uniq
  distances.each do |distance|
    CSV.open("tmp/dst#{distance}.csv", "wb", col_sep: " ") do |csv|
      csv << results.first.keys
      results.each do |result|
        csv << result.values if result[:distance] == distance
      end
    end

    gnuplot_commands = "
      set term png
      set dgrid3d 30,30
      set hidden3d
      set title 'Parameter scan'
      set xlabel 'scattering factor'
      set ylabel 'absorption factor'
      set zlabel 'chi squared nu'
      splot 'tmp/dst#{distance}.csv' \\
        using 1:3:7 \\
        with lines \\
        title 'Distance #{distance}m'
    "
    File.open("tmp/dst#{distance}.gnuplot", 'w') { |file| file.write gnuplot_commands }
    shell "gnuplot tmp/dst#{distance}.gnuplot > tmp/dst#{distance}.png"
  end

  log.success "Finished ParameterScan."

end