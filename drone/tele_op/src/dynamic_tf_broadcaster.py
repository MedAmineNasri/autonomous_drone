#!/usr/bin/env python  
import roslib
roslib.load_manifest('tele_op')

import math

import rospy
import tf
import math
from geometry_msgs.msg import Pose
from tf.transformations import euler_from_quaternion

x = 0.0
y = 0.0
z = 0.0
yaw = 0.0
rot_x = 0.0 
rot_y = 0.0
rot_z = 0.0 
rot_w = 1.0

def newpose(msg):  
    global x 
    global y 
    global z  
    global rot_x 
    global rot_y
    global rot_z
    global rot_w
    global yaw

    x = msg.position.x
    y = msg.position.y
    z = msg.position.z
    
    rot_x = msg.orientation.x
    rot_y = msg.orientation.y
    rot_z = msg.orientation.z
    rot_w = msg.orientation.w

    (roll , pitch , yaw) = euler_from_quaternion ([rot_x , rot_y , rot_z , rot_w])

    


if __name__ == '__main__':
    rospy.init_node('dynamic_tf_broadcaster')


    sub = rospy.Subscriber ('/drone/gt_pose' , Pose , newpose)

    br = tf.TransformBroadcaster()
    rate = rospy.Rate(10.0)
    while not rospy.is_shutdown():
        x1 = x * math.cos (-yaw) - y * math.sin (-yaw)
        y1 = x * math.sin (-yaw) + y * math.cos (-yaw)

        br.sendTransform((-x1 , -y1 , -z),
                         (rot_x ,rot_y, rot_z, -rot_w),
                         rospy.Time.now(),
                         "map",
                         "drone")


        rate.sleep()
