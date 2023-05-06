#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import rospy
import tf
import numpy as np
from geometry_msgs.msg import Pose

tf_listener = None

# 物体探索の位置を近い順にソートする処理
def sort_closeness_target(candidate_list, target_list=["base_footprint"], close_threshold_m=0):
    searching_candidate_list = []
    distance_list = []
    for target in target_list:
        for candidate in candidate_list:
            now = rospy.Time.now()
            try:
                tf_listener.waitForTransform(target, candidate, now, rospy.Duration(2.0))
                (trans, _) = tf_listener.lookupTransform(target, candidate, now)
            except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
                continue
            except Exception as e:
                rospy.logerr(e)
                continue
            distance = np.sqrt(trans[0]**2 + trans[1]**2)
            if not close_threshold_m == 0:
                if distance < close_threshold_m:
                    searching_candidate_list.append(candidate)
                    distance_list.append(distance)
            else:
                searching_candidate_list.append(candidate)
                distance_list.append(distance)

    index_min_distance = np.argsort(distance_list)
    sorted_list = []
    print ("searching_candidate_list : ", searching_candidate_list)
    print ("distance_list : ", distance_list)
    for idx in index_min_distance:
        sorted_list.append(searching_candidate_list[idx])
    print ("\nsorted_list : ", sorted_list)
    sorted_list = sorted(set(sorted_list), key=sorted_list.index)
    print ("\nsorted_list : ", sorted_list)
    return sorted_list


# 物体探索の位置を近い順にソートする処理
def sort_closeness_target_base(candidate_list):
    candidate_pose_dict = {}
    sorted_list = []
    for candidate in candidate_list:
        try:
            tf_listener.waitForTransform("base_footprint", candidate, rospy.Time(0), rospy.Duration(3.0))
            (trans, _) = tf_listener.lookupTransform("base_footprint", candidate, rospy.Time(0))
        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            continue
        except Exception as e:
            rospy.logerr(e)
            continue
        candidate_pose_dict[candidate] = trans
    base = (0.0, 0.0, 0.0)
    while not len(candidate_pose_dict) == 0:
        shortest_dis = 1000000
        shortest_key = ""
        for key in candidate_pose_dict.keys():
            trans = candidate_pose_dict[key]
            dis = np.sqrt((trans[0] - base[0])**2 + (trans[1] - base[1])**2)
            if dis < shortest_dis:
                shortest_dis = dis
                shortest_key = key
        sorted_list.append(shortest_key)
        base = candidate_pose_dict[shortest_key]
        candidate_pose_dict.pop(shortest_key)

    return sorted_list


# room_patrol_list, on_the_list, close_list3つのリストを合わせて、部屋のcandidateを近い順にソートする処理
def get_searching_candidate_list(room_patrol_list, on_the_list, close_list, close_threshold_m=3., max_list_size=2):
    total_sorted_list = []
    if len(on_the_list) == 0 and len(close_list) == 0:
        sorted_list = sort_closeness_target_base(room_patrol_list)
        return sorted_list
    elif len(on_the_list) > 0 and len(close_list) == 0:
        #"sth on the FURNITURE"の場合そのFURNITURE上の何ヶ所のGraspablePositionを見るのかを設定
        #物体検出に時間短縮や，移動の際の衝突リスクを避けることができる
        #ただし設定により行かなくなったGraspablePositionが他のGraspablePositionと離れている場合，カメラに移せない場合があるので注意
        print('on_the_list' + str(on_the_list))
        for furniture in on_the_list:
            sorted_list = sort_closeness_target(room_patrol_list, target_list=[furniture], close_threshold_m=1.5)
            if "custom_kitchen" in furniture:
                max_list_size = 6
            elif "shelf" in furniture or "wooden_cupboard" in furniture or "white_rack" in furniture or "iron_bed" in furniture or "sink" in furniture or "TV_rack" in furniture:
                max_list_size = 3
            elif "dining_table" in furniture or "white_side_table" in furniture: #white_side_tableに4つ物体が乗っているケースでsort後に4つめになるgraspablepositionが他の物体と離れていたため変更
                max_list_size = 4
            elif "corner_sofa" in furniture or "armchair" in furniture:
                max_list_size = 1
            if len(sorted_list) > max_list_size:
                sorted_list = sorted_list[:max_list_size]
            print('furniture name: ' + str(furniture))
            total_sorted_list = total_sorted_list + sorted_list
        print('total_sorted_list: ' + str(set(total_sorted_list)))
        return list(set(total_sorted_list))
    elif len(on_the_list) > 0:  # & len(close_list) > 0
        sorted_close_list = sort_closeness_target(on_the_list, target_list=close_list, close_threshold_m=3.0)
        for furniture in sort_closeness_target:
            sorted_list = sort_closeness_target(room_patrol_list, target_list=[furniture], close_threshold_m=1.5)
            if "custom_kitchen" in furniture:
                max_list_size = 6
            elif "shelf" in furniture or "wooden_cupboard" in furniture or "white_rack" in furniture or "iron_bed" in furniture or "sink" in furniture or "TV_rack" in furniture:
                max_list_size = 3
            elif "dining_table" in furniture or "white_side_table" in furniture: #white_side_tableに4つ物体が乗っているケースでsort後に4つめになるgraspablepositionが他の物体と離れていたため変更 in 2021
                max_list_size = 4
            elif "corner_sofa" in furniture or "armchair" in furniture:
                max_list_size = 1
            if len(sorted_list) > max_list_size:
                sorted_list = sorted_list[:max_list_size]
            print('furniture name: ' + str(furniture))
            total_sorted_list = total_sorted_list + sorted_list
        print('total_sorted_list: ' + str(set(total_sorted_list)))
        return list(set(total_sorted_list))
    else:  # len(on_the_list) == 0 & len(close_list) > 0
        sorted_list = sort_closeness_target(room_patrol_list, target_list=close_list, close_threshold_m=3.0)
        max_list_size = 4
        if len(sorted_list) > max_list_size:
            sorted_list = sorted_list[:max_list_size]
        return sorted_list


# map基準の探索対象のtfを取得
def get_target_pose(base, tf_name_list):
    target_pose_list = {}
    for tf_name in tf_name_list:
        try:
            tf_listener.waitForTransform(base, tf_name, rospy.Time(0), rospy.Duration(3.0))
            (trans, rot) = tf_listener.lookupTransform(base, tf_name, rospy.Time(0))
            pose = Pose()
            pose.position.x = trans[0]
            pose.position.y = trans[1]
            pose.position.z = trans[2]
            pose.orientation.x = rot[0]
            pose.orientation.y = rot[1]
            pose.orientation.z = rot[2]
            pose.orientation.w = rot[3]
            target_pose_list[tf_name] = pose
        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            continue
        except Exception as e:
            rospy.logerr(e)
            continue
    return target_pose_list


# tf listenerをセット
def set_tf_listener():
    global tf_listener
    tf_listener = tf.TransformListener()


# この部分は「$ python obj_searcher.py」の時には実行される
if __name__ == "__main__":
    import room_data_manager
    rospy.init_node("debug_object_searcher")
    set_tf_listener()
    #room_data_manager.launch_slam("Layout2019HM02")
    rospy.sleep(2)
    bed, kitchen, living, lobby = room_data_manager.get_furniture_patrol_list()
    res = get_searching_candidate_list(living, [],["living_room#TV", "living_room#round_low_table"], )
    #print res
