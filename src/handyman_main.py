#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import rospy
import smach
import smach_ros
from smach_files import overlaytext, node_manager, handyman_msg_manager, move, obj_data_manager, message_analysis
from smach_files import room_data_manager, obj_searcher, obj_recog, estimate_position, grasp, place_position_estimator
from smach_files import put, no_put, joint_controller, obj_depth_measure, reset, box_detect, ssd_node_manager, wheel_controller

# Global変数
Command = []
has_moved = False
has_grasped = False
has_sended = False
has_not_existed = False
Layout_list = ["Layout2019HM01", "Layout2020HM01", "Layout2021HM01", "Layout2019HM02", "Layout2021HM02", "LayoutA", "LayoutB", "LayoutC", "LayoutD"] #使用されるレイアウトのリスト

#置くための微調整が必要な物体
rabbit_flag = False #デフォルトの置く高さが低すぎる物体（Rabbit）
spray_bottle_flag = False #デフォルトの置く高さが低すぎる物体（Spray_bottle）

#長方形の物体、エンドエフェクタは上から物体を把持
game_controller_flag = False

#各種フラグのリセット
def reset_command():
    global Command, has_moved, has_grasped, has_sended, rabbit_flag, spray_bottle_flag, game_controller_flag
    Command = []
    has_moved = False
    has_grasped = False
    has_sended = False
    rabbit_flag = False
    spray_bottle_flag = False
    game_controller_flag = False


#======================================================================================================================================================================================
#==========Sigverseとの通信待機用ステート==============================================================================================================================================

class WaitCommand(smach.State):

    def __init__(self):
        smach.State.__init__(self, outcomes=["check_point", "task_finish"])

    def execute(self, userdata):
        global Command
        overlaytext.write_main_log("STATE : Wait_command\n Reset ROS_Node now")

        # ROS nodeの初期化
        reset_command()
        node_manager.reset_ros_node()
        handyman_msg_manager.reset_flag_and_msg()
        obj_recog.reset_detect_obj_pose_dict()
        overlaytext.write_command([], "Waiting Environment and Command")
        overlaytext.write_main_log("STATE : Wait_command\nReset ROS node Success")
        handyman_msg_manager.reset_stop()
        rospy.sleep(2)

        #レイアウトに応じたslamや家具リストを取得
        while not rospy.is_shutdown():
            #環境の情報が来るまで待機
            if not handyman_msg_manager.get_ready_flag() and handyman_msg_manager.get_environment_info() == "":
                rospy.sleep(0.5)
                continue
            #取得した環境がわからない場合のGiveUp処理
            if handyman_msg_manager.get_environment_info() not in Layout_list:
                handyman_msg_manager.send_msg("Give_up")
                return "task_finish"
            rospy.sleep(3.0)
            room_data_manager.launch_slam(handyman_msg_manager.get_environment_info())
            bed_room_furniture_list, kitchen_furniture_list, living_room_furniture_list, lobby_furniture_list = room_data_manager.get_furniture_name_list()
            message_analysis.set_furniture_name_list(bed_room_furniture_list, kitchen_furniture_list, living_room_furniture_list, lobby_furniture_list)
            rospy.sleep(5.0)
            reset.pub_initial_pose()
            rospy.sleep(2.0)
            handyman_msg_manager.send_msg("I_am_ready")
            overlaytext.write_main_log("STATE : Wait_command\nGet Ready Success")
            break

        #Sigverse側からのメッセージを受け取る(msg.detail)
        while not rospy.is_shutdown():
            instruction_msg = handyman_msg_manager.get_instruction_msg()
            if instruction_msg == "":
                rospy.loginfo("Wait_command -> Waiting Instruction Command")
                rospy.sleep(0.5)
                continue
            rospy.loginfo("Wait_command -> Get Command Success")
            #言語解析
            Command = message_analysis.analysis_msg(instruction_msg)
            print(Command)
            overlaytext.write_main_log("STATE : Wait_command\nGet Command Success")
            rospy.sleep(2.0)
            break
        session_start_time = handyman_msg_manager.get_session_start_time()
        move.set_session_start_time(session_start_time)
        environment = handyman_msg_manager.get_environment_info()
        overlaytext.write_command(Command, environment)

        return "check_point"


