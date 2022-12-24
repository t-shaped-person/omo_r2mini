#!/usr/bin/env python3
import sys
import tty
import rclpy
import select
import termios

from rclpy.node import Node
from rclpy.qos import QoSProfile
from geometry_msgs.msg import Twist

# MAX_LIN_VEL = 0.4                                                               # 0.4m/s (400mm/s)
# MAX_ANG_VEL = 4.7                                                               # 4.7rad/s (wheel speed: 0.3995m/s = 0.17/2*4.7)
MAX_LIN_VEL = 0.3                                                               # 0.3m/s (300mm/s)
MAX_ANG_VEL = 3.5                                                               # 3.5rad/s (wheel speed: 0.2975m/s = 0.17/2*3.5)
STEP_LIN_VEL = 0.01                                                             # 0.01m/s step (10mm/s)
STEP_ANG_VEL = 0.1                                                              # 5.73degree step (wheel speed 0.0085m/s)

msg = '''
Control your omo_r2mini~~
----------------------------------------------------------------------
Moving around:
        w
    a   s   d
        x
w/x: increase/decrease linear velocity (omo_r2mini: ~0.3m/s)
a/d: increase/decrease angular velocity (omo_r2mini: ~3.5rad/s)
space, s: force stop
----------------------------------------------------------------------
CTRL+C to quit
'''

class teleop_keyboard(Node):
    def __init__(self):
        super().__init__('teleop_keyboard')                                     # node name
        qos_profile = QoSProfile(depth=10)                                      # que size 10
        self.publisher = self.create_publisher(Twist, 'cmd_vel', qos_profile)   # message type: Twist, topic name: cmd_vel
        self.settings = termios.tcgetattr(sys.stdin)

    def publish(self, msg):
        self.publisher.publish(msg)
    
    def print(self, str_info):
        self.get_logger().info(str_info)
    
    def constrain(self, vel, min_vel, max_vel):
        return min(max_vel, max(min_vel, vel))
    
    def keyin(self):
        tty.setraw(sys.stdin.fileno())
        select.select([sys.stdin], [], [], 0.1)
        key = sys.stdin.read(1)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key
    
    def smooth_accel_decel(self, current_vel, target_vel, slop):
        if target_vel > current_vel:
            current_vel = min(target_vel, current_vel + slop)
        elif target_vel < current_vel:
            current_vel = max(target_vel, current_vel - slop)
        else:
            current_vel = target_vel
        return current_vel

def main():
    rclpy.init()
    node = teleop_keyboard()
    keyin_cnt = 0
    target_lin_vel, target_ang_vel, current_lin_vel, current_ang_vel = 0.0, 0.0, 0.0, 0.0
    twist = Twist()
    try:
        print(msg)
        while True:
            key = node.keyin()
            if key == 'w' or key.lower() == 'w':
                target_lin_vel = node.constrain(target_lin_vel+STEP_LIN_VEL, -MAX_LIN_VEL, MAX_LIN_VEL)
                keyin_cnt += 1
                node.print(f'current velocity:\tlinear {target_lin_vel:.2f}\t angular {target_ang_vel:.2f}')
            elif key == 'x' or key.lower() == 'x':
                target_lin_vel = node.constrain(target_lin_vel-STEP_LIN_VEL, -MAX_LIN_VEL, MAX_LIN_VEL)
                keyin_cnt += 1
                node.print(f'current velocity:\tlinear {target_lin_vel:.2f}\t angular {target_ang_vel:.2f}')
            elif key == 'a' or key.lower() == 'a':
                target_ang_vel = node.constrain(target_ang_vel+STEP_ANG_VEL, -MAX_ANG_VEL, MAX_ANG_VEL)
                keyin_cnt += 1
                node.print(f'current velocity:\tlinear {target_lin_vel:.2f}\t angular {target_ang_vel:.2f}')
            elif key == 'd' or key.lower() == 'd':
                target_ang_vel = node.constrain(target_ang_vel-STEP_ANG_VEL, -MAX_ANG_VEL, MAX_ANG_VEL)
                keyin_cnt += 1
                node.print(f'current velocity:\tlinear {target_lin_vel:.2f}\t angular {target_ang_vel:.2f}')
            elif key == ' ' or key == 's' or key.lower() == 's':
                target_lin_vel, target_ang_vel, current_lin_vel, current_ang_vel = 0.0, 0.0, 0.0, 0.0
                keyin_cnt += 1
                node.print(f'current velocity:\tlinear {target_lin_vel:.2f}\t angular {target_ang_vel:.2f}')
            else:
                if key == '\x03':
                    break
            
            if keyin_cnt == 20:
                print(msg)
                keyin_cnt = 0
            
            current_lin_vel = node.smooth_accel_decel(current_lin_vel, target_lin_vel, (STEP_LIN_VEL/10))
            twist.linear.x, twist.linear.y, twist.linear.z = current_lin_vel, 0.0, 0.0
            current_ang_vel = node.smooth_accel_decel(current_ang_vel, target_ang_vel, (STEP_ANG_VEL / 10.0))
            twist.angular.x, twist.angular.y, twist.angular.z = 0.0, 0.0, current_ang_vel
            node.publish(twist)
    except Exception as e:
        print(e)
    finally:
        twist.linear.x, twist.linear.y, twist.linear.z = 0.0, 0.0, 0.0
        twist.angular.x, twist.angular.y, twist.angular.z = 0.0, 0.0, 0.0
        node.publish(twist)
        node.destroy_node()
        rclpy.shutdown()
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, node.settings)


if __name__ == '__main__':
    main()