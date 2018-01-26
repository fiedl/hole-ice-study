#!/usr/bin/env ruby
#
# We want to shoot photons onto a DOM from different angles.
#
# This script loops through the angles and, for each angle, generates
# an i3 file with a qframe containing several photons.

require 'optparse'
require 'fiedl/log'

options = {}
OptionParser.new do |opts|
  opts.banner = "Usage: ./create_qframe_i3_files_with_photons_from_all_angles.rb [options]"

  opts.on "--dom-position=DOM_POSITION", "Move around given position, e.g. -256.02301025390625,-521.281982421875,500" do |dom_position|
    options[:dom_position] = dom_position.split(",").map(&:to_f)
  end
  opts.on "--shoot-from-distance=DISTANCE", "--distance=DISTANCE", "Photons are created in that distance from the DOM." do |distance|
    options[:distance] = distance.to_f
  end
  opts.on "--angles=ANGLES", "Angles eta to scan, e.g. 0,45,90,180." do |angles|
    options[:angles] = angles.split(",").map(&:to_i)
  end
  opts.on "--number-of-angles=NUMBER", "e.g. 360. This determines the angular resolution." do |number_of_angles|
    options[:number_of_angles] = number_of_angles.to_i
  end
  opts.on "--gcd-file=FILENAME", "If given, this gcd file is written at the beginning of the output i3 file." do |filename|
    options[:gcd_file] = filename
  end
  opts.on "--output-file-pattern=PATTERN", "e.g. 'tmp/photons_from_angle_ANGLE.i3'. 'ANGLE' is replaced with the actual angle." do |output_file_pattern|
    options[:output_file_pattern] = output_file_pattern
  end
  opts.on "--number-of-photons-per-angle=NUMBER" do |number|
    options[:number_of_photons_per_angle] = number.to_i
  end
  opts.on "--number-of-runs=NUMBER", "Repeat the same scenario NUMBER times, i.e. create NUMBER q frames." do |number|
    options[:number_of_runs] = number.to_i
  end

end.parse!

options[:number_of_runs] ||= 1

log.head "Creating photons from all angles"
log.info options

angular_range = options[:angles] || (0..359).step(360 / options[:number_of_angles])
log.section "Looping through #{angular_range.to_s}"

require 'matrix'
angular_range.each do |angle|
  angle_str = angle.to_s.rjust(3, "0")
  filename = options[:output_file_pattern].gsub("ANGLE", angle_str)
  log.p "angle #{angle_str.blue} ... "

  # dom position
  dom_position = Vector[*options[:dom_position]]

  # direction from dom to photons
  pi = Math::PI
  angle_rad = angle * pi / 180
  distance = options[:distance]
  direction_to_dom = Vector[Math.sin(angle_rad) * distance, 0, -Math.cos(angle_rad) * distance]

  # photon position
  photon_position = dom_position + direction_to_dom
  #log.variable photon_position, :photon_position

  # photon direction
  photon_direction = - direction_to_dom.normalize
  #log.variable photon_direction, :photon_direction
  log.info "photons from #{photon_direction.to_s.red}"

  # write photons into file
  `python #{__dir__}/create_qframe_i3_file_with_photons_from_angle.py \
    --photon-position=#{photon_position.to_a.join(",")} \
    --photon-direction=#{photon_direction.to_a.join(",")} \
    --number-of-photons=#{options[:number_of_photons_per_angle]} \
    --gcd-file=#{options[:gcd_file]} \
    --output-file=#{filename} \
    --number-of-runs=#{options[:number_of_runs]} \
    > tmp/create_qframes.log 2>&1
  `

  log.ensure_file filename, show_log: "tmp/create_qframes.log"
end

log.success "Finished."
