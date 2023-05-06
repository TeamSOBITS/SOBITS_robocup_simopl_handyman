#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import rospy
from subprocess import Popen

kill_node_list = [
    # "/rviz",
    #"/robot_ctrl/hsr_controller",
    "/move_base",
    "/pcl_scan_mixer",
    "/sobit_navigation/waypoint_nav",
    #"/depth_image_proc_point_cloud_xyz",  # HSR minimal
    #"/depth_image_proc_point_cloud_xyzrgb",
    #"/depth_image_proc_register",
    "/handyman_tf_broadcaster/destination_broadcaster_node",
    "/handyman_tf_broadcaster/other_obj_broadcaster_node",
    "/standing_position_estimator/standing_position_estimator_node",
    #"/robot_ctrl/joint_controller",
    #"/robot_ctrl/get_object_depth",
    "/map_server",
    "/map_movebase_server",
    "/amcl",  # sobit_navigation
]


def reset_ros_node():
    for node in kill_node_list:
        command = ["rosnode", "kill", node]
        print (command)
        Popen(command)
    rospy.sleep(10.0)
    Popen(["rosnode", "cleanup"])
    rospy.sleep(5.0)
    # Popen(["roslaunch", "hsr_ros", "minimal.launch"])
    # rospy.sleep(3.0)
    Popen(["roslaunch", "standing_position_estimator", "standing_position_estimator.launch"])
    rospy.sleep(6.0)
    rospy.loginfo("************* ROS_NODE RESET FINISH *************")
    """
    # sobit_navigation
    Popen(["rosnode", "kill", "/amcl"])
    Popen(["rosnode", "kill", "/map_movebase_server"])
    Popen(["rosnode", "kill", "/map_server"])
    Popen(["rosnode", "kill", "/move_base"])
    Popen(["rosnode", "kill", "/sobit_navigation/waypoint_nav"])
    Popen(["rosnode", "kill", "/pcl_scan_mixer"])
    # HSR_ros minimal
    Popen(["rosnode", "kill", "/robot_ctrl/grasp_obj_by_frame"])
    Popen(["rosnode", "kill", "/robot_ctrl/hsr_controller"])
    Popen(["rosnode", "kill", "/hsrb/head_rgbd_sensor/depth_metric"])
    Popen(["rosnode", "kill", "/hsrb/head_rgbd_sensor/depth_metric_rect"])
    Popen(["rosnode", "kill", "/hsrb/head_rgbd_sensor/depth_points"])
    Popen(["rosnode", "kill", "/hsrb/head_rgbd_sensor/depth_rectify_depth"])
    Popen(["rosnode", "kill", "/hsrb/head_rgbd_sensor/depth_registered_sw_metric_rect"])
    Popen(["rosnode", "kill", "/hsrb/head_rgbd_sensor/head_rgbd_sensor_nodelet_manager"])
    Popen(["rosnode", "kill", "/hsrb/head_rgbd_sensor/ir_rectify_ir"])
    Popen(["rosnode", "kill", "/hsrb/head_rgbd_sensor/points_xyzrgb_sw_registered"])
    Popen(["rosnode", "kill", "/hsrb/head_rgbd_sensor/register_depth_rgb"])
    Popen(["rosnode", "kill", "/hsrb/head_rgbd_sensor/rgb_rectify_color"])
    Popen(["rosnode", "kill", "/robot_ctrl/get_object_depth"])
    rospy.sleep(6.0)

    Popen(["rosnode", "cleanup"])
    rospy.sleep(3.0)
    Popen(["roslaunch", "hsr_ros", "minimal.launch"])
    rospy.sleep(3.0)
    Popen(["roslaunch", "standing_position_estimator", "standing_position_estimator.launch"])
    rospy.sleep(6.0)
    rospy.loginfo("************* ROS_NODE RESET FINISH *************")
    """


# この部分は「$ python node_manager.py」の時には実行される
if __name__ == "__main__":
    rospy.init_node("debug_node_manager")