#!/usr/bin/env ruby
require 'fiedl/log'
require 'optparse'
require 'pp'
require 'pawgen'

options = {}
OptionParser.new do |opts|
  opts.banner = "Usage: bundle exec ruby run.rb [options]"

  opts.on "--hole-ice=METHOD", "simulation or approximation" do |method|
    options[:hole_ice] = method
  end
  opts.on "--no-hole-ice", "Run without hole-ice code" do
    options[:hole_ice] = false
  end
end.parse!

log.head "Flasher simulation"

# Check requirements
#
log.section "Check requirements"
(log.error 'Environment variable $I3_PORTS is not set, which is needed for clsim working with geant4.'; raise('Requirements not met.')) unless ENV['I3_PORTS']
(log.error 'Environment variable $I3_TESTDATA is not set.'; raise('Requirements not met.')) unless ENV['I3_TESTDATA']
(log.error "$I3_TESTDATA (#{ENV['I3_TESTDATA']}) does not exist in the file system."; raise('Requirements not met.')) unless File.exists?(ENV['I3_TESTDATA'])
(log.error "IceSim not loaded. Please navigate to your icecube-simulation build and run \`./env-shell.sh\`. If you've followed the [install guide](...), just run \`ice-env\`."; raise('Requirements not met.')) unless ENV['I3_SHELL']
log.success "OK."


# Run id
log.section "Run id"
pwgen = PawGen.new.set_length!(8).exclude_ambiguous!
run_id_options = {
  run_id: "Run-#{Time.now.year}-#{pwgen.anglophonemic}",
  started_at: Time.now.to_s
}
log.configuration run_id_options
options.merge! run_id_options
shell "mkdir -p tmp"
File.open("tmp/options.txt", 'w') { |file| PP.pp(options, file) }
log.ensure_file "tmp/options.txt"

# Detector geometry
#
log.section "Detector geometry"
dom_radius = 0.16510

# DOM Positions: https://wiki.icecube.wisc.edu/index.php/Geometry_releases
#
string_62_position = [-189.98, 257.42]
string_63_position = [ -66.70, 276.92]

