#!/usr/bin/env ruby
require 'fiedl/log'
require 'optparse'

options = {}
OptionParser.new do |opts|
  opts.banner = "Usage: bundle exec ruby run.rb [options]"

  opts.on "--scattering-factor=SCA", "Something between 0.0 and 1.0." do |sca|
    options[:scattering_factor] = sca.to_f
  end
  opts.on "--absorption-factor=ABS", "Something between 0.0 and 1.0." do |abs|
    options[:absorption_factor] = abs.to_f
  end
  opts.on "--distance=DST", "Distance to shoot photons from to the dom in metres." do |dst|
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
  opts.on "--save-photon-paths", "for example, to visualize them in steamshovel" do
    options[:save_photon_paths] = true
  end
  opts.on "--cpu", "use the cpu rather than the gpu for the simulation" do
    options[:cpu] = true
  end
  opts.on "--angle=DEGREES", "e.g. 45" do |angle|
    options[:angles] = [angle.to_i]
  end
  opts.on "--plane-wave", "Start photons from a plane rather than a point." do
    options[:plane_wave] = true
  end
  opts.on "--cylinder-shift=METRES", "Shift the hole-ice cylinder x position by this value in metres to study asymmetries." do |metres|
    options[:cylinder_shift] = metres
  end
end.parse!

log.head "Firing Range: Fire Photons Onto a DOM"
log.info "This is a simple test to check whether clsim is working."
log.info "README: https://github.com/fiedl/diplomarbeit/tree/master/scripts/FiringRange"


# Check requirements
#
log.section "Check requirements"
(log.error 'Environment variable $I3_PORTS is not set, which is needed for clsim working with geant4.'; raise('Requirements not met.')) unless ENV['I3_PORTS']
(log.error 'Environment variable $I3_TESTDATA is not set.'; raise('Requirements not met.')) unless ENV['I3_TESTDATA']
(log.error "$I3_TESTDATA (#{ENV['I3_TESTDATA']}) does not exist in the file system."; raise('Requirements not met.')) unless File.exists?(ENV['I3_TESTDATA'])
(log.error "IceSim not loaded. Please navigate to your icecube-simulation build and run \`./env-shell.sh\`. If you've followed the [install guide](...), just run \`ice-env\`."; raise('Requirements not met.')) unless ENV['I3_SHELL']
log.success "OK."


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
    #[-256.02301025390625 + options[:cylinder_shift].to_f, -521.281982421875, 0],  # outer column
    #[-256.02301025390625 + options[:cylinder_shift].to_f, -521.281982421875, 0],  # bubble column of the hole ice
    [-256.02301025390625 + dom_radius + 0.02, -521.281982421875, 500.0],          # cable
  ],
  hole_ice_cylinder_radii: [
    #0.30,
    #0.08,
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

if File.exist? options[:gcd_file_with_hole_ice]
  log.warning "File #{options[:gcd_file_with_hole_ice]} exists. Please remove it if you want it to be recreated."
else
  shell "mkdir -p tmp"
  shell "python #{__dir__}/../AngularAcceptance/lib/create_gcd_file_with_hole_ice.py \\
    --input-gcd-file=#{options[:gcd_file]} \\
    --output-gcd-file=#{options[:gcd_file_with_hole_ice]} \\
    " + options[:hole_ice_cylinder_positions].enum_for(:each_with_index).collect { |pos, index|
      "--cylinder-x=#{options[:hole_ice_cylinder_positions][index][0]} \\
      --cylinder-y=#{options[:hole_ice_cylinder_positions][index][1]} \\
      --cylinder-z=#{options[:hole_ice_cylinder_positions][index][2]} \\
      --cylinder-radius=#{options[:hole_ice_cylinder_radii][index]} \\
      "
    }.join + "> #{options[:create_gcd_log]} 2>&1"
end

log.ensure_file options[:gcd_file_with_hole_ice], show_log: options[:create_gcd_log]


# Create photon frames
#
log.section "Create photon frames"

