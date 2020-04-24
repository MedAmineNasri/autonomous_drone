#!/usr/bin/env python

import rospy

from geometry_msgs.msg import Vector3
from std_msgs.msg import Empty
from geometry_msgs.msg import Pose 
from tf.transformations import euler_from_quaternion
from geometry_msgs.msg import Point , Twist
from math import atan2


x = 0.0
y = 0.0
z = 0.0
yaw = 0.0


def newpose(msg):  
    global x 
    global y 
    global z  
    global yaw 

    x = msg.position.x
    y = msg.position.y
    z = msg.position.z
    
    rot_q = msg.orientation
    (roll , pitch , yaw) = euler_from_quaternion ([rot_q.x , rot_q.y , rot_q.z , rot_q.w])
  
 
if __name__=="__main__":

    rospy.init_node ("controller")

    sub = rospy.Subscriber ('/drone/gt_pose' , Pose , newpose)
    pub = rospy.Publisher('cmd_vel', Twist, queue_size = 1)



    r=rospy.Rate(4)
    goal = Point ()
    goal.x =4
    goal.y =1
    goal.z =4

    


    while not rospy.is_shutdown () :
        kp = 0.1
        kp1 =0.05
        inc_x = goal.x - x
        kpx = kp * inc_x

        inc_y = goal.y - y
        kpy = kp * inc_y

        inc_z = goal.z - z
        kpz = kp1 * inc_z

        angle_to_goal = atan2 (inc_x , inc_y)
        kpd = angle_to_goal*kp

        speed = Twist()

        #if abs(angle_to_goal - yaw ) > 0.1 :
            
        #    speed.linear.x=0.0
        #    speed.linear.y=0.0
        #    speed.linear.z=0.0
        #    speed.angular.x = 0.0
        #    speed.angular.y = 0.0
        #    speed.angular.z = kpd

            
            
            
        #else :         
        speed.linear.x = kpx
        speed.linear.y = kpy
        speed.linear.z = kpz
        speed.angular.x = 0.0
        speed.angular.y = 0.0
        speed.angular.z = 0.0      

        
    
        pub.publish(speed)   
        r.sleep   





