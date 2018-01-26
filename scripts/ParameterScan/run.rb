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
end.parse!

log.head "Parameter Scan"
log.info "README: https://github.com/fiedl/hole-ice-study/tree/master/scripts/ParameterScan"


# Parameter range configuration
#
options.merge!({
  scattering_factor_range: [0.0001, 0.5, 1.0, 100.0],
  absorption_factor_range: [0.0001, 0.5, 1.0, 100.0],
  distance_range: [1.0, 2.0],
  number_of_photons: 1e5,
  number_of_runs: 5,
  number_of_parallel_runs: 5
})

log.info "This script will iterate over the following configuration"
log.info "and perform an angular acceptance scan aiming to determine"
log.info "the parameter configuration with best accordance to the"
log.info "reference plot (minimizing chi squared)."
log.info ""
log.info "Configuration:"
log.configuration options

if options[:skip_simulation]
  log.warning "Skipping simulation due to paraeter --skip-simulation. Continue with plotting."
else
  log.info "Looping over parameter ranges:"

  options[:distance_range].each do |dst|
    options[:scattering_factor_range].each do |sca|
      options[:absorption_factor_range].each do |abs|

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
            --number-of-parallel-runs=#{options[:number_of_parallel_runs]} \\
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

log.section "Finding the best parameters via minimal chi-squared"
log.info "Collecting data from simulation results."
results = Dir.glob("results/*").collect do |result_directory|
  if File.exists? "#{result_directory}/data/options.txt"
    configuration = eval(File.read("#{result_directory}/data/options.txt"))
    {
      scattering_factor: configuration[:scattering_factor],
      distance: configuration[:distance],
      absorption_factor: configuration[:absorption_factor]
    }.merge(configuration[:chi_squared_results].values.first)
  else
    log.warning "File #{result_directory}/data/options.txt is missing. Skipping this parameter set."
    nil
  end
end
results = results - [nil]

log.info "Writing results into table data file."
CSV.open("results/results.csv", "wb", col_sep: " ") do |csv|
  csv << results.first.keys
  results.each do |result|
    csv << result.values if result[:distance] == 10.0
  end
end
log.ensure_file "results/results.csv"

log.info "Plotting 3d plot for separate distances."
distances = results.collect { |result| result[:distance] }
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