detector_geometry_options = {
  gcd_file: "$I3_TESTDATA/sim/GeoCalibDetectorStatus_IC86.55380_corrected.i3.gz",
  ice_model_file: "$I3_SRC/clsim/resources/ice/spice_mie",
  seed: 123456,
  hole_ice_cylinder_positions: [
    string_62_position + [0],
    string_63_position + [0]
  ],

  # Hole-ice configuration from Martin's best estimates
  hole_ice_cylinder_radii: [
    0.5 * dom_radius, 0.5 * dom_radius
  ],
  cylinder_scattering_lengths: [
    0.05 * (1 - 0.94), 0.05 * (1 - 0.94)
  ],
  cylinder_absorption_lengths: [
    100.0, 100.0
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
File.open("tmp/options.txt", 'w') { |file| PP.pp(options, file) }

if File.exist? options[:gcd_file_with_hole_ice]
  log.warning "File #{options[:gcd_file_with_hole_ice]} exists. Please remove it if you want it to be recreated."
else
  shell "python #{__dir__}/../AngularAcceptance/lib/create_gcd_file_with_hole_ice.py \\
    --input-gcd-file=#{options[:gcd_file]} \\
    --output-gcd-file=#{options[:gcd_file_with_hole_ice]} \\
    " + options[:hole_ice_cylinder_positions].enum_for(:each_with_index).collect { |pos, index|
      "--cylinder-x=#{options[:hole_ice_cylinder_positions][index][0]} \\
      --cylinder-y=#{options[:hole_ice_cylinder_positions][index][1]} \\
      --cylinder-z=#{options[:hole_ice_cylinder_positions][index][2]} \\
      --cylinder-radius=#{options[:hole_ice_cylinder_radii][index]} \\
      --cylinder-scattering-length=#{options[:cylinder_scattering_lengths][index]} \\
      --cylinder-absorption-length=#{options[:cylinder_absorption_lengths][index]} \\
      "
    }.join + "> #{options[:create_gcd_log]} 2>&1"
end
log.ensure_file options[:gcd_file_with_hole_ice], show_log: options[:create_gcd_log]

# Create simulated flashes
#
log.section "Create simulated flashes"
flasher_options = {
  string_number: 62,
  dom_number: 30,
  i3_file: "tmp/flasher.i3",
  brightness: 127,
  width: 127,
  mask: "111111111111" # https://wiki.icecube.wisc.edu/index.php/Flasher_LED_mask
}
log.configuration flasher_options
options.merge!({flasher: flasher_options})
File.open("tmp/options.txt", 'w') { |file| PP.pp(options, file) }

if File.exists? options[:flasher][:i3_file]
  log.warning "Skipping creation of already existing file #{options[:flasher][:i3_file]}."
else
  shell "python #{__dir__}/../AngularAcceptance/lib/create_flasher_pulse.py \\
    --gcd=#{options[:gcd_file_with_hole_ice]} \\
    --string=#{flasher_options[:string_number]} \\
    --dom=#{flasher_options[:dom_number]} \\
    --brightness=#{flasher_options[:brightness]} \\
    --width=#{flasher_options[:width]} \\
    --mask=0b#{flasher_options[:mask]} \\
    --outfile=#{flasher_options[:i3_file]} \\
  "
end
log.ensure_file options[:flasher][:i3_file]


# Propagate the photons with clsim.
#
log.section "Propagate photons with clsim"
propagation_options = {
  hole_ice: (options[:hole_ice].nil? ? :simulation : options[:hole_ice]),
  save_photon_paths: false,
  cpu: false,
  input_file: options[:flasher][:i3_file],
  output_i3_file: "tmp/propagated_photons.i3",
  propagation_log_file: "tmp/propagation.log",
  clsim_log_file: "tmp/clsim.log",
}
options.merge! propagation_options
log.configuration propagation_options
File.open("tmp/options.txt", 'w') { |file| PP.pp(options, file) }

if File.exists? options[:output_i3_file]
  log.warning "Skipping creation of already existing file #{options[:output_i3_file]}."
else

  shell "rm #{options[:clsim_log_file]}"

  shell "python #{__dir__}/../AngularAcceptance/lib/propagate_photons_with_clsim.py \\
    --ice-model=#{options[:ice_model_file]} \\
    --seed=#{options[:seed]} \\
    --output-i3-file=#{options[:output_i3_file]} \\
    --use-gpus=#{options[:cpu] ? 'False' : 'True'} \\
    --save-photon-paths=#{options[:save_photon_paths] ? 'True' : 'False'} \\
    --number-of-parallel-runs=1 \\
    --use-hole-ice-approximation=#{(options[:hole_ice].to_s == 'approximation') ? 'True' : 'False'} \\
    --use-hole-ice-simulation=#{(options[:hole_ice].to_s == 'simulation') ? 'True' : 'False'} \\
    --use-flasher-info-vect=True \\
    #{options[:input_file]} \\
    2>&1 | tee #{options[:clsim_log_file]}
  "
end
log.ensure_file propagation_options[:output_i3_file]


# Read out numbers of hits.
#
log.section "Read out numbers of hits"
read_out_options = {
  receiving_string: 63,
  numbers_of_hits_file: "tmp/hits.txt"
}
options.merge! read_out_options
log.configuration read_out_options
File.open("tmp/options.txt", 'w') { |file| PP.pp(options, file) }

shell "python #{__dir__}/../AngularAcceptance/lib/read_out_photon_hits.py \\
  --string=#{options[:receiving_string]} \\
  --i3-file=#{options[:output_i3_file]} \\
  --outfile=#{options[:numbers_of_hits_file]} \\
"
log.ensure_file options[:numbers_of_hits_file]


# Export results.
#
log.section "Exporting results"
shell "mkdir -p results"
results_folder = "results/#{options[:run_id]}"
shell "mv tmp #{results_folder}"
log.ensure_file results_folder

log.success "Finished."

