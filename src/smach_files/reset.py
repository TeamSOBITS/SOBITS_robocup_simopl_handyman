#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import rospy
from geometry_msgs.msg import Twist
from geometry_msgs.msg import PoseWithCovarianceStamped

is_reset = False


def reset_odom():
    global is_reset
    pub = rospy.Publisher('/hsrb/command_velocity', Twist, queue_size=10)
    is_reset = True
    rate = rospy.Rate(10)
    while is_reset:
        twist = Twist()
        pub.publish(twist)
        rate.sleep()


def reset_stop_odom():
    global is_reset
    is_reset = False


def pub_initial_pose():
    pub = rospy.Publisher("/initialpose", PoseWithCovarianceStamped, queue_size=10)
    data = PoseWithCovarianceStamped()
    data.pose.pose.orientation.w = 1.0
    check_publishers_connection(pub)
    pub.publish(data)


def check_publishers_connection(publisher):
    loop_rate_to_check_connection = rospy.Rate(1)
    while (publisher.get_num_connections() == 0 and not rospy.is_shutdown()):
        try:
            loop_rate_to_check_connection.sleep()
        except rospy.ROSInterruptException:
            pass