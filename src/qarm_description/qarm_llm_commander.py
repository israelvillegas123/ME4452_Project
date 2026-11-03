#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
# from google import genai
# from google.genai import types
from pydantic import BaseModel, Field
import json
import time
import threading

from urllib import request, error 
from typing import Literal 

# Define a strict structural mold that Gemini is legally forced to fill out
class QArmJointAngles(BaseModel):
    joint1: float = Field(description="Base rotation angle between -3.0 and 3.0")
    joint2: float = Field(description="Shoulder pitch angle between -1.5 and 1.5")
    joint3: float = Field(description="Elbow pitch angle between -1.5 and 1.5")
    joint4: float = Field(description="Wrist roll angle between -3.0 and 3.0")
    gripper: Literal["open", "closed"] = Field(
        description="Set to open or closed"
    )

class QArmLLMCommander(Node):
    def __init__(self):
        super().__init__('qarm_llm_commander')
        self.publisher_ = self.create_publisher(JointState, '/joint_states', 10)
        # self.client = genai.Client()
        self.ollama_url = 'http://192.168.65.254:11434/api/generate'
        self.ollama_model = 'qwen3:4b-instruct'
        
        # Initial straight-up home posture position values
        self.current_positions = [0.0, 0.0, 0.0, 0.0, 0.0]

        # code for smooth interpolation 
        self.target_positions = self.current_positions.copy()

        # max simulated speed for each commanded joint: 
        # four arm joints in rad/s, gripper in m/s
        self.max_speeds = [1.0, 1.0, 1.0, 1.5, 0.04]
        self.timer_period = 0.05

        self.joint_names = ['joint1', 'joint2', 'joint3', 'joint4', 'left_gripper_joint']
        
        # Broadcast thread loop running at 10Hz to hold the position lock
        self.timer = self.create_timer(
            self.timer_period, 
            self.publish_joint_states
        )

    def advance_toward_target(self):
        """Move each command position toward its target at a bounded speed."""
        for index, target in enumerate(self.target_positions):
            difference = target - self.current_positions[index]
            max_step = self.max_speeds[index] * self.timer_period

            if abs(difference) <= max_step:
                self.current_positions[index] = target
            elif difference > 0.0:
                self.current_positions[index] += max_step
            else:
                self.current_positions[index] -= max_step
    def publish_joint_states(self):
        self.advance_toward_target()
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        msg.position = self.current_positions
        self.publisher_.publish(msg)

    # update target pose instead of teleoperating current pose
    def command_arm_with_ai(self, user_prompt):
        self.get_logger().info(f"Sending prompt to local Qwen: '{user_prompt}'")

        system_instruction = (
            "You are a safe kinematics command interpreter for a 4-axis Quanser "
            "QArm robotic arm. Convert the user's request into one target joint "
            "configuration in radians. Return only JSON matching the supplied schema. "
            "Keep joint1 and joint4 between -3.0 and 3.0. Keep joint2 and joint3 "
            "between -1.5 and 1.5."
            "Set gripper to 'open' or closed'. If the user does not mention it, use 'closed'."
        )

        payload = {
            "model": self.ollama_model,
            "system": system_instruction,
            "prompt": user_prompt,
            "format": QArmJointAngles.model_json_schema(),
            "stream": False,
            "think": False,
            "options": {"temperature": 0}
        }

        try:
            request_data = json.dumps(payload).encode("utf-8")
            http_request = request.Request(
                self.ollama_url,
                data=request_data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with request.urlopen(http_request, timeout=120) as response:
                result = json.loads(response.read().decode("utf-8"))

            angles = QArmJointAngles.model_validate_json(result["response"])

            gripper_position = 0.025 if angles.gripper == "open" else 0.0
            self.target_positions = [
                float(angles.joint1),
                float(angles.joint2),
                float(angles.joint3),
                float(angles.joint4), 
                gripper_position 
            ]

            self.get_logger().info(
                f"Local-Qwen target coordinates: {self.target_positions}"
            )

        except Exception as command_error:
            self.get_logger().error(
                f"Local Qwen command failed: {command_error}"
            )
def ros_spin_thread(node):
    rclpy.spin(node)

def main(args=None):
    rclpy.init(args=args)
    node = QArmLLMCommander()
    
    # Run the background communications processing loop
    threading.Thread(target=ros_spin_thread, args=(node,), daemon=True).start()
    
    time.sleep(1)
    print("\n" + "="*60)
    print("🤖 AI STRICT SCHEMA POSITION-LOCK COMMANDER ACTIVE 🤖")
    print("Give your instructions in plain English ('exit' to finish).")
    print("="*60 + "\n")
    
    try:
        while rclpy.ok():
            user_input = input("Enter prompt for QArm: ")
            if user_input.strip().lower() == 'exit':
                break
            if user_input.strip() == '':
                continue
            node.command_arm_with_ai(user_input)
    except KeyboardInterrupt:
        pass
        
    rclpy.shutdown()

if __name__ == '__main__':
    main()
