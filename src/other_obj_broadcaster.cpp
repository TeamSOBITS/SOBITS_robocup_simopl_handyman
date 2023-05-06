#include <geometry_msgs/Pose.h>/
#include <ros/ros.h>
#include <tf2_ros/static_transform_broadcaster.h>

#include <boost/optional.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <boost/property_tree/ptree.hpp>
#include <iostream>

struct non_obj_data {
  std::string         other_obj_name;
  geometry_msgs::Pose location;
};

class OtherObjBroadcaster {
 private:
  ros::NodeHandle           nh_;
  std::string               map_frame_name_;
  std::string               other_obj_json_path_;
  std::vector<non_obj_data> other_obj_vec_;

  tf2_ros::StaticTransformBroadcaster tf2_br_;

  void raed_non_obj_json(std::string json_path) {
    //rosparamの/location_poseからotherだったらtfを出力
    XmlRpc::XmlRpcValue pose_val;
    nh_.getParam("/location_pose", pose_val);
    //ROS_INFO_STREAM("\n" << pose_val << " : \n");
    int pose_num = pose_val.size();

    for ( int pos = 0; pos < pose_num; pos++ ) {
      //ROS_INFO_STREAM("\n" << pose_val[pos]["location_name"] << "\n");
      non_obj_data other_obj_location;
      //std::string  destination_name;
      if (static_cast<std::string>(pose_val[pos]["object_type"]) == "other") {
        other_obj_location.other_obj_name = static_cast<std::string>(pose_val[pos]["location_name"]); 
        //ROS_INFO_STREAM("\n" << static_cast<double>(pose_val[pos]["translation_x"]) << "\n");
        other_obj_location.location.position.x = static_cast<double>(pose_val[pos]["translation_x"]);
        //ROS_INFO_STREAM("\n" << other_obj_location.location.position.x << "\n");
        other_obj_location.location.position.y = static_cast<double>(pose_val[pos]["translation_y"]);
        other_obj_location.location.position.z = static_cast<double>(pose_val[pos]["translation_z"]);
        other_obj_location.location.orientation.x = static_cast<double>(pose_val[pos]["rotation_x"]);
        other_obj_location.location.orientation.y = static_cast<double>(pose_val[pos]["rotation_y"]);
        other_obj_location.location.orientation.z = static_cast<double>(pose_val[pos]["rotation_z"]);
        other_obj_location.location.orientation.w = static_cast<double>(pose_val[pos]["rotation_w"]);
        other_obj_vec_.push_back(other_obj_location);
      }
      
      //std::cout << "\nother_obj_vec_.destination_name:" << other_obj_vec_[pos].destination_name << std::endl;
      //std::cout << "\nother_obj_vec_.location:" << other_obj_vec_[pos].location << std::endl;
    }
    return;
  }

  void tf2_broadcaster() {
    for (int i = 0; i < other_obj_vec_.size(); i++) {
      geometry_msgs::TransformStamped tf_msg;
      tf_msg.header.frame_id         = map_frame_name_;
      tf_msg.header.stamp            = ros::Time::now();
      tf_msg.child_frame_id          = other_obj_vec_[i].other_obj_name;
      tf_msg.transform.translation.x = other_obj_vec_[i].location.position.x;
      tf_msg.transform.translation.y = other_obj_vec_[i].location.position.y;
      tf_msg.transform.translation.z = other_obj_vec_[i].location.position.z;
      tf_msg.transform.rotation.x    = other_obj_vec_[i].location.orientation.x;
      tf_msg.transform.rotation.y    = other_obj_vec_[i].location.orientation.y;
      tf_msg.transform.rotation.z    = other_obj_vec_[i].location.orientation.z;
      tf_msg.transform.rotation.w    = other_obj_vec_[i].location.orientation.w;
      tf2_br_.sendTransform(tf_msg);
    }
    return;
  }

 public:
  OtherObjBroadcaster() {
    nh_.param("map_frame_name", map_frame_name_, std::string("map"));
    nh_.param("other_obj_json_path",
              other_obj_json_path_,
              std::string("/home/sobits/catkin_ws/src/robocup_simopl_handyman/map/LayoutHM01/"
                          "saved_location_LayoutHM01_other_object.json"));
    this->raed_non_obj_json(other_obj_json_path_);
    this->tf2_broadcaster();
  }
};

int main(int argc, char **argv) {
  ros::init(argc, argv, "other_obj_broad_caster_node");
  OtherObjBroadcaster other_obj_br;
  ros::spin();
  return 0;
}