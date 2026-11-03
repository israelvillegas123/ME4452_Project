#!/usr/bin/env python3
"""RViz-only object world for a QArm pick-and-place prototype."""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from visualization_msgs.msg import Marker, MarkerArray


class QArmObjectWorld(Node):
    def __init__(self):
        super().__init__('qarm_object_world')

        self.marker_publisher = self.create_publisher(
            MarkerArray,
            '/qarm/object_markers',
            10
        )

        self.command_subscriber = self.create_subscription(
            String,
            '/qarm/object_command',
            self.object_command_callback,
            10
        )

        self.cube_state = 'on_table'
        self.timer = self.create_timer(0.1, self.publish_world)

        self.get_logger().info(
            'RViz object world ready: red cube at pickup location.'
        )

    def object_command_callback(self, message):
        command = message.data.strip()

        if command == 'attach_red_cube' and self.cube_state == 'on_table':
            self.cube_state = 'attached'
            self.get_logger().info('Red cube attached to gripper.')

        elif command == 'release_red_cube' and self.cube_state == 'attached':
            self.cube_state = 'placed'
            self.get_logger().info('Red cube released in drop zone.')

        elif command == 'reset_scene':
            self.cube_state = 'on_table'
            self.get_logger().info('Object world reset.')

        else:
            self.get_logger().warn(
                f'Ignored object command: {command} '
                f'(current state: {self.cube_state})'
            )

    def publish_world(self):
        markers = MarkerArray()
        markers.markers.append(self.make_table_marker())
        markers.markers.append(self.make_drop_zone_marker())
        markers.markers.append(self.make_cube_marker())
        self.marker_publisher.publish(markers)

    def make_table_marker(self):
        marker = Marker()
        marker.header.frame_id = 'base_link'
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = 'scene'
        marker.id = 0
        marker.type = Marker.CUBE
        marker.action = Marker.ADD
        marker.pose.position.x = 0.25
        marker.pose.position.y = 0.0
        marker.pose.position.z = -0.15
        marker.pose.orientation.w = 1.0
        marker.scale.x = 0.70
        marker.scale.y = 0.70
        marker.scale.z = 0.04
        marker.color.r = 0.35
        marker.color.g = 0.28
        marker.color.b = 0.20
        marker.color.a = 1.0
        return marker

    def make_drop_zone_marker(self):
        marker = Marker()
        marker.header.frame_id = 'base_link'
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = 'scene'
        marker.id = 1
        marker.type = Marker.CYLINDER
        marker.action = Marker.ADD
        marker.pose.position.x = 0.15
        marker.pose.position.y = -0.25
        marker.pose.position.z = 0.005
        marker.pose.orientation.w = 1.0
        marker.scale.x = 0.10
        marker.scale.y = 0.10
        marker.scale.z = 0.01
        marker.color.r = 0.10
        marker.color.g = 0.80
        marker.color.b = 0.20
        marker.color.a = 0.45
        return marker

    def make_cube_marker(self):
        marker = Marker()
        #marker.header.stamp = self.get_clock().now().to_msg()
        marker.header.stamp.sec=0
        marker.header.stamp.nanosec=0
        #marker.frame_locked=True
        marker.ns = 'objects'
        marker.id = 0
        marker.type = Marker.CUBE
        marker.action = Marker.ADD
        marker.pose.orientation.w = 1.0
        marker.scale.x = 0.04
        marker.scale.y = 0.04
        marker.scale.z = 0.04
        marker.color.r = 0.90
        marker.color.g = 0.05
        marker.color.b = 0.05
        marker.color.a = 1.0

        if self.cube_state == 'attached':
            marker.header.frame_id = 'GRIPPER_BASE'
            marker.pose.position.z = 0.16
        elif self.cube_state == 'placed':
            marker.header.frame_id = 'base_link'
            marker.pose.position.x = 0.15
            marker.pose.position.y = -0.25
            marker.pose.position.z = 0.03
        else:
            marker.header.frame_id = 'base_link'
            marker.pose.position.x = 0.28
            marker.pose.position.y = 0.0
            marker.pose.position.z = 0.03

        return marker


def main(args=None):
    rclpy.init(args=args)
    node = QArmObjectWorld()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()