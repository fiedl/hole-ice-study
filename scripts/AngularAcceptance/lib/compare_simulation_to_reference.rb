#!/usr/bin/env ruby
require 'fiedl/log'
require 'optparse'
require 'pp'

options = {}
OptionParser.new do |opts|
  opts.banner = "Compare simulation data to reference plot. Usage: lib/compare_simulation_to_reference.rb [options]"

  opts.on "--input-files=PATTERN_LIST", "e.g. tmp/angle_hits_deviation_and_photons.txt,results/**/data/angle_hits_deviation_and_photons.txt" do |pattern|
    options[:input_files] = pattern.split(",").collect { |path| Dir.glob(path) }.flatten
  end
  opts.on "--data-labels=LABELS", "e.g. simulation with distance 0.5m, distance 1.0m" do |labels|
    options[:data_labels] = labels.split(",")
  end
  opts.on "--data-label=LABEL" do |label|
    options[:data_labels] = [label]
  end
  opts.on "--output-plot-file=FILE", "e.g. tmp/compare_to_reference.png" do |file|
    options[:output_plot_file] = file
  end
  opts.on "--gnuplot-log=FILE", "e.g. tmp/chi_square_gnuplot.log" do |file|
    options[:gnuplot_log] = file
  end
  opts.on "--results-file=FILE", "e.g. tmp/chi_square_results.txt" do |file|
    options[:results_file] = file
  end
  opts.on "--use-hole-ice" do
    options[:use_hole_ice] = true
  end
end.parse!

options[:input_files] ||= ["tmp/angle_hits_deviation_and_photons.txt"]
options[:output_plot_file] ||= "tmp/compare_to_reference.png"
options[:gnuplot_log] ||= "tmp/chi_square_gnuplot.log"
options[:results_file] ||= "tmp/chi_square_results.txt"
options[:use_hole_ice] ||= false

log.head "Compare simulation data to reference plot"
log.info "Therefore, calculate reduced chi square of simulation data"
log.info "and reference curve regarding the DOM angular acceptance"
log.info "distribution."
log.configuration options

if options[:use_hole_ice]
  polynomial_parameters = "
  a = 0.32813; b = 0.63899; c = 0.20049; d =-1.2250; e =-0.14470; f = 4.1695;
  g = 0.76898; h =-5.8690; i =-2.0939; j = 2.3834; k = 1.0435;
  "
else
  polynomial_parameters = "
  a = 0.26266; b = 0.47659; c = 0.15480; d =-0.14588; e = 0.17316; f = 1.3070;
  g = 0.44441; h =-2.3538; i =-1.3564; j = 1.2098; k = 0.81569;
  "
end

shell "mkdir -p tmp"
shell "rm #{options[:gnuplot_log]}"

results = {}
options[:input_files].each do |input_file|

  log.section "Perform calculations for #{input_file}"
  results[input_file] = {}

  result_id = input_file.split("/")[-3]
  results[input_file][:id] = result_id

  # greek letter with utf-8 encoding:
  # http://stackoverflow.com/a/24653552/2066546

  gnuplot_script = "
    set term png;
    set encoding utf8;
    set title 'Angular Acceptance';
    set xlabel 'cos(η)';
    set ylabel 'relative sensitivity';
    set logscale y;

    #{polynomial_parameters}

    f(x) = a + b*x + c*x**2 + d*x**3 + e*x**4 + f*x**5
      + g*x**6 + h*x**7 + i*x**8 + j*x**9 + k*x**10;

    set output 'tmp/temp.png';

    set datafile missing '0.0 0.0';

    N = 0;
    plot '#{input_file}'
      using 1:(N = N + 1);
    print 'N = ', N;

    nu = N - 11;

    g(x) = f(x) / scale;

    set datafile missing '0.0 0.0';

    fit [-1:1] g(x) '#{input_file}'
      using (cos(\\$1 / 360 * 2 * pi)):(\\$2 / \\$4):(\\$3 / \\$4)
      yerr
      via scale;

    print 'scale = ', scale;
    print 'chi^2_nu = ', FIT_STDFIT**2;
    print 'nu = ', nu;
  "

  shell "gnuplot -e \"#{gnuplot_script}\" \\
    >> #{options[:gnuplot_log]} \\
    2>&1"

  def extract_result(variable_name, options, results, input_file)
    variable = `grep '#{variable_name} =' #{options[:gnuplot_log]}`
      .split("\n").last
      .split(" = ").last
    results[input_file][variable_name] = variable
  end

  extract_result 'scale', options, results, input_file
  extract_result 'N', options, results, input_file
  extract_result 'nu', options, results, input_file
  extract_result 'chi^2_nu', options, results, input_file
end

log.section "Results"
log.configuration results
File.open(options[:results_file], 'w') { |file| PP.pp(results, file) }
log.ensure_file options[:results_file]




log.section "Plot all into one plot"
label_counter = 0
gnuplot_script = "
  set term png;
  set encoding utf8;
  set title 'Angular Acceptance';
  set xlabel 'cos(η)';
  set ylabel 'relative sensitivity';
  set logscale y;
  set key right bottom;

  #{polynomial_parameters}

  f(x) = a + b*x + c*x**2 + d*x**3 + e*x**4 + f*x**5
    + g*x**6 + h*x**7 + i*x**8 + j*x**9 + k*x**10;

  set xrange [-1:1];

  plot
" + options[:input_files].collect { |input_file|
    id = results[input_file][:id]
    label = options[:data_labels][label_counter] if options[:data_labels]
    label ||= id
    label_counter += 1
    scale = results[input_file]['scale']
    chisq_nu = results[input_file]['chi^2_nu'].to_f.round(4)
"
    '#{input_file}'
    using (cos(\\$1 / 360 * 2 * pi)):(\\$2 / \\$4 * #{scale}):(\\$3 / \\$4 * #{scale}):(\\$1 <= 180 ? 1 : 2)
    with errorbars linecolor variable
    title '#{label}, χ^2_ν=#{chisq_nu}',
"
}.join("\n") + "
    f(x) title 'Reference Plot' lt rgb 'red' lw 1;
"

shell "gnuplot -e \"#{gnuplot_script}\" > #{options[:output_plot_file]}"

