#!/usr/bin/env ruby
require 'fiedl/log'
require 'optparse'

options = {}
OptionParser.new do |opts|
  opts.banner = "Create histograms for the number of hits for all angles. Usage: lib/create_histograms_for_hits.rb [options]"

  opts.on "--input-files=PATTERN", "e.g. tmp/angle_hits_and_photons_*.txt" do |pattern|
    options[:input_files] = pattern
  end
  opts.on "--input-columns=COLUMNS", "e.g. angle,hits,photons" do |columns|
    options[:input_columns] = columns
  end
  opts.on "--output-file-pattern=PATTERN", "e.g. tmp/hits_histogram_ANGLE.png" do |pattern|
    options[:output_file_pattern] = pattern
  end
  opts.on "--min-bin=NUMBER" do |number|
    options[:min_bin] = number.to_i
  end
  opts.on "--max-bin=NUMBER" do |number|
    options[:max_bin] = number.to_i
  end
end.parse!

options[:input_files] ||= "tmp/angle_hits_and_photons_*.txt"
options[:input_columns] ||= "angle,hits,photons"
options[:output_file_pattern] ||= "tmp/hits_histogram_ANGLE.png"
options[:min_bin] ||= 0
options[:max_bin] ||= 200

log.head "Create histograms"
log.info "In oder to check plausibility, these histograms visualize the distribution"
log.info "of the number of hits for each angle when repeating the simulation for a"
log.info "given angle several times."
log.configuration options

options[:input_files] = Dir.glob(options[:input_files])

options[:input_files].each do |input_file|
  # http://stackoverflow.com/a/694892/2066546
  angle = input_file.split("/").last[/\d+/]

  output_file = options[:output_file_pattern].gsub("ANGLE", angle)

  root_script = "
    #include \"Riostream.h\"
    ifstream in;
    in.open(\"#{input_file}\");

    TH1F *h1 = new TH1F(\"histogram\", \"DOM sensitivity at #eta = #{angle} deg\", 100, #{options[:min_bin]}, #{options[:max_bin]});
    h1->GetXaxis()->SetTitle(\"Number of DOM hits\");

    Float_t #{options[:input_columns]};

    while (in.good()) {
      in >> #{options[:input_columns].gsub(',', ' >> ')};
      h1->Fill(hits);
    }

    in.close();

    TCanvas *c = new TCanvas;
    h1.Draw();
    TImage *img = TImage::Create();
    img->FromPad(c);
    img->WriteImage(\"#{output_file}\");
  "

  shell "echo '#{root_script}' | root -b -l"
  log.ensure_file output_file
end

