#!/usr/bin/env python3
# coding: utf-8
import rospy
from jsk_rviz_plugins.msg import OverlayText

# 端末にMainの情報を出力
def write_main_log(msg):
    pub_rviz_text = rospy.Publisher("/handyman_main_log", OverlayText, queue_size=1, latch=True)

    text = OverlayText()
    text.text = msg
    pub_rviz_text.publish(text)

    rospy.loginfo(msg)


# 端末に情報を出力
def write_command(cmd, environment):
    pub_rviz_text_cmd = rospy.Publisher("/handyman_cmd", OverlayText, queue_size=1, latch=True)

    text = "******** TASK COMMAND ********\n"
    text += "Environment : "
    text += environment
    text += "\n"
    for i in range(len(cmd)):
        text += "cmd[{:d}] : ".format(i)
        text += "{} = {}".format(cmd[i].command, cmd[i].target)
        if len(cmd[i].option1) > 0:
            text += "  option1 = {}".format(str(cmd[i].option1))
        if len(cmd[i].option2) > 0:
            text += "  option2 = {}".format(str(cmd[i].option2))
        """
        まだできてない
        if (cmd[i].option != 'UNKNOWN' and cmd[i].option != ''):
            text += ' close to '
            text += str(cmd[i].option)
        """
        text += '\n'
    msg = OverlayText()
    msg.text = text
    pub_rviz_text_cmd.publish(msg)
    rospy.loginfo(text)


# 検出物体を端末に出力
def write_detect_obj(msg):
    pub_rviz_text = rospy.Publisher("/handyman_detect_obj", OverlayText, queue_size=1, latch=True)

    text = OverlayText()
    for furniture in msg.keys():
        text.text += "{}:\n".format(furniture)
        for obj_data in msg[furniture]:
            text.text += "{}, ".format(obj_data.Class)
        text.text += "\n"

    pub_rviz_text.publish(text)


# この部分は「$ python  overlaytext.py」の時には実行される
if __name__ == '__main__':
    from robocup_simopl_handyman.msg import robocup_simopl_handymanCommand
    rospy.init_node("debug_overlay")
    print ("do processing() @overlaytext.py")
    command = []
    a = robocup_simopl_handymanCommand()
    b = robocup_simopl_handymanCommand()
    command.append(a)
    command.append(b)
    write_command(command, "b")
