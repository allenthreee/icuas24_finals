import rospy
import numpy as np
import math

from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import Quaternion
from std_msgs.msg import Int32

# BAG 1 fruit count: 18 yellow, 3 larger red, 5 smaller red
# BAG 2 fruit count: 18 yellow, 3 larger red, 5 smaller red
# BAG 3 fruit count: 18 yellow, 3 larger red, 5 smaller red
# BAG 4 fruit count: 23 yellow, 7 larger red, 10 smaller red

def calc_marker_dist(marker1, marker2):
    dx = marker1.pose.position.x - marker2.pose.position.x
    dy = marker1.pose.position.y - marker2.pose.position.y
    dz = marker1.pose.position.z - marker2.pose.position.z
    dist = math.sqrt(dx*dx + dy*dy + dz*dz)

    if math.isnan(dist):
        print("dist is nan")
        return 0
    return dist



class PlantFruitDatabase:
    def __init__(self):
        self.red_fruit_pub = rospy.Publisher("/red_fruit_arr_", MarkerArray, queue_size=10)
        self.red_fruit_count_pub = rospy.Publisher('/red_fruit_count', Int32, queue_size=10, latch=True)
        self.red_fruit_arr_ = MarkerArray()
        self.yellow_fruit_pub = rospy.Publisher("/yellow_fruit_arr_", MarkerArray, queue_size=10)
        self.yellow_fruit_count_pub = rospy.Publisher('/yellow_fruit_count', Int32, queue_size=10, latch=True)
        self.yellow_fruit_arr_ = MarkerArray()
        self.real_yellow_fruit_arr_ = []
        self.real_red_fruit_arr_ = []

        self.red_dist = 1.1
        self.yellow_dist = 1.0

    def add_red_fruit_marker(self, fruit_color, fruit_id, position, rpy_roll, two_d_size):
        print(f"add_red_fruit_marker() called, the pose is\n{position}")
        marker = Marker()
        marker.header.frame_id = "camera_init"
        marker.type = marker.SPHERE
        marker.action = marker.ADD

        fruit_size = two_d_size/10
        marker.scale.x = fruit_size
        marker.scale.y = fruit_size
        marker.scale.z = fruit_size
        marker.color.a = 0.2
        if(np.isnan(position[0]) or np.isnan(position[1]) or np.isnan(position[2])):
            print("fruit pose isnan, return")
            return

        # position[0] = round(position[0],0)

        marker.pose.position.x = position[0]
        marker.pose.position.y = position[1]
        marker.pose.position.z = position[2]
        marker.pose.orientation = Quaternion(0,0,0,1)
        marker.id = fruit_id

        rpy_roll = abs(rpy_roll)
        self.real_red_fruit_arr_.clear()
        this_id = 0
        half_count = 0
        for i in range(0,len(self.red_fruit_arr_.markers)):
            old_marker = self.red_fruit_arr_.markers[i]
            dist = calc_marker_dist(old_marker, marker)

            if (dist <= self.red_dist):
                print("duplicate red_fruit by 3D dist, IIR and return")
                old_marker.pose.position.x = (rpy_roll*old_marker.pose.position.x + marker.pose.position.x)/(rpy_roll+1)
                old_marker.pose.position.y = (rpy_roll*old_marker.pose.position.y + marker.pose.position.y)/(rpy_roll+1)
                old_marker.pose.position.z = (rpy_roll*old_marker.pose.position.z + marker.pose.position.z)/(rpy_roll+1)
                old_marker.color.a = old_marker.color.a + 0.2
                old_marker.scale.x = (3*old_marker.scale.x + fruit_size)/4
                old_marker.scale.y = (3*old_marker.scale.y + fruit_size)/4
                old_marker.scale.z = (3*old_marker.scale.z + fruit_size)/4
                # self.red_fruit_count_pub.publish(i+1)
                this_id = i+1

            if(old_marker.color.a >= 1):
                self.real_red_fruit_arr_.append(1)
            elif(0.4 <= old_marker.color.a < 1):
                half_count = half_count+0.5
            elif(old_marker.color.a < 0.4):
                print("new fruit, not take into account")
        # if it's a new red
        marker.color.r = 1.0
        marker.color.g = 0.0
        marker.color.b = 0.0
        if(this_id == 0):
            self.red_fruit_arr_.markers.append(marker)
        new_red_id = len(self.red_fruit_arr_.markers)
        self.red_fruit_count_pub.publish(len(self.real_red_fruit_arr_)+ int(half_count/2))
        if(this_id > len(self.real_red_fruit_arr_) or this_id==0):
            this_id = len(self.real_red_fruit_arr_)
        return this_id

    def add_yellow_fruit_marker(self, fruit_color, fruit_id, position, rpy_roll, two_d_size):
        print("add_yellow_fruit_marker() called")
        marker = Marker()
        marker.header.frame_id = "camera_init"
        marker.type = marker.SPHERE
        marker.action = marker.ADD

        fruit_size = two_d_size/10
        marker.scale.x = fruit_size
        marker.scale.y = fruit_size
        marker.scale.z = fruit_size
        marker.color.a = 0.3
        if(np.isnan(position[0]) or np.isnan(position[1]) or np.isnan(position[2])):
            print("fruit pose isnan, return")
            return

        # position[0] = round(position[0],0)

        marker.pose.position.x = position[0]
        marker.pose.position.y = position[1]
        marker.pose.position.z = position[2]
        marker.pose.orientation = Quaternion(0,0,0,1)
        marker.id = fruit_id

        rpy_roll = abs(rpy_roll)

        self.real_yellow_fruit_arr_.clear()
        this_id = 0
        half_count = 0
        for i in range(0,len(self.yellow_fruit_arr_.markers)):
            old_marker = self.yellow_fruit_arr_.markers[i]
            dist = calc_marker_dist(old_marker, marker)
            if (dist <= self.yellow_dist):
                print("duplicate yellow_fruit by 3D dist, IIR and return")
                old_marker.pose.position.x = (rpy_roll*old_marker.pose.position.x + marker.pose.position.x)/(rpy_roll+1)
                old_marker.pose.position.y = (rpy_roll*old_marker.pose.position.y + marker.pose.position.y)/(rpy_roll+1)
                old_marker.pose.position.z = (rpy_roll*old_marker.pose.position.z + marker.pose.position.z)/(rpy_roll+1)
                old_marker.color.a = old_marker.color.a + 0.3
                old_marker.scale.x = (3*old_marker.scale.x + fruit_size)/4
                old_marker.scale.y = (3*old_marker.scale.y + fruit_size)/4
                old_marker.scale.z = (3*old_marker.scale.z + fruit_size)/4
                # self.yellow_fruit_count_pub.publish(i+1)
                print(f"yellow_id by IIR is: {i+1}, start from 1, NOT 0")
                this_id = i+1
            if(old_marker.color.a > 0.5):
                self.real_yellow_fruit_arr_.append(1)
            elif(0.2 < old_marker.color.a < 0.5):
                half_count = half_count+0.6
            # elif(old_marker.color.a == 0.3):
            #     print(f"real_yellow_fruit_arr_: {self.real_yellow_fruit_arr_}")
        # if it's a new yellow
        marker.color.r = 1.0
        marker.color.g = 1.0
        marker.color.b = 0.0
        if(this_id == 0):
            self.yellow_fruit_arr_.markers.append(marker)
        new_yellow_id = len(self.yellow_fruit_arr_.markers)
        self.yellow_fruit_count_pub.publish(len(self.real_yellow_fruit_arr_)+int(half_count/2))
        print(f"new_yellow_id is: {new_yellow_id}")
        if(this_id > len(self.real_yellow_fruit_arr_) or this_id==0):
            this_id = len(self.real_yellow_fruit_arr_)
        return this_id




    def publish_markers(self):
        # print("publish from class===================================================")
        self.red_fruit_pub.publish(self.red_fruit_arr_)
        self.yellow_fruit_pub.publish(self.yellow_fruit_arr_)
