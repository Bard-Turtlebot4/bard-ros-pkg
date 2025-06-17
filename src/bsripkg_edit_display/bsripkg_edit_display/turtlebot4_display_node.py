from irobot_create_msgs.msg import InterfaceButtons, LightringLeds

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_default
from std_msgs.msg import String


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

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello World: %d' % self.i
        self.display_publisher.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
        self.i += 1

    def publish_message(self):
        msg = String()
        user_message = input("What do you want Turtlebot to say?: ")
        msg.data = user_message
        self.display_publisher.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)


    # # Interface buttons subscription callback
    # def interface_buttons_callback(self, create3_buttons_msg: InterfaceButtons):
    #     # Button 1 is pressed
    #     if create3_buttons_msg.button_1.is_pressed:
    #         self.get_logger().info('Button 1 Pressed!')
    #         self.button_1_function()

    # Perform a function when Button 1 is pressed
    # def button_1_function(self):
    #     # Create a ROS 2 message
    #     lightring_msg = LightringLeds()
    #     # Stamp the message with the current time
    #     lightring_msg.header.stamp = self.get_clock().now().to_msg()

    #     # Lights are currently off

    #     # Override system lights

    #     # Lights are currently on
    #         # Disable system override. The system will take back control of the lightring.

    #     # Publish the message
    #     self.lightring_publisher.publish(lightring_msg)
    #     # Toggle the lights on status
    #     self.lights_on_ = not self.lights_on_


def main(args=None):
    rclpy.init(args=args)
    node = TurtleBot4FirstNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
