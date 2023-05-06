#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import rospy
import roslib
import tf
from smach_files import joint_controller, handyman_msg_manager
from subprocess import Popen

#ssdを使って人のtfを取得する処理
def get_person_tf():
    tf_cl_frame = "person"
    tf_pr_frame = "map"
    tf_pr_robot_frame = "base_footprint"

    #tfリスナーの定義
    tf_listener = tf.TransformListener()
    br = tf.TransformBroadcaster()
    target_flag = False
    rate = rospy.Rate(10.0)
    while not rospy.is_shutdown():
        try:
            #親フレームに対する子フレーム
            #t = tf_listener.lookupTransform(tf_pr_frame,tf_cl_frame,rospy.Time())
            tf2robot = tf_listener.lookupTransform(tf_pr_robot_frame,tf_cl_frame,rospy.Time())
            print (tf2robot[0][0])
            if tf2robot[0][0] < 5.0: #ロボット中心に1.5m範囲内に人検出
                br.sendTransform((tf2robot[0][0] - 0.2, tf2robot[0][1], 1.0),
                                    tf.transformations.quaternion_from_euler(0, 0, 1),
                                    rospy.Time.now(),
                                    "placeable_point",
                                    "base_footprint")
                rospy.sleep(2.0)
                target_flag = True
            print ("try target_flag",target_flag)
            break

        except(tf.LookupException, tf.ConnectivityException,tf.ExtrapolationException) as e:
            if handyman_msg_manager.get_finish_task_flag():
                return False
            rospy.logerr(e)
            rate.sleep()
            print ("except target_flag",target_flag)
            joint_controller.move_to_registered_motion("PERSON_DETECT_POSE")
            rospy.sleep(3.0)

    return target_flag


# ssd_nodeの起動
def launch_ssd():
    #ssd_nodeの起動
    Popen(["roslaunch", "ssd_node", "object_detect_with_tf_wrs.launch"])
    #tfをどうにかする処理
    result = get_person_tf()
    rospy.sleep(1.0)
    print ("get placeable_point")
    print ("return ssd_node person",result)
    Popen(["rosnode", "kill", "/ssd_object_detect/ssd_node"])
    Popen(["rosnode", "kill", "/ssd_object_detect/ssd_tf_broadcaster_hsr"])
    return result


# この部分は「$ python ssd_node_manager.py」の時には実行される
if __name__ == "__main__":
    rospy.init_node("debug_ssd_node_manager")
    rospy.loginfo("ssd_node_manager")
    result = launch_ssd()
    print ("complete:",result)