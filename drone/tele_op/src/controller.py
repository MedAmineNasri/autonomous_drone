#!/usr/bin/env python

import rospy
import math

from std_msgs.msg import String
from geometry_msgs.msg import Vector3
from std_msgs.msg import Empty
from geometry_msgs.msg import Pose , PoseStamped
from tf.transformations import euler_from_quaternion
from geometry_msgs.msg import Point , Twist
from math import atan2
from sensor_msgs.msg import Range


x = 0.0
y = 0.0
z = 0.0
yaw = 0.0

f = 0.0
r1 = 0.0
b = 0.0
l = 0.0

goal = Point ()
yawgoal = 0.0



def distanceF(msg):
    global f

    f = msg.range

def distanceL(msg):
    global l

    l = msg.range    

def distanceR(msg):
    global r1

    r1 = msg.range

def distanceB(msg):
    global b

    b = msg.range

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

def newgoal (msg) :
    global goal 
    global yawgoal 
    goal.x =msg.pose.position.x
    goal.y =msg.pose.position.y
    goal.z =msg.pose.position.z   

    rotq = msg.pose.orientation
    (rollgoal , pitchgoal , yawgoal) = euler_from_quaternion ([rotq.x , rotq.y , rotq.z , rotq.w])


 
if __name__=="__main__":

    rospy.init_node ("controller")


    sub = rospy.Subscriber ('/drone/sonar/front' , Range , distanceF)
    sub = rospy.Subscriber ('/drone/sonar/right' , Range , distanceR)
    sub = rospy.Subscriber ('/drone/sonar/back' , Range , distanceB)
    sub = rospy.Subscriber ('/drone/sonar/left' , Range , distanceL)
    sub = rospy.Subscriber ('/drone/gt_pose' , Pose , newpose)
    sub = rospy.Subscriber ('/waypoint' , PoseStamped , newgoal)
    pub = rospy.Publisher('cmd_vel', Twist, queue_size = 1)
    pub2 = rospy.Publisher ('/sonar/collision', String, queue_size = 1)


    empty_msg = Empty()
    r=rospy.Rate(1)

    ZERO_VEL_DIST = 1.2  
    BRAKE_GRAD = 1
    kp = 0.1
    kp1 =0.05
    kp2 = 0.1
    speed = Twist()


    while not rospy.is_shutdown () :
        test_inc_x = goal.x - x
        test_inc_y = goal.y - y

        inc_x = test_inc_x * math.cos (-yaw) - test_inc_y * math.sin (-yaw)
        inc_y = test_inc_x * math.sin (-yaw) + test_inc_y * math.cos (-yaw)
        

        
        kpx = kp * inc_x
        kpy = kp * inc_y

        inc_z = goal.z - z
        kpz = kp1 * inc_z

        kpth = yawgoal - yaw

        


        if (f > ZERO_VEL_DIST) and (inc_x > 0.3) :
            
            Speed_bound_x = (f-ZERO_VEL_DIST) * BRAKE_GRAD
            
            
            speed.linear.x = kpx * Speed_bound_x
            speed.linear.y = 0
            speed.linear.z = kpz
            speed.angular.x = 0.0
            speed.angular.y = 0.0
            speed.angular.z =  kpth
            pub2.publish ("move forward")
            print(kpth)
             
             
        
        elif (b > ZERO_VEL_DIST) and (inc_x < -0.3)  :

            Speed_bound_x =  (b-ZERO_VEL_DIST) * BRAKE_GRAD

            speed.linear.x = kpx * Speed_bound_x
            speed.linear.y = 0
            speed.linear.z = kpz
            speed.angular.x = 0.0
            speed.angular.y = 0.0
            speed.angular.z =  kpth
            pub2.publish ("move backward")
            print (kpth)
             

        elif ((r1> ZERO_VEL_DIST) and (inc_y <-0.3)) :              
            
            Speed_bound_y = (r1-ZERO_VEL_DIST) * BRAKE_GRAD

            speed.linear.x = 0
            speed.linear.y = kpy * Speed_bound_y
            speed.linear.z = kpz
            speed.angular.x = 0.0
            speed.angular.y = 0.0
            speed.angular.z =  kpth
            pub2.publish("move right")
            print (kpth)
            

        elif   ((l> ZERO_VEL_DIST) and (inc_y >0.3)) :
             
            Speed_bound_y = (l-ZERO_VEL_DIST) * BRAKE_GRAD

            speed.linear.x = 0
            speed.linear.y = kpy * Speed_bound_y
            speed.linear.z = kpz
            speed.angular.x = 0.0
            speed.angular.y = 0.0
            speed.angular.z =  kpth
            pub2.publish("move left")
            print (kpth)
            

        else  :       

            speed.linear.x = 0
            speed.linear.y = 0
            speed.linear.z = kpz
            speed.angular.x = 0.0
            speed.angular.y = 0.0
            speed.angular.z =  kpth
            pub2.publish("block")
            print (kpth)
    
            

        
    
        pub.publish(speed)   
        r.sleep   





