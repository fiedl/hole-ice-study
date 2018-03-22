#!/usr/bin/env ruby
require 'fiedl/log'
require 'optparse'
require 'pp'
require 'pawgen'

options = {}
OptionParser.new do |opts|
  opts.banner = "Usage: bundle exec ruby run.rb [options]"

  opts.on "--hole-ice", "Add hole ice to the simulation" do
    options[:hole_ice] = true
  end
  opts.on "--cable", "Add a cable shadow to the simulation" do
    options[:cable] = true
  end
  opts.on "--cylinder-shift=METRES", "Shift the hole-ice cylinder x position by this value in metres to study asymmetries." do |metres|
    options[:cylinder_shift] = metres
  end
  opts.on "--number-of-events=N", "Number of separate q frames with muon events" do |number|
    options[:number_of_events] = (number || 1).to_i
  end
end.parse!

log.head "Muon Test Simulation"
log.info "See: https://github.com/fiedl/hole-ice-study/issues/44"


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
shell "rm -r tmp/*"
shell "mkdir -p tmp"


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
hole_ice_cylinder_positions = []
hole_ice_cylinder_radii = []
if options[:hole_ice]
  hole_ice_cylinder_positions << [-256.02301025390625 + options[:cylinder_shift].to_f, -521.281982421875, 0]
  hole_ice_cylinder_radii << 0.08
end
if options[:cable]
  hole_ice_cylinder_positions << [-256.02301025390625 + dom_radius + 0.02, -521.281982421875, 500.0]
  hole_ice_cylinder_radii << 0.02
end
detector_geometry_options = {
  gcd_file: "$I3_TESTDATA/sim/GeoCalibDetectorStatus_IC86.55380_corrected.i3.gz",
  ice_model_file: "$I3_SRC/clsim/resources/ice/spice_mie",
  seed: 123456,
  hole_ice_cylinder_positions: hole_ice_cylinder_positions,
  hole_ice_cylinder_radii: hole_ice_cylinder_radii
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

log.ensure_file options[:gcd_file_with_hole_ice], show_log: options[:create_gcd_log]


# Create muon track
#
log.section "Create muon track q frame"
options.merge!({
  i3_file_with_muon: "tmp/muon.i3",
  generate_muon_log: "tmp/generateTestMuons.log"
})
shell "python #{__dir__}/lib/generateTestMuons.py \\
  --gcd=#{options[:gcd_file_with_hole_ice]} \\
  --outfile=#{options[:i3_file_with_muon]} \\
  --numevents=#{options[:number_of_events]} \\
  > #{options[:generate_muon_log]} 2>&1"
log.ensure_file options[:i3_file_with_muon], show_log: options[:generate_muon_log]