photon_frames_options = {
  dom_index: [1, 1],
  dom_position: [-256.02301025390625, -521.281982421875, 500],
  distance: options[:distance] || 1.0,
  angles: options[:angles] || [90],
  number_of_photons: options[:number_of_photons] || 1e5,
  number_of_runs: options[:number_of_runs] || 2,
  number_of_parallel_runs: options[:number_of_parallel_runs] || 2,
  photons_i3_file: "tmp/photons.i3"
}
options.merge! photon_frames_options

if File.exist?(options[:photons_i3_file]) && (!options[:scattering_factor]) && (!options[:absorption_factor]) && (!options[:distance])
  log.warning "File #{options[:photons_i3_file]} already exists. If you want to recreate it, please specify parameters. See 'run.rb --help'."
else
  log.configuration photon_frames_options

  shell "ruby ../AngularAcceptance/lib/create_qframe_i3_files_with_photons_from_all_angles.rb \\
    --dom-position=#{options[:dom_position].join(',')} \\
    --distance=#{options[:distance]} \\
    #{"--angles=#{options[:angles].join(',')}" if options[:angles]} \\
    #{"--number-of-angles=#{options[:number_of_angles]}" if options[:number_of_angles]} \\
    --gcd-file=#{options[:gcd_file_with_hole_ice]} \\
    --output-file-pattern=tmp/photons.i3 \\
    --number-of-photons-per-angle=#{options[:number_of_photons]} \\
    --number-of-runs=#{options[:number_of_parallel_runs]} \\
    #{"--plane-wave" if options[:plane_wave]} \\
    #{"--plane-wave-size=#{options[:distance]}" if options[:plane_wave]} \\
    --seed=#{options[:seed]}
  "
end
log.ensure_file "tmp/photons.i3"


# Propagate the photons with clsim.
#
log.section "Propagate photons with clsim"
global_propagation_options = {
  hole_ice: :simulation,  # false, :approximation, :simulation
  scattering_factor: options[:scattering_factor] || 0.1,
  absorption_factor: options[:absorption_factor] || 0.1,
  save_photon_paths: options[:save_photon_paths],
  propagation_log_file: "tmp/propagation.log",
  clsim_log_file: "tmp/clsim.log",
  clsim_error_fallback: 'skip' # or: gpu-1-parallel OR cpu OR sleep OR skip
}
options.merge! global_propagation_options
log.configuration global_propagation_options

angle = options[:angles].first
propagation_options = {
  input_file: options[:photons_i3_file],
  seed: options[:seed] + 100 * angle.to_i,
  output_i3_file: options[:photons_i3_file].gsub("tmp/", "tmp/propagated_"),
  output_text_file: options[:photons_i3_file].gsub(".i3", "_dom_hits.txt"),
  output_separate_data_file: "tmp/angle_hits_and_photons_#{angle}.txt",
  output_mean_data_file: "tmp/angle_mean_hits_std_deviation_and_photons_#{angle}.txt",
}

shell "rm #{propagation_options[:output_text_file]}"
shell "rm #{options[:clsim_log_file]}"

shell "ruby ../AngularAcceptance/lib/propagate_photons_and_count_hits.rb \\
  --input-file=#{propagation_options[:input_file]} \\
  --number-of-runs=#{options[:number_of_runs]} \\
  --number-of-parallel-runs=#{options[:number_of_parallel_runs]} \\
  --fallback=#{options[:clsim_error_fallback]} \\
  --hole-ice=#{options[:hole_ice]} \\
  --scattering-factor=#{options[:scattering_factor]} \\
  --absorption-factor=#{options[:absorption_factor]} \\
  #{'--save-photon-paths' if options[:save_photon_paths]} \\
  #{'--cpu' if options[:cpu]} \\
  --seed=#{propagation_options[:seed]} \\
  --ice-model=#{options[:ice_model_file]} \\
  --output-i3-file=#{propagation_options[:output_i3_file]} \\
  --output-text-file=#{propagation_options[:output_text_file]} \\
  --show-log
"
log.ensure_file propagation_options[:output_i3_file]
log.ensure_file propagation_options[:output_text_file]

shell "cat tmp/photons_dom_hits.txt"
