#!/usr/bin/env ruby
# Adds the new premium-UI files to the AstroNumeric Xcode target.
require 'xcodeproj'

project_path = File.expand_path('AstroNumeric.xcodeproj', __dir__)
project = Xcodeproj::Project.open(project_path)
target = project.targets.find { |t| t.name == 'AstroNumeric' } || project.targets.first
main_group = project.main_group.find_subpath('AstroNumeric', true)

shared_group = main_group.find_subpath('SharedComponents', true) || main_group.new_group('SharedComponents')
shared_group.set_path('SharedComponents') if shared_group.path.nil? || shared_group.path.empty?

home_group = main_group.find_subpath('Features/Home', true)
home_group.set_path('Home') if home_group && (home_group.path.nil? || home_group.path.empty?)

shared_files = [
  'DesignTokens.swift',
  'SkeletonView.swift',
  'MysticModeToggle.swift',
  'TimeScrubber.swift',
  'PremiumHeroBlock.swift',
  'TabSelectedDot.swift'
]

shared_files.each do |file|
  rel_path = file
  abs_path = File.expand_path("AstroNumeric/SharedComponents/#{file}", __dir__)
  unless File.exist?(abs_path)
    puts "MISSING ON DISK: #{abs_path}"; next
  end
  if shared_group.files.any? { |f| f.path&.end_with?(file) }
    puts "Already in project: #{file}"; next
  end
  ref = shared_group.new_file(rel_path)
  target.source_build_phase.add_file_reference(ref)
  puts "Added SharedComponents/#{file}"
end

home_files = ['MoonPhaseActivity.swift']
home_files.each do |file|
  abs_path = File.expand_path("AstroNumeric/Features/Home/#{file}", __dir__)
  unless File.exist?(abs_path)
    puts "MISSING ON DISK: #{abs_path}"; next
  end
  if home_group.files.any? { |f| f.path&.end_with?(file) }
    puts "Already in project: #{file}"; next
  end
  ref = home_group.new_file(file)
  target.source_build_phase.add_file_reference(ref)
  puts "Added Features/Home/#{file}"
end

project.save
puts 'Done.'
