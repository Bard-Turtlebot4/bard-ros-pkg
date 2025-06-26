#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_default

from std_msgs.msg import String
from irobot_create_msgs.msg import LightringLeds, LedColor, AudioNote, AudioNoteVector
from irobot_create_msgs.srv import EStop
from builtin_interfaces.msg import Duration
from geometry_msgs.msg import TwistStamped

import time


class GoalCompletedNode(Node):
    def __init__(self):
        super().__init__('bsri_request_completed')

        # Publishers
        self.display_publisher = self.create_publisher(String, '/hmi/display/message', qos_profile_default)
        self.lightring_publisher = self.create_publisher(LightringLeds, '/cmd_lightring', qos_profile_default)
        self.audio_publisher = self.create_publisher(AudioNoteVector, '/cmd_audio', qos_profile_default)
        self.cmd_vel_publisher = self.create_publisher(TwistStamped, '/cmd_vel', qos_profile_default)

        # Service client for /e_stop
        self.e_stop_client = self.create_client(EStop, '/e_stop')
        while not self.e_stop_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /e_stop service...')

        rclpy.spin_once(self, timeout_sec=2)  # Wait briefly for publishers

        self.send_e_stop(True)  # Stop robot
        time.sleep(1.0)         # Wait for 1 second
        self.send_e_stop(False)  # Re-enable robot


        self.set_lightring_green()
        self.display_goal_completed()
        self.play_melody_with_spin()

        self.get_logger().info("Goal feedback sequence complete.")
        self.destroy_node()

    def send_e_stop(self, e_stop_on: bool):
        request = EStop.Request()
        request.e_stop_on = e_stop_on

        future = self.e_stop_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        if future.result() is not None:
            state = "ENABLED" if e_stop_on else "DISABLED"
            self.get_logger().info(f"[EStop] Robot E-Stop {state}")
        else:
            self.get_logger().error("[EStop] Service call failed")

    def set_lightring_green(self):
        msg = LightringLeds()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.override_system = True
        msg.leds = [LedColor(red=0, green=255, blue=0) for _ in range(6)]
        self.lightring_publisher.publish(msg)
        self.get_logger().info("[LightRing] Green LEDs ON")

    def release_lightring(self):
        msg = LightringLeds()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.override_system = False
        self.lightring_publisher.publish(msg)
        self.get_logger().info("[LightRing] Override released")

    def display_goal_completed(self):
        msg = String()
        msg.data = "GOAL COMPLETED"
        self.display_publisher.publish(msg)
        self.get_logger().info("[Display] GOAL COMPLETED")

    def play_melody_with_spin(self):
        g = AudioNote(frequency=392, max_runtime=Duration(sec=0, nanosec=200_000_000))
        c = AudioNote(frequency=522, max_runtime=Duration(sec=0, nanosec=200_000_000))
        e = AudioNote(frequency=658, max_runtime=Duration(sec=0, nanosec=200_000_000))
        g2 = AudioNote(frequency=784, max_runtime=Duration(sec=0, nanosec=400_000_000))
        melody = [g, c, e, g2, e, g2]

        audio_msg = AudioNoteVector()
        audio_msg.header.stamp = self.get_clock().now().to_msg()
        audio_msg.notes = melody
        self.audio_publisher.publish(audio_msg)
        self.get_logger().info("[Audio] Melody sent (G-C-E-G2-E-G2)")

        twist_msg = TwistStamped()
        twist_msg.twist.angular.z = 2.0
        stop_msg = TwistStamped()
        stop_msg.twist.angular.z = 0.0

        self.get_logger().info("[Motion] Spinning while melody plays")
        start_time = time.time()
        duration = 3.4

        while time.time() - start_time < duration:
            twist_msg.header.stamp = self.get_clock().now().to_msg()
            self.cmd_vel_publisher.publish(twist_msg)
            time.sleep(0.1)

        stop_msg.header.stamp = self.get_clock().now().to_msg()
        self.cmd_vel_publisher.publish(stop_msg)
        self.get_logger().info("[Motion] Stopped spinning")

        self.release_lightring()


def main(args=None):
    rclpy.init(args=args)
    node = GoalCompletedNode()
    rclpy.spin_once(node, timeout_sec=2.0)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
