# Juan Diego Mora Rubio 06/17/2025
# This ROS package for the Turtlebot4 makes a pulsing Create3 lighring

from irobot_create_msgs.msg import InterfaceButtons, LightringLeds

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data


class TurtleBot4FirstNode(Node):
    #lights_on_ = False

    def __init__(self):
        super().__init__('bsri_node_lightring_node')  # initialize ros2 node

        timer_period = 0.1 # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

        # # Subscribe to the /interface_buttons topic
        # self.interface_buttons_subscriber = self.create_subscription(
        #     InterfaceButtons,
        #     '/interface_buttons',
        #     self.interface_buttons_callback,
        #     qos_profile_sensor_data)

        # Create a publisher for the /cmd_lightring topic
        self.lightring_publisher = self.create_publisher(LightringLeds, '/cmd_lightring', qos_profile_sensor_data)

        # while(True):
        #     lightring_function()
    # # Interface buttons subscription callback
    # def interface_buttons_callback(self, create3_buttons_msg: InterfaceButtons):
    #     # Button 1 is pressed
    #     if create3_buttons_msg.button_1.is_pressed:
    #         self.get_logger().info('Button 1 Pressed!')
    #         self.button_1_function()

    # Perform a function when Button 1 is pressed
    def timer_callback(self):
        # Create a ROS 2 message
        lightring_msg = LightringLeds()
        # Stamp the message with the current time
        lightring_msg.header.stamp = self.get_clock().now().to_msg()

        # Lights are currently off
        #if not self.lights_on_:
        # Override system lights
        lightring_msg.override_system = True

        # LED RING
        lightring_msg.leds[self.i % 6].red = 0
        lightring_msg.leds[self.i % 6].blue = 255
        lightring_msg.leds[self.i % 6].green = 255

        self.i += 1


        # Lights are currently on
        #else:
            # Disable system override. The system will take back control of the lightring.
        #lightring_msg.override_system = False

        # Publish the message
        self.lightring_publisher.publish(lightring_msg)
        # Toggle the lights on status
        #self.lights_on_ = not self.lights_on_


def main(args=None):
    rclpy.init(args=args)
    node = TurtleBot4FirstNode()  # initialize ros2 node
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
