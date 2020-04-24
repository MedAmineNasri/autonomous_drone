#include <ros/ros.h>

#include <geometry_msgs/Pose.h>
#include <geometry_msgs/PoseStamped.h>
#include <geometry_msgs/TransformStamped.h>
#include <std_msgs/Header.h>
#include <std_msgs/Int16.h>
#include <limits.h>
#include <tf/LinearMath/Quaternion.h>
#include <tf/transform_datatypes.h>
#include <math.h>
#include <cstdlib>
#include <tf/transform_datatypes.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.h>
#include <std_msgs/Empty.h>
#include "std_msgs/String.h"

#include <iostream>
#include <fstream>
#include <string>
#include <sstream>

using namespace std;
using namespace tf2;


//Globals
geometry_msgs::PoseStamped WP,WP_l;
std_msgs::Header header;
geometry_msgs::TransformStamped rtf;

int16_t mode=1;


float cur_pos[3]={};
float cur_yaw=0;
//Mode Change Points
int s1=2,s2=100;
int n1=0,n2=0;
string pos ="";
 





class hl
{
  public:
  hl(){

    //Pose Subscribers
    subCurPose=im.subscribe("/drone/gt_pose",1,&hl::s_cur_cb,this);
    subsonar=im.subscribe("sonar/collision",1,&hl::s_cur_cb2,this);


    //subTf= im.subscribe("/rtf",1,&hl::tf_cb,this);

    //Waypoint Publisher
    waypoint=im.advertise<geometry_msgs::PoseStamped>("/waypoint",1);

    mod_pub=im.advertise<std_msgs::Int16>("/mode",1);
  }

  void tf_cb(const geometry_msgs::TransformStamped::ConstPtr& msg){
    rtf.header=msg->header;
    rtf.child_frame_id=msg->child_frame_id;
    rtf.transform=msg->transform;
  }

  void s_cur_cb(const geometry_msgs::Pose::ConstPtr& msg){
    cur_pos[0]=msg->position.x;
    cur_pos[1]=msg->position.y;
    cur_pos[2]=msg->position.z;

    cur_yaw=tf::getYaw(msg->orientation);

    //header=msg->header;

  }

  void s_cur_cb2(const std_msgs::String::ConstPtr& msg){
  pos = msg->data.c_str();
  }


  ros::Publisher getPub(){
            return waypoint;
        }

  ros::Publisher getPub2(){
            return mod_pub;
        }


  private:
    ros::NodeHandle im;
    ros::Publisher waypoint,mod_pub;
    ros::Subscriber subCurPose,subTf,subsonar;




};



// Class for queue
class queue
{
  geometry_msgs::PoseStamped *arr;     // array to store queue elements
  int capacity;   // maximum capacity of the queue
  int front;    // front points to front element in the queue (if any)
  int rear;     // rear points to last element in the queue
  int count;    // current size of the queue

public:
  queue(int size = 20);   // constructor max 20 waypoints

  void dequeue();
  void enqueue(geometry_msgs::PoseStamped x);
  geometry_msgs::PoseStamped peek();
  int size();
  bool isEmpty();
  bool isFull();
};

// Constructor to initialize queue
queue::queue(int size)
{
  arr = new geometry_msgs::PoseStamped[size];
  capacity = size;
  front = 0;
  rear = -1;
  count = 0;
}

// Utility function to remove front element from the queue
void queue::dequeue()
{
  // check for queue underflow
  if (isEmpty())
  {
    ROS_INFO("UnderFlow\nProgram Terminated\n");
    exit(EXIT_FAILURE);
  }

  ROS_INFO("Loading Next Waypoint") ;

  front = (front + 1) % capacity;
  count--;
}

// Utility function to add an item to the queue
void queue::enqueue(geometry_msgs::PoseStamped item)
{
  // check for queue overflow
  if (isFull())
  {
    ROS_INFO("OverFlow\nProgram Terminated\n");
    exit(EXIT_FAILURE);
  }

  rear = (rear + 1) % capacity;
  arr[rear] = item;
  count++;
  ROS_INFO("Initializing Waypoint %d",count);
}

// Utility function to return front element in the queue
geometry_msgs::PoseStamped queue::peek()
{
  if (isEmpty())
  {
    ROS_INFO("UnderFlow\nProgram Terminated\n");
    exit(EXIT_FAILURE);
  }
  return arr[front];
}

// Utility function to return the size of the queue
int queue::size()
{
  return count;
}

// Utility function to check if the queue is empty or not
bool queue::isEmpty()
{
  return (size() == 0);
}

// Utility function to check if the queue is full or not
bool queue::isFull()
{
  return (size() == capacity);
}

