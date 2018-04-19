#!/usr/bin/env ruby
require 'fiedl/log'
require 'json'
#require 'yaml'

log.head "Convert options.txt to options.json"
log.info "This script converts the ruby options files (`options.txt`) within"
log.info "the given directory to json files (`options.json`) that can be"
log.info "read by python."

log.section "Source"

base_path = File.expand_path ARGV[0]
log.info "Base path: #{base_path}"

options_files = Dir.glob("#{base_path}/**/options.txt")
log.info "Source files:"
for file in options_files
  log.info "- #{file}"
end

log.section "Converting files"
for txt_file in options_files
  ruby_hash = eval(File.read(txt_file))

  json = ruby_hash.to_json
  json_file = txt_file.gsub(".txt", ".json")
  File.open(json_file, "w") { |f| f.write json }
  log.ensure_file json_file

  #yaml = JSON.parse(json).to_yaml
  #yaml_file = txt_file.gsub(".txt", ".yaml")
  #File.open(yaml_file, "w") { |f| f.write yaml }
  #log.ensure_file yaml_file
end

log.success "Done."

