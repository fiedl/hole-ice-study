# Data source: https://icecube.wisc.edu/~dima/work/IceCube-ftp/leds/, 2018-01-18

require 'csv'
require_relative 'dom_positions'

# Usage:
#
#     require_relative 'cable_position'
#     CablePosition.find_by(string: 63, dom: 30).angle_from_grid_north_in_degrees
#     # => -134.849
#
class CablePosition

  attr_accessor :string
  attr_accessor :dom

  def self.find_by(attrs)
    cable_position = CablePosition.new
    cable_position.string = attrs[:string]
    cable_position.dom = attrs[:dom]
    return cable_position
  end

  def self.data_file
    # https://icecube.wisc.edu/~dima/work/IceCube-ftp/leds/results.txt
    File.expand_path("~/icecube/cable-data/icecube.wisc.edu/~dima/work/IceCube-ftp/leds/results.txt")
  end

  def self.headers
    %w(string dom tilt_nx tilt_ny tilt_nz tilt_error cable_dir cable_error led_dir)
  end

  def self.data
    CSV.parse(File.read(data_file), col_sep: " ", headers: headers)
  end

  def data
    self.class.data.select { |row| (row["string"].to_i == self.string) && (row["dom"].to_i == self.dom) }
  end

  def angle_from_grid_north_in_degrees
    data.first["cable_dir"].to_f
  end

  def angle_from_grid_north_in_rad
    angle_from_grid_north_in_degrees * 2.0 * Math::PI / 360
  end

  def self.dom_radius
   0.16510
  end

  def dom_position
    DomPosition.find_by(string: string, dom: dom)
  end

  def self.cable_radius
    0.02
  end

  def x
    dom_position.x + Math.sin(angle_from_grid_north_in_rad) * (self.class.dom_radius + self.class.cable_radius)
  end

  def y
    dom_position.y + Math.cos(angle_from_grid_north_in_rad) * (self.class.dom_radius + self.class.cable_radius)
  end

  def z
    dom_position.z
  end

end