#======================================================================================================================================================================================
#==========配列Commandにより、対応するステートへ移動する===============================================================================================================================

class CheckPoint(smach.State):

    def __init__(self):
        self.output_list = ["move", "grasp", "send", "task_finish"]
        smach.State.__init__(self, outcomes=self.output_list)

    def execute(self, userdata):
        if Command:
            rospy.loginfo("Check_point --> {}".format(Command[0].command))
        else:
            handyman_msg_manager.send_msg("Give_up")
            return "task_finish"
        if Command[0].command in self.output_list:
            return Command[0].command
        return "move"


#======================================================================================================================================================================================
#==========自律移動関係ステート========================================================================================================================================================

class Move(smach.State):

    def __init__(self):
        smach.State.__init__(self, outcomes=["move_finish"])

    def execute(self, userdata):
        global has_moved
        target_location = Command[0].target
        overlaytext.write_main_log("STATE : Moving\nTarget Location -> {}".format(target_location))
        #行き先の候補地がレイアウトにない場合
        if target_location not in room_data_manager.get_room_location_list():
            return "move_finish"
        #move.pyにゴールを送信
        result = move.move_to_target_tf(target_location)
        rospy.loginfo(result)
        #移動が失敗した or タスクが終了した
        if not result or handyman_msg_manager.get_finish_task_flag():
            return "move_finish"
        #現在いる部屋をroom_data_managerに保存
        room_data_manager.set_robot_pos(target_location)
        has_moved = True
        return "move_finish"


#======================================================================================================================================================================================
#==========物体把持用ステート==========================================================================================================================================================

