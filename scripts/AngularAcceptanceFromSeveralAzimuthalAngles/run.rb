#!/usr/bin/env ruby
require 'fiedl/log'

# This script simulates a shifted bubble column and creates effective
# angular-acceptance curves for plane waves of photons coming in from
# several azimuthal directions.
#
# See: https://github.com/fiedl/hole-ice-study/issues/117

log.head "Create angular-acceptance scans for several azimuthal directions"
log.info "https://github.com/fiedl/hole-ice-study/issues/117"

bubble_column_configs = [ # all lengths in meters
  {offset: 0.15, radius: 0.075, geometric_scattering_length: 0.10},
  {offset: 0.15, radius: 0.15, geometric_scattering_length: 0.10},
  {offset: 0.15, radius: 0.15, geometric_scattering_length: 0.70},
  {offset: 0.15, radius: 0.30, geometric_scattering_length: 0.70}
]

incoming_azimuthal_angles = [0, 120, 240] # degrees

# https://github.com/fiedl/hole-ice-study/issues/117#issuecomment-430986133
# incoming_polar_angles = [0, 7.5946433685914485, 8.13010235415598, 8.746162262555202, 9.462322208025611, 10.30484646876603, 11.3099324740202, 12.528807709151508, 14.036243467926468, 15.945395900922847, 18.43494882292201, 21.801409486351815, 26.565051177077976, 33.690067525979785, 45.0, 63.43494882292201, 90.0, 116.56505117707799, 135.0, 146.30993247402023, 153.43494882292202, 158.19859051364818, 161.56505117707798, 164.05460409907715, 165.96375653207355, 167.47119229084848, 168.6900675259798, 169.69515353123398, 170.53767779197437, 171.2538377374448, 171.86989764584402, 172.40535663140855, 180]
incoming_polar_angles = [0, 8, 9, 10, 11, 13, 16, 180, 22, 27, 34, 45, 63, 90, 117, 135, 146, 153, 158, 162, 164, 166, 167, 169, 171, 172, 180]

dom_position = [-256.02301025390625, -521.281982421875, 500.0]

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

# Cluster configuration
#
log.section "Cluster configuration?"
number_of_jobs = bubble_column_configs.count * incoming_azimuthal_angles.count
current_cluster_node_index = ENV['SGE_TASK_ID']
if current_cluster_node_index
  log.info "This is cluster node #{current_cluster_node_index} of #{number_of_jobs}."
  number_of_photons = 1e7
  cpu = false
  save_photon_paths = false
else
  log.info "Running locally on the CPU in order to produce animations."
  number_of_photons = 10
  cpu = true
  save_photon_paths = true
end

# Loop over configurations and run the simulation
#
parameter_set_index = 0
bubble_column_configs.each do |config|
  incoming_azimuthal_angles.each do |azimuthal_angle|
    parameter_set_index += 1

    need_to_perform_this_job = ((not current_cluster_node_index) or
        (current_cluster_node_index.to_i == parameter_set_index))

    if need_to_perform_this_job

      log.section "Parameters"
      log.configuration config

      offset = config[:offset]
      radius = config[:radius]
      sca = config[:geometric_scattering_length]
      abs = 100.0
      dst = 3.0
      plane_wave_size = dst

      hole_ice_position = [
        dom_position[0] - offset * Math.cos(azimuthal_angle * Math::PI / 180),
        dom_position[1] - offset * Math.sin(azimuthal_angle * Math::PI / 180)
      ]

      results_directory = "results/offset_#{offset * 100}cm_radius_#{radius * 100}cm_sca_#{sca * 100}cm_azi#{azimuthal_angle}"

      if File.exists? results_directory
        log.warning "Skipping already existing run #{results_directory}."
      else
        log.section "Run simulation"
        shell "mkdir -p #{results_directory} tmp"

        #          --ice-model=../AngularAcceptanceFromSeveralAzimuthalAngles/ice/perfect_bulk_ice \\

        shell "cd ../AngularAcceptance && ./run.rb \\
          --cluster \\
          --hole-ice-scattering-length=#{sca} \\
          --hole-ice-absorption-length=#{abs} \\
          --hole-ice-radius=#{radius} \\
          --distance=#{dst} \\
          --plane-wave \\
          --plane-wave-size=#{plane_wave_size} \\
          --number-of-photons=#{number_of_photons} \\
          --number-of-runs=1 \\
          --number-of-parallel-runs=1 \\
          --angles=#{incoming_polar_angles.join(',')} \\
          --dom-position=#{dom_position.join(',')} \\
          --hole-ice-position=#{hole_ice_position.join(',')} \\
          #{'--cpu' if cpu} \\
          #{'--save-photon-paths' if save_photon_paths} \\
        "

        shell "mv ../AngularAcceptance/results/current/* #{results_directory}/"
      end

    end

  end
end