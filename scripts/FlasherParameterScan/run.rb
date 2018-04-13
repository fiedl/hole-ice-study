#!/usr/bin/env ruby
require 'fiedl/log'
require 'optparse'
require 'pp'
require 'pawgen'

options = {}
OptionParser.new do |opts|
  opts.banner = "Usage: bundle exec ruby run.rb [options]"

  opts.on "--cluster", "--submit-to-cluster", "Run the script as array job on the cluster" do
    options[:submit_to_cluster] = true
  end
end.parse!

log.head "Flasher Simulation Parameter Scan"
log.info "README: https://github.com/fiedl/hole-ice-study/tree/master/scripts/FlasherParameterScan"


log.section "Parameter Scan Configuration"

options.merge!({
  effective_scattering_length_range: [0.05],
  hole_ice_radius_range_in_dom_radii: [0.5],
  absorption_length_range: [100],
  flasher_pulse_width_range: [0, 16, 32, 48, 64, 80, 96, 112, 127]
})

dom_radius = 0.16510
mean_scattering_angle_cosine = 0.94
options.merge!({
  scattering_length_range: options[:effective_scattering_length_range].collect { |s| s * ( 1 - mean_scattering_angle_cosine) },
  hole_ice_radius_range: options[:hole_ice_radius_range_in_dom_radii].collect { |n| n * dom_radius }
})

log.configuration options

number_of_jobs =
    options[:scattering_length_range].count *
    options[:absorption_length_range].count *
    options[:hole_ice_radius_range].count *
    options[:flasher_pulse_width_range].count
current_cluster_node_index = ENV['SGE_TASK_ID']


log.section "Grid Configuration"

if current_cluster_node_index
  log.info "\nThis is " + "cluster node #{current_cluster_node_index}".bold + ".\n"
end
log.info "There are #{number_of_jobs} parameter configurations in total."

if options[:submit_to_cluster]
  shell "qsub \\
      -l gpu \\
      -l tmpdir_size=10G \\
      -l s_rt=24:00:00 \\
      -l h_rss=12G \\
      -m ae \\
      -t 1-#{number_of_jobs} \\
    batch-job.sh \\
  "

  log.info "The results will be copied into 'cluster-results/*' by the"
  log.info "'batch-job.sh' script."

  log.success "These are your current cluster jobs:"
  shell "qstat -u $(whoami)"
else

  parameter_set_index = 0
  options[:flasher_pulse_width_range].each do |width|
    options[:effective_scattering_length_range].each do |esca|
      options[:absorption_length_range].each do |abs|
        options[:hole_ice_radius_range_in_dom_radii].each do |radius_in_dom_radii|

          parameter_set_index += 1

          need_to_perform_this_job = ((not current_cluster_node_index) or
              (current_cluster_node_index.to_i == parameter_set_index))

          if need_to_perform_this_job
            log.section "Parameters: esca=#{esca}, abs=#{abs}, pulse_width=#{width}, r=#{radius_in_dom_radii}r_dom"

            results_directory = "results/esca#{esca}_r#{radius_in_dom_radii}rdom_abs#{abs}_width#{width}"

            if File.exists?(results_directory)
              log.warning "Skipping already existing run #{results_directory}."
            else
              shell "mkdir -p #{results_directory} tmp"
              shell "cd ../FlasherSimulation && ./run.rb \\
                --hole-ice=simulation \\
                --effective-scattering-length=#{esca} \\
                --absorption-length=#{abs} \\
                --hole-ice-radius-in-dom-radii=#{radius_in_dom_radii} \\
                > ../FlasherParameterScan/tmp/flasher_simulation.log \\
                2> ../FlasherParameterScan/tmp/flasher_simulation.err"

              log.ensure_file "tmp/flasher_simulation.log"

              if File.stat("tmp/flasher_simulation.err").size > 0
                log.error "\nThis flasher simulation script run has produced errors:"
                shell "cat tmp/flasher_simulation.err"
                shell "tail -n 20 tmp/flasher_simulation.log"
                log.info "\n\n"
              end

              shell "mv tmp/flasher_simulation.* #{results_directory}/"
              shell "mv ../FlasherSimulation/results/*/* #{results_directory}/"
            end
          end

        end
      end
    end
  end

end

log.success "Done."