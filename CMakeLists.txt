cmake_minimum_required(VERSION 2.8.3)
project(robocup_simopl_handyman)

add_definitions(-std=c++14)

find_package(catkin REQUIRED COMPONENTS
  roscpp
  rospy
  std_msgs
  geometry_msgs
  trajectory_msgs
  tf
  pcl_conversions
  pcl_ros
  message_generation
  sobit_navigation_library
)

add_message_files(
  FILES
  robocup_simopl_handymanCommand.msg
)

generate_messages(
  DEPENDENCIES
  std_msgs
)
catkin_package()

include_directories(include ${catkin_INCLUDE_DIRS})
link_directories(/usr/local/lib)

add_executable(other_obj_broadcaster src/other_obj_broadcaster.cpp)
target_link_libraries(other_obj_broadcaster ${catkin_LIBRARIES})

add_executable(destination_broadcaster src/destination_broadcaster.cpp)
target_link_libraries(destination_broadcaster ${catkin_LIBRARIES})
