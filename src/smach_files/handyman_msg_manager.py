#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import rospy
from handyman.msg import HandymanMsg
from smach_files import reset

Msg_message = HandymanMsg()

Instruction_msg = ""
Environment_info = ""
Is_finished_task = False
Is_ready = False
Session_start_time = 0  # rospy.Time()
First_message_flag = True
Corrected_instruction_msg = ""

# SIGVerseからROSに通信を受け取る処理
def cb_sig2ros(msg):
    global Msg_message, Instruction_msg, Is_finished_task, Is_ready, Environment_info, First_message_flag, Session_start_time, Corrected_instruction_msg
    print (msg)

    Msg_message = msg

    if Msg_message.message == "Instruction":
        Instruction_msg = Msg_message.detail
        print ("Handyman : Instruction = " + str(Instruction_msg))
    elif Msg_message.message == "Task_failed":
        Is_finished_task = True
        First_message_flag = True  # 次のセッションの初めてのメッセージを受け取るのを待つため
        print ("Handyman : Task_failed")
        reset.reset_odom()
    elif Msg_message.message == "Task_succeeded":
        Is_finished_task = True
        First_message_flag = True  # 次のセッションの初めてのメッセージを受け取るのを待つため
        print ("Handyman : Task_succeeded")
    elif Msg_message.message == "Mission_complete":
        Is_finished_task = True
        First_message_flag = True  # 次のセッションの初めてのメッセージを受け取るのを待つため
        print ("Handyman : Mission_complete")
    elif Msg_message.message == "Are_you_ready?":
        if First_message_flag:  # セッションの初めてのメッセージを受けっとた時
            Session_start_time = rospy.Time.now()
            print ("First_message: OK")
            print ("Handyman : Get_Session_time = " + str(Session_start_time))
            First_message_flag = False  # セッションの初めてのメッセージを受け終わった
        Is_ready = True
        print ("Handyman : Get_are_you_ready Success")
    elif Msg_message.message == "Environment":
        Environment_info = Msg_message.detail
        print ("Handyman : Get_Environment = " + str(Environment_info))
    elif Msg_message.message == "Corrected_instruction":
        Corrected_instruction_msg = Msg_message.detail
        print ("Handyman : Corrected_instruction = " + str(Corrected_instruction_msg))


#フラッグとメッセージをリセットする処理
def reset_flag_and_msg():
    global Msg_message, Instruction_msg, Is_finished_task, Is_ready, Environment_info, Corrected_instruction_msg, Session_start_time
    Msg_message = HandymanMsg()
    Instruction_msg = ""
    Environment_info = ""
    Corrected_instruction_msg = ""
    Is_finished_task = False
    Is_ready = False


def get_environment_info():
    return Environment_info


def get_instruction_msg():
    return Instruction_msg


def get_finish_task_flag():
    return Is_finished_task


def get_ready_flag():
    return Is_ready


def get_last_msg():
    return Msg_message


def get_session_start_time():
    return Session_start_time


def send_msg(send_word):
    msg = HandymanMsg()
    msg.message = send_word
    pub_ros2sig.publish(msg)


def get_corrected_instruction_msg():
    global Corrected_instruction_msg
    return Corrected_instruction_msg


def reset_stop():
    reset.reset_stop_odom()


sub_sig2ros = rospy.Subscriber("/handyman/message/to_robot", HandymanMsg, cb_sig2ros)
pub_ros2sig = rospy.Publisher("/handyman/message/to_moderator", HandymanMsg, queue_size=10)


# この部分は「$ python handyman_msg_manager.py」の時には実行される
if __name__ == "__main__":
    send_msg()