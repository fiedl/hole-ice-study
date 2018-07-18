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

# Configure specific parameter points, i.e. pairs of esca and r
# for the parameter scan.
parameter_points = []

# # Grid scan:
# # https://github.com/fiedl/hole-ice-study/issues/59
# #
# effective_scattering_length_range = (0.01..0.10).step(0.01).collect { |v| v.round(2) } + (0.25..2.25).step(0.25).collect { |v| v.round(2) }
# hole_ice_radius_range_in_dom_radii = [0.01] + (0.3..1.8).step(0.1).collect { |v| v.round(2) }
# effective_scattering_length_range.each do |esca|
#   hole_ice_radius_range_in_dom_radii.each do |r_r_dom|
#     parameter_points << {radius_in_dom_radii: r_r_dom, esca: esca}
#   end
# end

# # 1D scan for swedish-camera radius
# # https://github.com/fiedl/hole-ice-study/issues/92
# #
# radius_in_dom_radii = 0.5
# escas = (0.001..0.01).step(0.001)
# escas.each { |esca| parameter_points << {radius_in_dom_radii: radius_in_dom_radii, esca: esca.round(3)} }

# # Additional points for contour plot
# # https://github.com/fiedl/hole-ice-study/issues/59#issuecomment-405671824
# #
# parameter_points << {radius_in_dom_radii: 1.4, esca: 0.4}
# parameter_points << {radius_in_dom_radii: 1.4, esca: 0.5}
# parameter_points << {radius_in_dom_radii: 1.4, esca: 0.6}
#
# parameter_points << {radius_in_dom_radii: 2.0, esca: 0.5}
# parameter_points << {radius_in_dom_radii: 2.1, esca: 0.6}
# parameter_points << {radius_in_dom_radii: 1.9, esca: 0.4}

# Random data poins within interesting area
#
100.times do
  x = Random.rand * (2.20 - 0.25) + 0.25
  y_upper = 0.513 * x - 0.128
  y_lower = 0.462 * x - 0.415
  y = Random.rand * (y_upper - y_lower) + y_lower

  parameter_points << {radius_in_dom_radii: x, esca: y}
end

dom_radius = 0.16510
mean_scattering_angle_cosine = 0.94

parameter_points.each do |params|
  params[:radius] = params[:radius_in_dom_radii] * dom_radius
  params[:sca] = params[:esca] * (1 - mean_scattering_angle_cosine)
end

options.merge!({
  absorption_length: 100,
  flasher_pulse_width: 127,
  flasher_pulse_brightness: 127,
  thinning_factor: 0.1,
  parameter_sets: parameter_points
})

log.configuration options

number_of_jobs = options[:parameter_sets].count
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
      -l s_rt=0:29:00 \\
      -l h_rss=30G \\
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
  options[:parameter_sets].each do |parameter_set|
    parameter_set_index += 1

    radius_in_dom_radii = parameter_set[:radius_in_dom_radii]
    esca = parameter_set[:esca]
    abs = options[:absorption_length]
    width = options[:flasher_pulse_width]
    brightness = options[:flasher_pulse_brightness]
    thinning_factor = options[:thinning_factor] || 1.0

    need_to_perform_this_job = ((not current_cluster_node_index) or
        (current_cluster_node_index.to_i == parameter_set_index))

    if need_to_perform_this_job
      log.section "Parameters: esca=#{esca}, abs=#{abs}, pulse_width=#{width}, brightness=#{brightness}, r=#{radius_in_dom_radii}r_dom"

      results_directory = "results/esca#{esca}_r#{radius_in_dom_radii}rdom_abs#{abs}_width#{width}_bright#{brightness}"

      if File.exists?(results_directory)
        log.warning "Skipping already existing run #{results_directory}."
      else
        shell "mkdir -p #{results_directory} tmp"
        shell "cd ../FlasherSimulation && ./run.rb \\
          --hole-ice=simulation \\
          --effective-scattering-length=#{esca} \\
          --absorption-length=#{abs} \\
          --hole-ice-radius-in-dom-radii=#{radius_in_dom_radii} \\
          --width=#{width} \\
          --brightness=#{brightness} \\
          --thinning-factor=#{thinning_factor} \\
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

        shell "rm #{results_directory}/*.i3"
      end
    end
  end

end

log.success "Done."
