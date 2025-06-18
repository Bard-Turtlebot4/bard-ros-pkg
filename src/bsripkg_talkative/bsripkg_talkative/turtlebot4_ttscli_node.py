from irobot_create_msgs.msg import InterfaceButtons, LightringLeds

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_default
from std_msgs.msg import String
from gtts import gTTS
import subprocess
from io import BytesIO

class TurtleBot4FirstNode(Node):

    def __init__(self):
        super().__init__('turtlebot4_display_node')

        # Create a publisher for the /cmd_lightring topic
        self.display_publisher = self.create_publisher(String, '/hmi/display/message', qos_profile_default)
        # timer_period = 0.5  # seconds
        # self.timer = self.create_timer(timer_period, self.timer_callback)
        # self.i = 0

        while(True):
            self.publish_message()

    def publish_message(self):
        msg = String()
        user_message = input("What do you want Turtlebot to say?: ")
        msg.data = user_message
        # Convert text to speech (in memory)
        tts = gTTS(text = user_message, lang='en')
        mp3_fp = BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)  # Go to start of buffer

        # Play MP3 using mpg123 by piping data into its stdin
        try:
            proc = subprocess.Popen(
                ['mpg123', '-'],  # '-' tells mpg123 to read from stdin
                stdin=subprocess.PIPE
            )
            proc.stdin.write(mp3_fp.read())
            proc.stdin.close()
            proc.wait()
        except Exception as e:
            print(f"Error playing audio: {e}")

        self.display_publisher.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)


def main(args=None):
    rclpy.init(args=args)
    node = TurtleBot4FirstNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
