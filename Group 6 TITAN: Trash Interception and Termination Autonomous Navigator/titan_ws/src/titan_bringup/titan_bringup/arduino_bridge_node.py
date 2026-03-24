import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TransformStamped
from nav_msgs.msg import Odometry
from std_msgs.msg import Empty
import tf2_ros
from tf_transformations import quaternion_from_euler
import serial
import struct
import math

class ArduinoBridge(Node):
    def __init__(self):
        super().__init__('arduino_bridge')
        
        self.declare_parameter('port', '/dev/arduino')
        self.declare_parameter('baudrate', 115200)
        self.declare_parameter('ticks_per_meter', 3186.0) # Adjusted for 10cm wheels
        self.declare_parameter('wheel_base', 0.45)      # Measured 45cm width
        self.declare_parameter('publish_tf', True)
        
        self.port = self.get_parameter('port').value
        self.baudrate = self.get_parameter('baudrate').value
        self.TICKS_PER_METER = self.get_parameter('ticks_per_meter').value
        self.WHEEL_BASE = self.get_parameter('wheel_base').value
        self.publish_tf = self.get_parameter('publish_tf').value
        
        self.ser = None
        self.connect_serial()

        self.x = 0.0
        self.y = 0.0
        self.th = 0.0
        self.last_l_ticks = None
        self.last_r_ticks = None

        self.odom_pub = self.create_publisher(Odometry, 'odom', 10)
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)
        self.sub = self.create_subscription(Twist, 'cmd_vel', self.cmd_callback, 10)
        self.reset_sub = self.create_subscription(Empty, 'reset_odom', self.reset_callback, 10)
        
        self.create_timer(0.01, self.update_odom) # 100Hz

    def reset_callback(self, msg):
        self.x = 0.0
        self.y = 0.0
        self.th = 0.0
        self.get_logger().info("Odometry reset to zero.")

    def connect_serial(self):
        try:
            if self.ser: self.ser.close()
            self.ser = serial.Serial(self.port, self.baudrate, timeout=0.01)
            self.ser.reset_input_buffer()
            self.get_logger().info(f"Connected to Arduino (Binary Mode) on {self.port}")
        except Exception as e:
            self.get_logger().error(f"Serial error: {e}")
            self.ser = None

    def cmd_callback(self, msg):
        if not self.ser or not self.ser.is_open: return
        
        v = msg.linear.x
        w = msg.angular.z
        v_l = v - (w * self.WHEEL_BASE / 2.0)
        v_r = v + (w * self.WHEEL_BASE / 2.0)
        
        # Scale to PWM (-255 to 255)
        pwm_l = max(-255, min(255, int(v_l * 400))) 
        pwm_r = max(-255, min(255, int(v_r * 400)))
        
        # Packet: [0xAA, 0x55, pwm_l_h, pwm_l_l, pwm_r_h, pwm_r_l, crc]
        crc = (pwm_l ^ pwm_r) & 0xFF
        packet = struct.pack('>BBhhB', 0xAA, 0x55, pwm_l, pwm_r, crc)
        
        try:
            self.ser.write(packet)
        except Exception as e:
            self.get_logger().error(f"Write error: {e}")
            self.ser = None

    def update_odom(self):
        if not self.ser or not self.ser.is_open:
            self.connect_serial()
            return

        try:
            # Revert to 11 bytes: Header(2) + Ticks(8) + CRC(1)
            if self.ser.in_waiting >= 11:
                # Find header
                while self.ser.in_waiting >= 11:
                    if self.ser.read(1) == b'\xAA':
                        if self.ser.read(1) == b'\x55':
                            break
                
                payload = self.ser.read(9)
                if len(payload) < 9: return
                
                # Unpack: ticks (2x i=4), CRC (1x B=1)
                l_ticks, r_ticks, crc = struct.unpack('>iiB', payload)
                
                # Verify CRC
                calc_crc = (l_ticks ^ r_ticks) & 0xFF
                if calc_crc != crc:
                    return

                now = self.get_clock().now().to_msg()
                
                if self.last_l_ticks is None:
                    self.last_l_ticks, self.last_r_ticks = l_ticks, r_ticks
                    return

                dl = (l_ticks - self.last_l_ticks) / self.TICKS_PER_METER
                dr = (r_ticks - self.last_r_ticks) / self.TICKS_PER_METER
                self.last_l_ticks, self.last_r_ticks = l_ticks, r_ticks
                
                d_center = (dl + dr) / 2.0
                d_theta = (dr - dl) / self.WHEEL_BASE
                
                self.x += d_center * math.cos(self.th)
                self.y += d_center * math.sin(self.th)
                self.th += d_theta
                
                q = quaternion_from_euler(0, 0, self.th)
                
                # BroadTF
                t = TransformStamped()
                t.header.stamp = now
                t.header.frame_id, t.child_frame_id = 'odom', 'base_link'
                t.transform.translation.x, t.transform.translation.y = self.x, self.y
                t.transform.rotation.x, t.transform.rotation.y = q[0], q[1]
                t.transform.rotation.z, t.transform.rotation.w = q[2], q[3]
                if self.publish_tf:
                    self.tf_broadcaster.sendTransform(t)

                # Odom
                odom = Odometry()
                odom.header.stamp = now
                odom.header.frame_id, odom.child_frame_id = 'odom', 'base_link'
                odom.pose.pose.position.x, odom.pose.pose.position.y = self.x, self.y
                odom.pose.pose.orientation.x, odom.pose.pose.orientation.y = q[0], q[1]
                odom.pose.pose.orientation.z, odom.pose.pose.orientation.w = q[2], q[3]
                self.odom_pub.publish(odom)

        except Exception as e:
            self.get_logger().error(f"Bridge error: {e}")
            self.ser = None

def main(args=None):
    rclpy.init(args=args)
    node = ArduinoBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()