class Grasp(smach.State):

    def __init__(self):
        smach.State.__init__(self, outcomes=["grasp_finish"])

    def execute(self, userdata):
        global has_grasped, has_not_existed, rabbit_flag, spray_bottle_flag, game_controller_flag
        target_obj = Command[0].target
        room_patrol_list = room_data_manager.get_now_room_patrol_list()
        on_the_list = []
        close_list = []
        close_obj_list = []
        print("Grasped STATE")
        #目的の物体が存在しない場合（未知物体の処理を追記したい場合はここ）
        if not obj_data_manager.is_existed_obj(target_obj):
            return "grasp_finish"
        print('Command[0].option1: ' + str(Command[0].option1))
        for data in Command[0].option1:  # on the list
            tf_list = room_data_manager.get_target_furniture_obj_tf_list(data)
            print('tf_list: ' + str(tf_list))
            for tf_ in tf_list:
                on_the_list.append(tf_)
        for data in Command[0].option2:  # close the list
            if obj_data_manager.is_existed_obj(data):
                close_obj_list.append(data)
            else:
                tf_list = room_data_manager.get_target_furniture_obj_tf_list(data)
                for tf_ in tf_list:
                    close_list.append(tf_)
        #部屋のcandidateを近い順にソートする
        searching_list = obj_searcher.get_searching_candidate_list(room_patrol_list, on_the_list, close_list)
        print(searching_list) #['lobby#GraspingCandidatesPosition31', 'lobby#GraspingCandidatesPosition33', 'lobby#GraspingCandidatesPosition34']

        #map基準の探索対象のtfを取得
        searching_pose_dict = obj_searcher.get_target_pose("map", searching_list)
        overlaytext.write_main_log("STATE : Grasp\nTarget Object = {}\nsearching_list = {}".format(target_obj, str(searching_list)))
        res_detect = False
        detect_furniture = ""
        #searching listの数だけ繰り返す
        for furniture in searching_list:
            #物体認識
            if obj_recog.is_detected_in_target_pose(searching_pose_dict[furniture]):
                res_detect, target_obj_pose = obj_recog.is_detected_target_obj(target_obj, close_objs=close_obj_list, searching_pose_dict=searching_pose_dict, min_dis=3.0)
                #なにかしら推定された場合
                if res_detect:
                    detect_furniture = furniture
                    break
                else:
                    continue
            #立ち位置算出
            res_estimate, standing_pos = estimate_position.estimate_pos(target_name=furniture, distance=1.05)
            #立ち位置算出に失敗した or タスクが終わった
            if not res_estimate or handyman_msg_manager.get_finish_task_flag():
                return "grasp_finish"
            #立ち位置算出で算出した位置に自律移動
            res_move = move.move_to_target_pose(standing_pos)
            #自律移動に失敗した or タスクが終わっていない場合、↑と同じ処理をもう一度
            if not res_move and not handyman_msg_manager.get_finish_task_flag():
                res_estimate, standing_pos = estimate_position.estimate_pos(target_name=furniture, distance=1.10)
                if not res_estimate or handyman_msg_manager.get_finish_task_flag():
                    return "grasp_finish"
                res_move = move.move_to_target_pose(standing_pos)
            #自律移動に失敗した or タスクが終わった
            if not res_move or handyman_msg_manager.get_finish_task_flag():
                return "grasp_finish"
            #物体認識スタート(yoloのcallback関数が機能する)
            obj_recog.start_object_recognition(furniture, searching_pose_dict[furniture])
            res_detect, target_obj_pose = obj_recog.is_detected_target_obj(target_obj, close_objs=close_obj_list, searching_pose_dict=searching_pose_dict, min_dis=3.0)
            detect_obj_dict = obj_recog.get_detect_obj_pose_dict()
            overlaytext.write_detect_obj(detect_obj_dict)
            if res_detect:
                detect_furniture = furniture
                break

        #物体認識に失敗した
        if not res_detect:
            has_not_existed = True
            return "grasp_finish"

        #立ち位置算出
        res_estimate, standing_pos = estimate_position.estimate_pos(pose=target_obj_pose, distance=0.95)
        #立ち位置算出に失敗した or タスクが終わった
        if not res_estimate or handyman_msg_manager.get_finish_task_flag():
            return "grasp_finish"
        #自律移動
        res_move = move.move_to_target_pose(standing_pos)
        #自律移動に失敗した or タスクが終わっていない場合、↑と同じ処理をもう一度
        if not res_move and not handyman_msg_manager.get_finish_task_flag():
            res_estimate, standing_pos = estimate_position.estimate_pos(target_name=furniture, distance=1.05)
            if not res_estimate or handyman_msg_manager.get_finish_task_flag():
                return "grasp_finish"
            res_move = move.move_to_target_pose(standing_pos)
        #自律移動失敗 or タスク終わった
        if not res_move or handyman_msg_manager.get_finish_task_flag():
            return "grasp_finish"
        #物体認識
        res_recog = obj_recog.start_object_recognition("", searching_pose_dict[detect_furniture], option=target_obj)
        #物体認識が失敗した or タスクが終わっていない
        if not res_recog and not handyman_msg_manager.get_finish_task_flag():
            #立ち位置算出
            res_estimate, standing_pos = estimate_position.estimate_pos(pose=target_obj_pose, distance=1.10)
            #立ち位置算出に失敗した or タスクが終わった
            if not res_estimate or handyman_msg_manager.get_finish_task_flag():
                return "grasp_finish"
            #自律移動
            res_move = move.move_to_target_pose(standing_pos)
            #自律移動に失敗した or タスクが終わった
            if not res_move or handyman_msg_manager.get_finish_task_flag():
                return "grasp_finish"
            #物体認識
            res_recog = obj_recog.start_object_recognition("", searching_pose_dict[detect_furniture], option=target_obj)
        #物体認識に失敗 or タスクが終わった
        if not res_recog or handyman_msg_manager.get_finish_task_flag():
            return "grasp_finish"
        #物体把持
        res_grasp = grasp.grasp_object(target_obj, 0)

        #Rabbitは置く位置が低いのでSENDのためにフラグを立てる
        if target_obj == 'rabbit_doll':
            rabbit_flag = True
        #spray_bottleは置く位置が低いのでSENDのためにフラグを立てる
        if target_obj == "spray_bottle":
            spray_bottle_flag = True
        #game_controllerは長方形の物体と定義されるのでSENDのためにフラグを立てる
        if target_obj == "game_controller":
            game_controller_flag = True

        if not res_grasp:
            if handyman_msg_manager.get_finish_task_flag():
                return "grasp_finish"
            res_recog = obj_recog.start_object_recognition("", searching_pose_dict[detect_furniture], option=target_obj)
            if not res_recog or handyman_msg_manager.get_finish_task_flag():
                return "grasp_finish"
            res_grasp = grasp.grasp_object(target_obj, 0)
            if not res_grasp or handyman_msg_manager.get_finish_task_flag():
                return "grasp_finish"
        rospy.loginfo("Grasp Object Success")
        has_grasped = True
        return "grasp_finish"


