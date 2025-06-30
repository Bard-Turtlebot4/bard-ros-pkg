#!/usr/bin/env python3

import os
import sys
import time
import subprocess

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_default

from irobot_create_msgs.msg import (
    LightringLeds,
    LedColor,
    AudioNote,
    AudioNoteVector
)
from irobot_create_msgs.srv import EStop
from builtin_interfaces.msg import Duration
from std_msgs.msg import String

# === CONFIG ===
MAX_LED_ON_TIME = 10
WAIT_FOR_SUBSCRIBERS_TIMEOUT = 2.0
PROMPT_FILENAME = "prompt_text.txt"
DEFAULT_PROMPT_FOLDER = "/home/ubuntu/bsri_tts_prompts/mor_cap_verbal"


def load_prompt_line(index: int, base_path: str = DEFAULT_PROMPT_FOLDER) -> tuple[str, str]:
    prompt_path = os.path.join(base_path, PROMPT_FILENAME)
    if not os.path.isfile(prompt_path):
        raise FileNotFoundError(f"Missing prompt file: {prompt_path}")

    with open(prompt_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if ':' in line]

    if index < 0 or index >= len(lines):
        raise IndexError(f"Prompt index {index} out of bounds (0–{len(lines)-1})")

    line = lines[index]
    audio_name, text = line.split(':', 1)
    audio_path = os.path.join(base_path, audio_name.strip())
    return audio_path, text.strip().strip('“”"')


class TurtleBot4OneShotNode(Node):
    def __init__(self, audio_path: str | None, message_text: str | None):
        super().__init__('bsri_request_handler')

        self.display_publisher = self.create_publisher(String, '/hmi/display/message', qos_profile_default)
        self.lightring_publisher = self.create_publisher(LightringLeds, '/cmd_lightring', qos_profile_default)
        self.audio_publisher = self.create_publisher(AudioNoteVector, '/cmd_audio', qos_profile_default)
        self.e_stop_client = self.create_client(EStop, '/e_stop')

        self.wait_for_service(self.e_stop_client)
        self.call_e_stop(True)
        rclpy.spin_once(self, timeout_sec=2.0)
        self.wait_for_publishers_ready()

        self.set_lightring_red()

        if audio_path and message_text:
            self.display_message(message_text)
            self.play_audio_file(audio_path)
        else:
            self.display_message(" ")
            self.play_beep_notes()

        self.release_lightring()
        self.call_e_stop(False)

    def wait_for_service(self, client):
        self.get_logger().info("Waiting for /e_stop service...")
        if not client.wait_for_service(timeout_sec=5.0):
            self.get_logger().error("Service /e_stop not available.")
            raise SystemExit

    def call_e_stop(self, stop_on: bool):
        req = EStop.Request()
        req.e_stop_on = stop_on
        future = self.e_stop_client.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=2.0)
        if future.result() is not None:
            state = "ENABLED" if stop_on else "DISABLED"
            self.get_logger().info(f"[EStop] Robot E-Stop {state}")
        else:
            self.get_logger().warn("[EStop] E-Stop call failed or timed out.")

    def wait_for_publishers_ready(self):
        start = time.time()
        while time.time() - start < WAIT_FOR_SUBSCRIBERS_TIMEOUT:
            if (self.lightring_publisher.get_subscription_count() > 0 or
                self.display_publisher.get_subscription_count() > 0 or
                self.audio_publisher.get_subscription_count() > 0):
                return
            time.sleep(0.1)

    def display_message(self, text: str):
        msg = String()
        msg.data = text
        self.display_publisher.publish(msg)
        self.get_logger().info(f"[Display] Message sent: '{text}'")

    def set_lightring_red(self):
        msg = LightringLeds()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.override_system = True
        msg.leds = [LedColor(red=255, green=0, blue=0) for _ in range(6)]
        self.lightring_publisher.publish(msg)
        self.get_logger().info("[LightRing] Red LEDs ON")

    def release_lightring(self):
        msg = LightringLeds()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.override_system = False
        self.lightring_publisher.publish(msg)
        self.get_logger().info("[LightRing] Override released")

    def play_audio_file(self, path: str):
        self.get_logger().info(f"[Audio] Playing: {path}")
        try:
            proc = subprocess.Popen(['mpg123', path])
            start = time.time()
            while proc.poll() is None:
                if time.time() - start > MAX_LED_ON_TIME:
                    proc.terminate()
                    self.get_logger().warn("[Audio] Playback exceeded time limit.")
                    break
                time.sleep(0.1)
        except Exception as e:
            self.get_logger().error(f"[Audio] Playback failed: {e}")

    def play_beep_notes(self):
        self.get_logger().info("[Audio] Playing 2 short beeps (C and F#)")
        msg = AudioNoteVector()
        msg.header.stamp = self.get_clock().now().to_msg()

        note_c = AudioNote(frequency=261, max_runtime=Duration(sec=0, nanosec=700_000_000))
        note_fs = AudioNote(frequency=370, max_runtime=Duration(sec=0, nanosec=700_000_000))

        msg.notes = [note_fs, note_c]
        time.sleep(2)
        self.audio_publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    try:
        # Default values
        audio_path = None
        message_text = None

        # Command-line usage: ros2 run bsripkg_experiment_2025 bsri_request_denied [index]
        if len(sys.argv) >= 2:
            try:
                index = int(sys.argv[1])
                audio_path, message_text = load_prompt_line(index)
            except Exception as e:
                print(f"[ERROR] Could not load prompt: {e}")
                sys.exit(1)

        node = TurtleBot4OneShotNode(audio_path, message_text)
        rclpy.spin_once(node, timeout_sec=0.1)
        node.destroy_node()

    finally:
        rclpy.shutdown()


if __name__ == '__main__':
    main()
