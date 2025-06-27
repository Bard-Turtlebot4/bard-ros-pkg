from irobot_create_msgs.msg import (
    LightringLeds,
    LedColor,
    AudioNote,
    AudioNoteVector
)
from builtin_interfaces.msg import Duration
from irobot_create_msgs.srv import EStop
from std_msgs.msg import String

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_default

import argparse
import time
import subprocess
import os


MAX_LED_ON_TIME = 10  # seconds
WAIT_FOR_SUBSCRIBERS_TIMEOUT = 2.0  # seconds
PROMPT_FILENAME = "prompt_text.txt"


def resolve_audio_path(filename: str) -> str:
    if os.path.isabs(filename) and os.path.isfile(filename):
        return filename
    fallback = os.path.join(os.getcwd(), filename)
    if os.path.isfile(fallback):
        return fallback
    raise FileNotFoundError(f"Audio file '{filename}' not found.")


def lookup_response_for_audio(mp3_path: str) -> str:
    folder = os.path.dirname(mp3_path)
    prompt_file_path = os.path.join(folder, PROMPT_FILENAME)
    filename = os.path.basename(mp3_path)

    if not os.path.isfile(prompt_file_path):
        raise FileNotFoundError(f"{PROMPT_FILENAME} not found in: {folder}")

    with open(prompt_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if ':' not in line:
                continue
            name, text = line.split(':', 1)
            if name.strip() == filename:
                return text.strip().strip('“”"')

    raise ValueError(f"No response found for '{filename}' in {prompt_file_path}")


class TurtleBot4OneShotNode(Node):
    def __init__(self, audio_path: str | None):
        super().__init__('bsri_request_handler')

        self.display_publisher = self.create_publisher(String, '/hmi/display/message', qos_profile_default)
        self.lightring_publisher = self.create_publisher(LightringLeds, '/cmd_lightring', qos_profile_default)
        self.audio_beep_publisher = self.create_publisher(AudioNoteVector, '/cmd_audio', qos_profile_default)
        self.e_stop_client = self.create_client(EStop, '/e_stop')

        self.wait_for_service(self.e_stop_client)
        self.call_e_stop(True)  # STOP robot
        rclpy.spin_once(self, timeout_sec=2)
        self.wait_for_publishers_ready()

        # Always turn on red lights first
        self.set_lightring_red()

        if audio_path:
            # Audio file mode
            message_text = lookup_response_for_audio(audio_path)
            self.display_message(message_text)
            self.play_audio_while_red(audio_path)
        else:
            # Fallback mode: empty message + beeps
            self.display_message(" ")
            self.play_beep_notes()

        self.release_lightring()
        self.call_e_stop(False)  # RESUME robot

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
            self.get_logger().warn("[EStop] Service call failed or timed out.")

    def wait_for_publishers_ready(self):
        start = time.time()
        while time.time() - start < WAIT_FOR_SUBSCRIBERS_TIMEOUT:
            if (self.lightring_publisher.get_subscription_count() > 0 or
                self.display_publisher.get_subscription_count() > 0 or
                self.audio_beep_publisher.get_subscription_count() > 0):
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

    def play_audio_while_red(self, path: str):
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

        # Two short notes: C (261 Hz), F# (370 Hz) for 200 ms
        note_c = AudioNote(frequency=261, max_runtime=Duration(sec=0, nanosec=700_000_000))
        note_fs = AudioNote(frequency=370, max_runtime=Duration(sec=0, nanosec=700_000_000))

        msg.notes = [note_fs, note_c]
        time.sleep(2)
        self.audio_beep_publisher.publish(msg)

def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio", help="MP3 filename or full path to play")
    cli_args = parser.parse_args()

    rclpy.init(args=args)
    try:
        resolved_audio_path = resolve_audio_path(cli_args.audio) if cli_args.audio else None
        node = TurtleBot4OneShotNode(resolved_audio_path)
        rclpy.spin_once(node, timeout_sec=0.1)
        node.destroy_node()
    finally:
        rclpy.shutdown()


if __name__ == '__main__':
    main()
