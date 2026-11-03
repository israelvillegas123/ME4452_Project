cmake_minimum_required(VERSION 3.8)
project(qarm_description)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY launch urdf
  DESTINATION share/${PROJECT_NAME}
)

install(
    PROGRAMS 
        qarm_llm_commander.py
        qarm_object_world.py
    DESTINATION lib/${PROJECT_NAME}
)

ament_package()