#======================================================================================================================================================================================
#==========把持した物体を置きに行くステート============================================================================================================================================

class Send(smach.State):

    def __init__(self):
        smach.State.__init__(self, outcomes=["send_finish"])

    def execute(self, userdata):
        global has_sended, rabbit_flag, spray_bottle_flag, game_controller_flag
        rospy.sleep(1)
        print ("send start",Command[0].target)

        #置き先がアバターの場合
        if Command[0].target == "me":
            Command[0].target = "ModeratorSearchPosition"
        elif Command[0].target == "Moderator":
            Command[0].target = "ModeratorSearchPosition"
        # target_destination_list＝置き位置の名前が入っている場所
        target_destination_list = room_data_manager.get_target_destination_list(Command[0].target)

        if len(target_destination_list) == 0:# or len(Command[0].option1) > 1:
            rospy.logerr("target_destination_list length 0 ")#or len(destination_room) > 1
            return "send_finish"
        close_list = []
        close_obj_list = []
        all_furniture_obj_list = room_data_manager.get_all_furniture_obj_tf_list()

        # 例外処理
        for data in Command[0].option2:  # close the list
            if obj_data_manager.is_existed_obj(data):
                close_obj_list.append(data)
            else:
                tf_list = room_data_manager.get_target_furniture_obj_tf_list(data, furniture_list=all_furniture_obj_list)
                for tf_ in tf_list:
                    close_list.append(tf_)
        target_destination_list = obj_searcher.get_searching_candidate_list(target_destination_list, [], close_list)

        print("target_destination_list",target_destination_list)
        if len(target_destination_list) > 1:
            remove_list = []
            for target_furniture in target_destination_list:
                print("target_furniture: ",target_furniture)
                for room_name in Command[0].option1:
                    print("target_furniture",target_furniture)
                    if room_name not in target_furniture:
                        remove_list.append(target_furniture)
            for remove_furniture in remove_list:
                target_destination_list.remove(remove_furniture)
        print('option1' + str(Command[0].option1))
        print("target_destination_list",target_destination_list)
        print("close_list",close_list)

        # 最終的な置き位置決定
        target_destination = ""
        if "box" in Command[0].target or "wooden_shelf" in Command[0].target: # 今回はwooden_shelfのみだが今後増える可能性あり
            for target_destination_candidate in target_destination_list:
                if "front" in target_destination_candidate:
                    target_destination = target_destination_candidate
                    break # これがないと、次に近い候補に選択肢が行く
        if target_destination == "": #  念の為、frontがない場合に備えて
            if len(target_destination_list) == 0:# or len(Command[0].option1) > 1:
                rospy.logerr("target_destination_list length 0 ")#or len(destination_room) > 1
                return "send_finish"
            target_destination = target_destination_list[0]
        overlaytext.write_main_log("STATE : SEND\nTarget Send = {}".format(target_destination))
        print("target_destination",target_destination)

        # 置く位置＝「人」場合、物体の長さを確認しない
        if "ModeratorSearchPosition" in target_destination:
            arm_shift_z_m = 0.01 #適当な決め打ち
        # ゴミ箱とダンボールに置く場合
        elif "box" in target_destination:
            arm_shift_z_m = 0.2
            rospy.sleep(3.0)
        else:
            #把持した物体が配置できるような微調整はここ
            if rabbit_flag is True: #デフォルトだと低くて置けない物体の高さ調整
                arm_shift_z_m = obj_depth_measure.get_obj_depth()
                rospy.sleep(3.0)
                res_estimate, standing_pos = estimate_position.estimate_pos(target_name=target_destination, distance=0.90)
            elif spray_bottle_flag is True: #デフォルトだと低くて置けない物体の高さ調整
                arm_shift_z_m = obj_depth_measure.get_obj_depth() + 0.02
                rospy.sleep(3.0)
                res_estimate, standing_pos = estimate_position.estimate_pos(target_name=target_destination, distance=0.90)
            elif game_controller_flag is True:
                arm_shift_z_m = 0
                rospy.sleep(3.0)
                res_estimate, standing_pos = estimate_position.estimate_pos(target_name=target_destination, distance=0.90)
            else:
                arm_shift_z_m = obj_depth_measure.get_obj_depth() -0.03
                rospy.sleep(3.0)
                res_estimate, standing_pos = estimate_position.estimate_pos(target_name=target_destination, distance=0.90)
        print ("arm_shift",arm_shift_z_m)

        # 物体の長さが０ｍ以下なら
        if arm_shift_z_m < 0:
            return "send_finish"

        # 置く位置＝「人」場合、物体の長さを確認しない
        if "ModeratorSearchPosition" in target_destination:
            res_move = move.move_to_target_tf(target_destination)

        # ゴミ箱とダンボールに置く場合
        elif "front" in target_destination or "box" in target_destination:
            res_move = move.move_to_target_tf(target_destination)
        else:
            res_move = move.move_to_target_pose(standing_pos)

        # 移動先の座標がない場合
        if not res_move or handyman_msg_manager.get_finish_task_flag():
            return "send_finish"

        # 置く位置＝「box」が含まれる場合
        if "box" in target_destination:
            print ("box version")
            joint_controller.move_to_registered_motion("DETECTING_BOX_POSE")
            rospy.sleep(1.0)
            box_detect.box_entry_gate_detection_ctrl(True)# ゴミ箱検出
            rospy.sleep(2.0)
            res_place_pos = box_detect.wait_for_frame_exists("placeable_point", 30)
            box_detect.box_entry_gate_detection_ctrl(False)
            print ("BOXres_place_pos",res_place_pos)
        #置く位置がアバターの場合
        elif "ModeratorSearchPosition" in target_destination:
            print ("person detection")
            res_place_pos = ssd_node_manager.launch_ssd()# 人検出
        else:
            print ("none box version ")
            if "dining_table" in target_destination:#dining_tableの高さが原因で、次のDETECTING_POSEで物体にぶつかって物体が落ちるため、15cm後ろに下がる
                wheel_controller.processing("X:-25")
            joint_controller.move_to_registered_motion("DETECTING_POSE")
            rospy.sleep(1.0)
            place_position_estimator.placeable_position_estimator_ctrl(True)# 置き位置検出
            rospy.sleep(2.0)
            res_place_pos = place_position_estimator.wait_for_frame_exists("placeable_point", 30)
            place_position_estimator.placeable_position_estimator_ctrl(False)
            print ("res_place_pos",res_place_pos)

        if not res_place_pos or handyman_msg_manager.get_finish_task_flag():
            return "send_finish"

        if "ModeratorSearchPosition" in target_destination:
            res_put = no_put.to_moderator(arm_shift_z_m)# 置く処理
        elif "box" in target_destination:
            if game_controller_flag:
                res_put = no_put.no_put_object_for_game_controller(arm_shift_z_m)# 置く処理
            else:
                res_put = no_put.no_put_object(arm_shift_z_m)# 置く処理
        else:
            if game_controller_flag:
                res_put = put.put_object_for_game_controller(arm_shift_z_m, target_destination)# 置く処理
            else:
                res_put = put.put_object(arm_shift_z_m, target_destination)# 置く処理

        if not res_put or handyman_msg_manager.get_finish_task_flag():
            return "send_finish"
        has_sended = True
        return "send_finish"


