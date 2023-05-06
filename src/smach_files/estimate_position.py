#!/usr/bin/env python3
# coding: utf-8
import rospy
from standing_position_estimator.srv import estimate_standing_position
from geometry_msgs.msg import Pose

# ロボットの立ち位置を予測する処理
def estimate_pos(target_name="", pose=Pose(), distance=0.8):
    rospy.wait_for_service('/standing_position_estimator/estimate_standing_position', 3.0)
    rospy.loginfo('Estimate_position -> Target_name [%s]', target_name)
    try:
        service = rospy.ServiceProxy('/standing_position_estimator/estimate_standing_position', estimate_standing_position)
        res = service(target_name, pose, distance)
        return True, res.estimated_pos
    except rospy.ServiceException as e:
        print ("Estimate_position Service call failed: %s" % e)
    return False, None


# この部分は「$ python estimate_position.py」の時には実行される
if __name__ == '__main__':
    print ("do processing() @estimate_position.py")
    estimate_pos('target', Pose(), 0.8)
