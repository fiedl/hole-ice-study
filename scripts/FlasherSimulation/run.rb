#!/usr/bin/env ruby
require 'fiedl/log'
require 'optparse'
require 'pp'
require 'pawgen'
require 'json'

options = {}
OptionParser.new do |opts|
  opts.banner = "Usage: bundle exec ruby run.rb [options]"

  opts.on "--hole-ice=METHOD", "simulation or approximation" do |method|
    options[:hole_ice] = method
  end
  opts.on "--no-hole-ice", "Run without hole-ice code" do
    options[:hole_ice] = false
  end

  opts.on "--width=WIDTH", "Flahser pulse width, min = 0, max = 127" do |width|
    options[:width] = width.to_i
  end
  opts.on "--brightness=BRIGHTNESS", "Flasher pulse brightness, min = 0, max = 127" do |brightness|
    options[:brightness] = brightness.to_i
  end
  opts.on "--thinning-factor=FACTOR", "between 0.0 and 1.0. See https://github.com/fiedl/hole-ice-study/issues/85" do |factor|
    options[:thinning_factor] = factor.to_f
  end
  opts.on "--effective-scattering-length=METRES" do |esca|
    options[:effective_scattering_length] = esca.to_f
  end
  opts.on "--absorption-length=METRES" do |abs|
    options[:absorption_length] = abs.to_f
  end
  opts.on "--hole-ice-radius-in-dom-radii=R" do |r|
    options[:hole_ice_radius_in_dom_radii] = r.to_f
  end

  opts.on "--cable", "Simulate cable shadow for the sending DOM" do
    options[:cable] = true
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

# Place hole-ice cylinders around these sending and receiving strings.
# See: https://github.com/fiedl/hole-ice-study/issues/59
#
strings_with_hole_ice = [63] + [62, 54, 55, 64, 71, 70] + [61, 53, 44, 45, 46, 56, 65, 72, 78, 77, 76, 69]
# strings_with_hole_ice = []
require_relative '../lib/string_positions'

# bubble-column cylinders
# defaults from Martin's best estimates
bubble_column_cylinder_positions = strings_with_hole_ice.collect { |string|
  string_position = StringPosition.for_string(string)
  [string_position[:x], string_position[:y], 0]
}
bubble_column_cylinder_radii = [
  (options[:hole_ice_radius_in_dom_radii] || 0.5) * dom_radius
] * strings_with_hole_ice.count
bubble_column_scattering_lengths = [
  (options[:effective_scattering_length] || 0.05) * (1 - 0.94)
] * strings_with_hole_ice.count
bubble_column_absorption_lengths = [
  (options[:absorption_length] || 100.0)
] * strings_with_hole_ice.count

# Simulate cable shadows using absorbing cylinders
# https://github.com/fiedl/hole-ice-study/issues/60
#
strings_with_cables = if options[:cables]
  strings_with_hole_ice
else
  []
end

# require_relative '../lib/cable_positions'
# doms = (1..60)
# cable_positions = strings_with_cables.collect { |string|
#   doms.collect { |dom|
#     cable_position = CablePosition.find_by(string: string, dom: dom)
#     [cable_position.x, cable_position.y, cable_position.z]
#   }
# }.flatten(1)
# cable_radii = [0.02] * (strings_with_cables.count * doms.count)
# cable_scattering_lengths = [100.0] * (strings_with_cables.count * doms.count)
# cable_absorption_lengths = [0.0] * (strings_with_cables.count * doms.count)


# Simulate a shadowing cable for the sending DOM by hand:
# https://github.com/fiedl/hole-ice-study/issues/97

if options[:cable]
  strings_with_cables = [63]
end

require_relative '../lib/cable_positions'
doms = [30]
# cable_positions = strings_with_cables.collect { |string|
#   doms.collect { |dom|
#     cable_position = CablePosition.find_by(string: string, dom: dom)
#     [cable_position.x, cable_position.y, cable_position.z]
#   }
# }.flatten(1)

# https://github.com/fiedl/hole-ice-study/issues/97#issuecomment-407362741
cable_positions = [[-66.83122690023184, 276.78947335840394, 3.119999885559082]]

cable_radii = [0.02] * (strings_with_cables.count * doms.count)
cable_scattering_lengths = [100.0] * (strings_with_cables.count * doms.count)
cable_absorption_lengths = [0.0] * (strings_with_cables.count * doms.count)

detector_geometry_options = {
  gcd_file: "$I3_TESTDATA/sim/GeoCalibDetectorStatus_IC86.55380_corrected.i3.gz",
  ice_model_file: "$I3_SRC/clsim/resources/ice/spice_mie",
  seed: 123456,
  hole_ice_cylinder_positions: bubble_column_cylinder_positions + cable_positions,
  hole_ice_cylinder_radii: bubble_column_cylinder_radii + cable_radii,
  cylinder_scattering_lengths: bubble_column_scattering_lengths + cable_scattering_lengths,
  cylinder_absorption_lengths: bubble_column_absorption_lengths + cable_absorption_lengths
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
  shell "python #{__dir__}/../lib/create_gcd_file_with_hole_ice.py \\
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
  string_number: 63,
  dom_number: 30,
  i3_file: "tmp/flasher.i3",
  brightness: options[:brightness] || 127,
  width: options[:width] || 127,
  mask: "111111111111" # https://wiki.icecube.wisc.edu/index.php/Flasher_LED_mask
}
log.configuration flasher_options
options.merge!({flasher: flasher_options})
File.open("tmp/options.txt", 'w') { |file| PP.pp(options, file) }

if File.exists? options[:flasher][:i3_file]
  log.warning "Skipping creation of already existing file #{options[:flasher][:i3_file]}."
else
  shell "python #{__dir__}/../lib/create_flasher_pulse.py \\
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

  shell "python #{__dir__}/../lib/propagate_photons_with_clsim.py \\
    --ice-model=#{options[:ice_model_file]} \\
    --seed=#{options[:seed]} \\
    --output-i3-file=#{options[:output_i3_file]} \\
    --use-gpus=#{options[:cpu] ? 'False' : 'True'} \\
    --thinning-factor=#{options[:thinning_factor] || 1.0} \\
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
  numbers_of_hits_file: "tmp/hits.txt"
}
options.merge! read_out_options
log.configuration read_out_options
File.open("tmp/options.txt", 'w') { |file| PP.pp(options, file) }

shell "python #{__dir__}/../lib/read_out_photon_hits.py \\
  --i3-file=#{options[:output_i3_file]} \\
  --outfile=#{options[:numbers_of_hits_file]} \\
"
log.ensure_file options[:numbers_of_hits_file]


# Log finish time.
#
options.merge!({
  finished_at: Time.now.to_s
})
File.open("tmp/options.txt", 'w') { |file| PP.pp(options, file) }


# Export json options for processing those with python later.
#
File.open("tmp/options.json", 'w') { |file| file.write options.to_json }


# Export results.
#
log.section "Exporting results"
shell "mkdir -p results"
results_folder = "results/#{options[:run_id]}"
shell "mv tmp #{results_folder}"
log.ensure_file results_folder

log.success "Finished."