#======================================================================================================================================================================================
#==========ステートが終わった後に行われるステート======================================================================================================================================

class IsFinished(smach.State):

    def __init__(self):
        smach.State.__init__(self, outcomes=["continue_task", "task_finish"])

    def execute(self, userdata):
        global Command, has_not_existed
        print(Command[0].command)
        print('has_grasped: ' + str(has_grasped))
        #コマンドの内容によって遷移先が変わる
        if handyman_msg_manager.get_finish_task_flag():
            return "task_finish"
        elif Command[0].command == "move" and has_moved:
            handyman_msg_manager.send_msg("Room_reached")
        elif Command[0].command == "grasp" and has_grasped:
            handyman_msg_manager.send_msg("Object_grasped")
        elif Command[0].command == "grasp" and has_not_existed:
            handyman_msg_manager.send_msg("Does_not_exist")
        elif Command[0].command == "send" and has_sended:
            handyman_msg_manager.send_msg("Task_finished")
        else:
            handyman_msg_manager.send_msg("Give_up")
            return "task_finish"

        #セッションが終了しているか確認
        start_time = rospy.Time.now()
        while rospy.Time.now() < start_time + rospy.Duration(5):
            if len(Command) == 1 or handyman_msg_manager.get_finish_task_flag():
                return "task_finish"
            else:
                rospy.sleep(1)

        #物体認識に失敗した場合の処理
        if Command[0].command == "grasp" and has_not_existed:
            has_not_existed = False
            start_time = rospy.Time.now()
            while rospy.Time.now() < start_time + rospy.Duration(5):
                if handyman_msg_manager.get_corrected_instruction_msg() == "":
                    rospy.sleep(0.5)
                else:
                    Command = message_analysis.analysis_msg(handyman_msg_manager.get_corrected_instruction_msg())
                    break
        try:
            Command.pop(0)
        except IndexError as e:
            print ("Command.pop(0) failed: %s" % e)
            return "task_finish"
        return "continue_task"


