#!/usr/bin/env ruby
require 'fiedl/log'
require 'optparse'
require 'pp'
require 'descriptive_statistics'
require 'active_support'
require 'time'

global_options = {}
OptionParser.new do |opts|
  opts.banner = "Creates plots from existing data. Usage: bundle exec ruby run.rb [options] data-directories"

  opts.on "--nominal", "Plot against icecube nominal rather than hole-ice acceptance." do
    global_options[:nominal] = true
  end
  opts.on "--no-reference", "Skip the reference curve in plot." do
    global_options[:no_reference] = true
  end
end.parse!
command_line_arguments = ARGV

log.head "Generate Angular Acceptance Plots From Existing Data"
log.info "README: https://github.com/fiedl/hole-ice-study/tree/master/scripts/AngularAcceptance"

log.section "Data"
data_directories = command_line_arguments
data_directories = ['cluster-results', 'results', 'tmp'] if data_directories.none?
data_directories.select! { |directory| File.directory?(directory) }

log.info "Found data directories:\n"
data_directories.each { |directory| log.info "- #{directory}" }
raise "No data directories found" if data_directories.none?
log.info ""

options_files = data_directories.collect { |directory| Dir["#{directory}/**/options.txt"] }.flatten
log.info "Found configurations:\n"
options_files.each { |file| log.info "- #{file}" }
raise "No options.txt found" if options_files.none?
log.info ""

configurations = options_files.collect { |options_file| eval(File.read(options_file)).merge({
  options_file: options_file,
  data_directory: File.dirname(options_file)
}) }

configurations.each_with_index do |options, index|

  log.head options[:run_id]
  log.configuration options.slice(:hole_ice_effective_scattering_length, :distance, :number_of_photons,
      :options_file, :data_directory)

  if File.exists? "#{options[:data_directory]}/plot_with_reference.png"
    log.warning "Skipping already existing plot #{options[:data_directory]}/plot_with_reference.png"
  else

    log.section "Compare to reference plot"
    log.info "The simulation data is compared to the reference plot by"
    log.info "showing both in one image and by showing reduced chi-suqre."
    compare_options = {
      chi_squared_nu_plot_file: "#{options[:data_directory]}/plot_with_reference.png",
      chi_squared_results_file: "#{options[:data_directory]}/chi_square_results.txt",
      chi_squared_gnuplot_log_file: "#{options[:data_directory]}/chi_square_gnuplot.log",
      chi_squared_data_file: "#{options[:data_directory]}/angle_hits_deviation_and_photons.txt",
      chi_squared_data_without_zero_errors_file: "#{options[:data_directory]}/angle_hits_deviation_and_photons_without_zero_errors.txt"
    }
    log.configuration compare_options
    options.merge! compare_options

    log.info "\nSkipping data rows with zero error".blue
    log.info "because they would be weighted with infinity in chi square."
    data_rows = File.read(options[:chi_squared_data_file]).split("\n")
    data_rows.select! do |row|
      columns = row.split(" ")
      if columns[2] == "0.0"
        log.warning "Skipping data row #{row}"
        false
      else
        true
      end
    end
    File.open(options[:chi_squared_data_without_zero_errors_file], 'w') { |file| file.write(data_rows.join("\n")) }
    log.info ""

    shell "ruby lib/compare_simulation_to_reference.rb \\
      --input-files='#{options[:chi_squared_data_without_zero_errors_file]}' \\
      --data-label='#{options[:run_id]}, esca=#{options[:hole_ice_effective_scattering_length].round(3)}m, r=#{options[:hole_ice_radius_in_dom_radii]}r_{dom}' \\
      --output-plot-file='#{options[:chi_squared_nu_plot_file]}' \\
      --results-file='#{options[:chi_squared_results_file]}' \\
      --gnuplot-log='#{options[:chi_squared_gnuplot_log_file]}' \\
      #{'--use-hole-ice' if options[:hole_ice] && !global_options[:nominal]}
    "
    log.ensure_file options[:chi_squared_nu_plot_file]
    log.ensure_file options[:chi_squared_results_file]

    log.info "Chi-squared results:"
    chi_squared_results = eval(File.read(options[:chi_squared_results_file]))
    log.configuration chi_squared_results
    options.merge!({
      chi_squared_results: chi_squared_results,
      agreement: chi_squared_results.values.first['chi^2_nu']
    })

    log.section "Update options.txt"
    File.open(options[:options_file], 'w') { |file| PP.pp(options, file) }

    log.success "Done processing #{options[:run_id]}"
  end
end

log.head "Parameter scan plots"
log.section "Extract parameters and agreements"
agreement_data = "effective_scattering_length hole_ice_radius_in_dom_radii agreement duration\n" + configurations.collect { |options|
  absorption_length = options[:hole_ice_absorption_length]
  effective_scattering_length = options[:hole_ice_effective_scattering_length]
  hole_ice_radius_in_dom_radii = options[:hole_ice_radius_in_dom_radii]
  agreement = options[:agreement]
  duration = Time.parse(options[:propagation_finished_at]) - Time.parse(options[:started_at])
  if agreement
    "#{effective_scattering_length} #{hole_ice_radius_in_dom_radii} #{agreement} #{duration}"
  else
    nil
  end
}.join("\n")
File.open("parameter_scan.txt", "w") { |f| f.write agreement_data }
log.ensure_file "parameter_scan.txt"
