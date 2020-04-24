#!/usr/bin/env python
# PointCloud2 color cube
# https://answers.ros.org/question/289576/understanding-the-bytes-in-a-pcl2-message/
import rospy
import struct

from sensor_msgs import point_cloud2
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Header
from sensor_msgs.msg import Range



l = 0.0


   

def distanceL(msg):
    global l

    l = msg.range




if __name__=="__main__":
   
    rospy.init_node("pc_left")


    
    

    pub = rospy.Publisher("point_cloud2", PointCloud2, queue_size=2)

    rr=rospy.Rate(500)

    lim = 8
    while not rospy.is_shutdown () :
        
        points = []
        sub = rospy.Subscriber ('/drone/sonar/left' , Range , distanceL)
        
        for i in range(lim):
            for j in range(lim):
                for k in range(lim):
                    x1 = float(i) / (8 * lim)
                    y1 = float(j) / (8 * lim)
                    z1 = float(k) / (8 * lim)
                    r = int(x1 * 8 * 255.0)
                    g = int(y1 * 8 * 255.0)
                    b = int(z1 * 8 * 255.0)
                    a = 255
                    
                    left_distance = l + 0.03
                    x=x1 - 0.0625 
                    y = y1 + left_distance 
                    z = z1 - 0.0625
                    
                    #print (r, g, b, a)
                    rgb = struct.unpack('I', struct.pack('BBBB', b, g, r, a))[0]
                    #print (hex(rgb))
                    pt = [x, y, z, rgb]
                    if (l<4) :
                        points.append(pt)

        fields = [PointField('x', 0, PointField.FLOAT32, 1),
                PointField('y', 4, PointField.FLOAT32, 1),
                PointField('z', 8, PointField.FLOAT32, 1),
                # PointField('rgb', 12, PointField.UINT32, 1),
                PointField('rgba', 12, PointField.UINT32, 1),
                ]

        #print points
        print l 

        header = Header()
        header.frame_id = "drone"
        pc2 = point_cloud2.create_cloud(header, fields, points)

        
        pc2.header.stamp = rospy.Time.now()
        pub.publish(pc2)
        rr.sleep 