queue readWP(char s[]){

  ifstream source,check;

    source.open(s,ios_base::in);
    ROS_INFO("Output %s",s);
    if(!source){
      cerr << "Could not read file";
    }

    check.open(s,ios_base::in);

    char oneline[30];
    int ct=0;
    int tot_ct=0;
    while(check){
      check.getline(oneline, 30);
      tot_ct++;
    }

    geometry_msgs::PoseStamped wp[tot_ct];
    queue q(tot_ct);

    for(std::string line; std::getline(source, line); )   //read stream line by line
{
    std::istringstream in(line);      //make a stream for the line itself

    std::string type;
                      //and read the first whitespace-separated token


    float ang;
    in >> wp[ct].pose.position.x >> wp[ct].pose.position.y >> wp[ct].pose.position.z>>ang;       //now read the whitespace-separated floats
    ROS_INFO("X :%f",wp[ct].pose.position.x);
    ROS_INFO("Y: %f",wp[ct].pose.position.y);
    ROS_INFO("Z : %f",wp[ct].pose.position.z);
    ROS_INFO("Angle (deg) %f",ang);
    ang= ang*(3.141/180);
    ROS_INFO("Angle (rad) %f",ang);
    quaternionTFToMsg(tf::createQuaternionFromYaw(ang), wp[ct].pose.orientation);
    wp[ct].header=header;

    q.enqueue(wp[ct]);
    ct++;

    ROS_INFO("Reading WP %d",ct);

}

    source.close();
    check.close();

    return q;

}


int main(int argc, char** argv) {
    // Node initialization
    ros::init(argc, argv, "hl");
    hl hlObj; //initalize the class with callback

    ros::Publisher waypoint = hlObj.getPub();

    ros::Publisher mod_pub = hlObj.getPub2();

    queue q = readWP("waypoints.txt");
    int tot_ct=q.size();
    queue s = readWP("scan.txt");
    int s_tot_ct=s.size();
    int wp_no,s_wp_no;

      // create a queue of capacity

    while(ros::ok()){

      ros::spinOnce();
      switch(mode){
        case 1:   //Navigation Waypoints
                  if(!q.isEmpty()){
                                  WP=q.peek();
                                  float x=abs(WP.pose.position.x - cur_pos[0]);
                                  float y=abs(WP.pose.position.y - cur_pos[1]);
                                  float z=abs(WP.pose.position.z - cur_pos[2]);
                                  float theta=(tf::getYaw(WP.pose.orientation)-cur_yaw);
                                 if((x<=0.4&&y<=0.4&&z<=0.4&&theta<=0.1) || (pos=="block")){ 
                                       q.dequeue();
                                       wp_no=tot_ct-q.size();
                                       if(wp_no==s1||wp_no==s2)
                                       { mode=2;
                                        break;
                                       }

                                       if(!q.isEmpty()){
                                             WP=q.peek();

                                      ROS_INFO("Waiting for 0.4 seconds!\n" );
                                        ros::Duration(0.4).sleep();
                                                        } //Sleep for 0.4 seconds
                                                              }
                                }
                                break;
        case 2:   //Scan Mode Waypoints
                  if(!s.isEmpty()){
                                  WP=s.peek();

                                  //tf2::doTransform(WP_l,WP,rtf);

                                  float x=abs(WP.pose.position.x - cur_pos[0]);
                                  float y=abs(WP.pose.position.y - cur_pos[1]);
                                  float z=abs(WP.pose.position.z - cur_pos[2]);
                                  float theta=(tf::getYaw(WP.pose.orientation)-cur_yaw);
                                 if((x<=0.4&&y<=0.4&&z<=0.4&&theta<=0.1) || (pos=="block")){ //
                                      if(s_wp_no==n1||s_wp_no==n2)
                                       { mode=1;
                                        s.dequeue();
                                        s_wp_no=tot_ct-q.size();
                                        break;
                                       }
                                       s.dequeue();
                                       s_wp_no=s_tot_ct-s.size();
                                       if(!s.isEmpty()){
                                             WP=s.peek();
                                             //tf2::doTransform(WP_l,WP,rtf);

                                      ROS_INFO("Waiting for 1 seconds!\n");
                                        ros::Duration(1).sleep();
                                                        }else{
                                                          mode=1;
                                                        } //Sleep for 1 seconds
                                                              }
                                }
                                break;
      }

        waypoint.publish(WP);
        std_msgs::Int16 mode_msg;
        mode_msg.data = mode;
        //mod_pub.publish(mode_msg);
        ros::Duration(0.1).sleep();
    }

}
