all: run
	
Gemfile.lock:
	bundle install

run: Gemfile.lock
	bundle exec ruby run.rb

help: Gemfile.lock
	bundle exec ruby run.rb --help
