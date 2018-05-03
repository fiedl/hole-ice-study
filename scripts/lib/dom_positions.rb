require 'csv'

class DomPosition

  attr_accessor :string
  attr_accessor :dom

  def self.find_by(attrs)
    position = DomPosition.new
    position.string = attrs[:string]
    position.dom = attrs[:dom]
    return position
  end

  def self.data_file
    # https://wiki.icecube.wisc.edu/images/2/22/Icecube_geometry.20110414.complete.txt
    File.expand_path("~/icecube/dom_positions.txt")
  end

  def self.headers
    %w(string dom x y z)
  end

  def self.data
    CSV.parse(File.read(data_file), col_sep: " ", headers: headers)
  end

  def data
    self.class.data.select { |row| (row["string"].to_i == self.string) && (row["dom"].to_i == self.dom) }
  end

  def x
    data.first["x"].to_f
  end

  def y
    data.first["y"].to_f
  end

  def z
    data.first["z"].to_f
  end

end
