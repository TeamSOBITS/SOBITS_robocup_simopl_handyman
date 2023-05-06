#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import rospy
import numpy as np
from sobit_common_msg.msg import ObjectPoseArray
from sobit_common_msg.srv import RunCtrl
from smach_files import handyman_msg_manager, joint_controller

detect_obj_pose_list = []
detect_obj_pose_dict = {}


def reset_detect_obj_pose_dict():
    global detect_obj_pose_dict
    detect_obj_pose_dict = {}


def get_detect_obj_pose_dict():
    return detect_obj_pose_dict


def cb_obj_poses(msg):
    global detect_obj_pose_list
    detect_obj_pose_list = msg.object_poses
    print(detect_obj_pose_list)


def yolo_ctrl(mode):
    rospy.wait_for_service("/yolov5_ros/run_ctrl")
    try:
        yolo_ctrl = rospy.ServiceProxy("/yolov5_ros/run_ctrl", RunCtrl)
        res = yolo_ctrl(mode)
        return res.response
    except rospy.ServiceException as e:
        rospy.logerr("yolo_ctrl service call failed : {}".format(e))
    return False


# 物体認識を開始
def start_object_recognition(location, pose, option=""):
    global detect_obj_pose_list, detect_obj_pose_dict
    detect_obj_pose_list = []
    rospy.Subscriber("yolov5_ros/object_poses", ObjectPoseArray, cb_obj_poses)
    yolo_ctrl(True)
    if handyman_msg_manager.get_finish_task_flag():
        return False
    if pose.position.z > 0.70:
        joint_controller.move_to_registered_motion("DETECTING_POSE2")
    else:
        joint_controller.move_to_registered_motion("DETECTING_POSE")
    rospy.sleep(2.0)
    start_time = rospy.Time.now()
    while rospy.Time.now() < start_time + rospy.Duration(4.0) and not handyman_msg_manager.get_finish_task_flag():
        rospy.sleep(0.5)
        if not option == "":
            for obj in detect_obj_pose_list:
                if option == obj.Class:
                    yolo_ctrl(False)
                    return True
    detect_obj_pose_dict[location] = detect_obj_pose_list
    yolo_ctrl(False)
    rospy.sleep(1.0)
    return False


# 目標位置かどうかを判断する処理
def is_detected_in_target_pose(target_pose, threshold=0.2):
    for furniture in detect_obj_pose_dict.keys():
        obj_data_array = detect_obj_pose_dict[furniture]
        for obj_data in obj_data_array:
            distance = np.sqrt((obj_data.pose.position.x - target_pose.position.x)**2 + (obj_data.pose.position.y - target_pose.position.y)**2 + (obj_data.pose.position.z - target_pose.position.z)**2)
            if distance < threshold:
                return True
    return False


# 目標物体かどうかを判断する処理
def is_detected_target_obj(target_obj, close_objs=[], searching_pose_dict={}, min_dis=2.0):
    target_obj_ = []
    close_objs_ = {}  # key: ojb_name 中身　：  [pose, pose..]
    for furniture in detect_obj_pose_dict.keys():
        obj_data_array = detect_obj_pose_dict[furniture]
        for obj_data in obj_data_array:

            #未知物体（2022年はmatryoshka）の場合複数のケースに対応
            #if "matryoshka" in obj_data.Class and target_obj == "matryoshka":
            #    obj_data.Class = "matryoshka"

            if obj_data.Class == target_obj:
                target_obj_.append(obj_data.pose)
            for close_obj in close_objs:
                if obj_data.Class == close_obj:
                    close_objs_.setdefault(obj_data.Class, []).append(obj_data.pose)
    print (close_objs_)
    if len(target_obj_) == 0:  # target_objをまだ見つけてない
        rospy.loginfo("target_objをまだ見つけてない")
        return False, None
    if len(close_objs) == 0:  # close_objが質問文にない場合でtarget_objをもう見つけている場合
        for searching_pose in searching_pose_dict.values():
            distance = np.sqrt((searching_pose.position.x - target_obj_[0].position.x)**2 + (searching_pose.position.y - target_obj_[0].position.y)**2 +
                               (searching_pose.position.z - target_obj_[0].position.z)**2)
            print ("distance : ", distance)
            if distance < 0.7:
                return True, target_obj_[0]
        rospy.logerr("近くにobjがありません")
        return False, target_obj_[0]
    for close_obj in close_objs:  # 目的のcloseオブジェクトリスト
        has_detected_close_obj = False
        for close_obj_ in close_objs_.keys():  # 今まで見つけたcloseオブジェクトリスト
            print (close_obj_)
            if close_obj == close_obj_:
                has_detected_close_obj = True
                break
        if not has_detected_close_obj:
            rospy.logerr("close_objが今までに1つでも見つけられなかった")
            return False, None  # close_objが今までに1つでも見つけられなかった

    # しきい値距離の計算
    target_obj_index = 0
    is_near_exist = False
    for i, target_obj_pose in enumerate(target_obj_):
        # test = False
        target_obj_index = i
        for close_obj_poses in close_objs_.values():  # ある１つのclose_obj のposeが配列が入ってる
            is_near_exist = False
            for close_obj_pose in close_obj_poses:
                dis = np.sqrt((target_obj_pose.position.x - close_obj_pose.position.x)**2 + (target_obj_pose.position.y - close_obj_pose.position.y)**2 +
                              (target_obj_pose.position.z - close_obj_pose.position.z)**2)
                rospy.loginfo("no if dis : {} , min_dis : {}".format(dis, min_dis))
                if dis < min_dis:
                    is_near_exist = True
                    rospy.loginfo("dis : {} , min_dis : {}".format(dis, min_dis))
                    rospy.loginfo("指定されたclose_objがtarget_objの近くにあった場合")
                    break
            if not is_near_exist:  # 指定されたclose_objがtarget_objの近くにない場合
                rospy.loginfo("指定されたclose_objがtarget_objの近くにない場合")
                break

        if is_near_exist:  # 指定されたすべてのclose_objがtarget_objの近くにあった場合
            break

    if is_near_exist:
        return True, target_obj_[target_obj_index]
    else:
        return False, None