#======================================================================================================================================================================================
#===========Main関数===================================================================================================================================================================

def main():
    rospy.init_node("robocup_simopl_handyman_node")
    rospy.loginfo("robocup_simopl_handyman node start")

    #ステートマシンの定義
    sm = smach.StateMachine(outcomes=["Game_finish"])
    with sm:
        smach.StateMachine.add("Wait_command", WaitCommand(), transitions={"check_point": "Check_point", "task_finish": "Is_finished"})
        smach.StateMachine.add("Check_point", CheckPoint(), transitions={"move": "Move", "grasp": "Grasp", "send": "Send", "task_finish": "Wait_command"})
        smach.StateMachine.add("Move", Move(), transitions={"move_finish": "Is_finished"})
        smach.StateMachine.add("Grasp", Grasp(), transitions={"grasp_finish": "Is_finished"})
        smach.StateMachine.add("Send", Send(), transitions={"send_finish": "Is_finished"})
        smach.StateMachine.add("Is_finished", IsFinished(), transitions={"continue_task": "Check_point", "task_finish": "Wait_command"})
    #オブジェクトリストの作成など
    obj_data_manager.read_graspable_obj_list()
    obj_data_manager.read_non_graspable_obj_list()
    obj_searcher.set_tf_listener()
    message_analysis.set_graspable_obj_list(obj_data_manager.get_graspable_obj_list())
    message_analysis.set_non_graspable_obj_list(obj_data_manager.get_non_graspable_obj_list())
    sis = smach_ros.IntrospectionServer("server", sm, "/HANDYMAN_TASK")
    sis.start()
    sm.execute()
    sis.stop()

if __name__ == "__main__":
    main()

#======================================================================================================================================================================================
