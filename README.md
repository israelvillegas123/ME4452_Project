# QArm ROS 2 Local-LLM Simulation

A ROS 2 Humble visual simulation of a 4-DOF Quanser QArm controlled through natural-language prompts. A local Qwen model runs through Ollama; no cloud API key is required.

## System Overview

```text
User prompt
    ↓
Qwen3 via local Ollama server
    ↓
qarm_llm_commander.py
    ↓  publishes /joint_states
robot_state_publisher
    ↓  publishes TF transforms
RViz RobotModel + object markers
```

The project currently provides visual simulation in RViz. It does not yet include physics, collision checking, inverse kinematics, camera perception, or real hardware control.

## Requirements

- Docker Desktop and the ROS 2 Dev Container
- ROS 2 Humble
- Ollama running on the Mac host
- Qwen model:

```bash
ollama pull qwen3:4b-instruct
```

## Build

Run these commands inside the ROS Dev Container terminal:

```bash
cd /workspaces/qarm_ros2_llm
source /opt/ros/humble/setup.bash
colcon build --packages-select qarm_description
source install/setup.bash
```

> ROS commands must run in a terminal beginning with `ros@...`, not the Mac Terminal prompt ending in `%`.

## Launch the Robot

Terminal 1:

```bash
cd /workspaces/qarm_ros2_llm
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch qarm_description rsp.launch.py
```

This starts:

- `robot_state_publisher`
- `qarm_object_world`

## Start the Local LLM Commander

Terminal 2:

```bash
cd /workspaces/qarm_ros2_llm
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run qarm_description qarm_llm_commander.py
```

Example prompt:

```text
Set joint1 to 1.0, joint2 to 0.5, joint3 to -0.7, and joint4 to 0.5 radians.
```

The commander sends the prompt to local Ollama and publishes smooth joint-state motion to RViz.

## Start RViz

Terminal 3:

```bash
source /opt/ros/humble/setup.bash
source /workspaces/qarm_ros2_llm/install/setup.bash
rviz2
```

In RViz:

1. Set **Global Options → Fixed Frame** to `base_link`.
2. Add a **RobotModel** display.
3. Set **Description Source** to `Topic`.
4. Set **Description Topic** to `/robot_description`.
5. Add `/qarm/object_markers` as a **MarkerArray** display.

## Object-World Commands

Terminal 4:

```bash
source /opt/ros/humble/setup.bash
```

Reset the scene:

```bash
ros2 topic pub --once /qarm/object_command std_msgs/msg/String "{data: 'reset_scene'}"
```

Attach the cube visually to the gripper:

```bash
ros2 topic pub --once /qarm/object_command std_msgs/msg/String "{data: 'attach_red_cube'}"
```

Release the cube at the drop zone:

```bash
ros2 topic pub --once /qarm/object_command std_msgs/msg/String "{data: 'release_red_cube'}"
```

## Project Files

```text
src/qarm_description/
├── CMakeLists.txt
├── package.xml
├── qarm_llm_commander.py
├── qarm_object_world.py
├── launch/
│   └── rsp.launch.py
└── urdf/
    └── qarm.urdf
```

## Ollama Connection

The commander uses this endpoint:

```text
http://192.168.65.254:11434/api/generate
```

If Docker assigns the Mac host a different IP address, update `self.ollama_url` in `qarm_llm_commander.py`, rebuild the package, and restart the commander.

## Current Limitations

- Natural language is translated directly to joint-angle targets; it is not task-level motion planning.
- The RViz cube attachment/release behavior is a visual state machine, not a physical grasp simulation.
- The accurate STL mesh model requires the corresponding files under `src/qarm_description/meshes/`.
- Joint limits should be treated as simulation limits; no hardware is connected.