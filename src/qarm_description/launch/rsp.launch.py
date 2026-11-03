import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # Pinpoint the URDF path we just repositioned
    urdf_file = os.path.join(
        get_package_share_directory('qarm_description'),
        'urdf',
        'qarm.urdf'
    )
    
    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    return LaunchDescription([
        # Main node publishing the physical layout of the QArm
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_desc}]
        ),
        # add object-world node 
        Node(
            package='qarm_description', 
            executable='qarm_object_world.py', 
            name='qarm_object_world', 
            output='screen'
        )

        # # Helper node giving us manual sliding GUI knobs to test moving joints
        # Node(
        #     package='joint_state_publisher_gui',
        #     executable='joint_state_publisher_gui',
        #     output='screen', 
        #     parameters=[{'robot_description': robot_desc}]
        # )
    ])
