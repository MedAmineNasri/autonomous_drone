#!/usr/bin/env python  
import roslib
roslib.load_manifest('tele_op')

import rospy
import tf

if __name__ == '__main__':
    rospy.init_node('dynamic_tf_broadcaster1')
    br = tf.TransformBroadcaster()
    rate = rospy.Rate(10.0)
    while not rospy.is_shutdown():
        br.sendTransform((0.03 , 0 , 0.01),
                         (0.7071068, 0, 0.7071068, 0),
                         rospy.Time.now(),
                         "sonar_f",
                         "drone")

        br.sendTransform((0.03 , 0 , 0.01),
                         (0.5, -0.5, 0.5, -0.5),
                         rospy.Time.now(),
                         "sonar_l",
                         "drone")

        br.sendTransform((0.03 , 0 , 0.01),
                         (0, 0.7071068, 0, 0.7071068),
                         rospy.Time.now(),
                         "sonar_b",
                         "drone")

        br.sendTransform((0.03 , 0 , 0.01),
                         (0.5, 0.5, 0.5, 0.5),
                         rospy.Time.now(),
                         "sonar_r",
                         "drone")                                                     
        
        rate.sleep()

        