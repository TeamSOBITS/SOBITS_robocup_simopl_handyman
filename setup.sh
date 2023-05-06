#!/bin/bash

cd ~/catkin_ws/src

git clone https://github.com/TeamSOBITS/robocup_simopl_handyman.git
cd robocup_simopl_handyman
git checkout rcjp_2023
cd ..

echo "Install HSR ROS"
git clone https://github.com/TeamSOBITS/hsr_ros.git
cd hsr_ros
git checkout handyman_2022
cd ..

echo "Install SOBIT Common"
git clone https://github.com/TeamSOBITS/sobit_common.git
cd sobit_common
git checkout handyman-2022
cd ..

echo "Install SOBIT Navigation Stack"
git clone https://github.com/TeamSOBITS/sobit_navigation_stack.git

echo "Install HSR Navigation Stack"
git clone https://github.com/TeamSOBITS/hsr_navigation_stack.git
cd hsr_navigation_stack
git checkout noetic_sigverse_2022
cd ..

echo "Install Standing Position Estimator"
git clone https://github.com/TeamSOBITS/standing_position_estimator.git


echo "Install Placeable Position Estimator"
git clone https://github.com/TeamSOBITS/placeable_position_estimator.git
cd placeable_position_estimator/
git checkout noetic_sigverse_2022
cd ..

echo "Install Box Entry Gate Detection"
git clone https://github.com/TeamSOBITS/box_entry_gate_detection.git
cd box_entry_gate_detection/
git checkout noetic_sigverse_2022
cd ..

echo "Install SSD Node"
git clone https://github.com/TeamSOBITS/ssd_node.git
cd ssd_node/
git checkout noetic_sigverse_2022
cd ..

echo "Install Pytorch Yolo"
git clone https://github.com/TeamSOBITS/yolov5_ros.git
cd yolov5_ros/
git checkout
cd ..

echo "Install SIGVerse ROS"
git clone https://github.com/TeamSOBITS/sigverse_ros_package.git
cd sigverse_ros_package
git checkout handyman_2022
cd ..

echo "Install Handyman ROS"
git clone https://github.com/TeamSOBITS/handyman_ros.git

echo "Install Image_pipeline"
git clone https://github.com/ros-perception/image_pipeline.git

echo "Install nltk"
python3 -m pip  install -U nltk --user

echo "torchtext"
python3 -m pip  install torchtext

echo "Install ros-noetic-roswww"
sudo apt-get install ros-noetic-roswww

echo "Install ros-noetic-rosbridge-suite"
sudo apt-get install ros-noetic-rosbridge-suite

echo "Install ros-noetic-jsk-rviz-plugins"
sudo apt-get install ros-noetic-jsk-rviz-plugins

echo "╔══╣ Install: Sobit Common (STARTING) ╠══╗"


sudo apt-get update
sudo apt-get install -y \
    ros-${ROS_DISTRO}-kobuki-* \
    ros-${ROS_DISTRO}-ecl-streams \
    ros-${ROS_DISTRO}-joy \
    ros-${ROS_DISTRO}-joint-state-publisher*

sudo cp ~/catkin_ws/src/sobit_common/turtlebot2/turtlebot_simulator/turtlebot_gazebo/libgazebo_ros_kobuki.so /opt/ros/${ROS_DISTRO}/lib

# 関係ない
sudo apt-get install -y \
    ros-${ROS_DISTRO}-pcl-* \
    ros-${ROS_DISTRO}-openni2-*


echo "╚══╣ Install: Sobit Common (FINISHED) ╠══╝"

#!/bin/bash
# 参考①：https://demikko-no-bibouroku.hatenablog.com/entry/2020/08/11/015340
# 参考②：https://qiita.com/ryu_software/items/d13a70aacfc6a71cacdb#%E3%82%A4%E3%83%B3%E3%82%B9%E3%83%88%E3%83%BC%E3%83%AB


echo "╔══╣ Install: Sobit Navigation Stack (STARTING) ╠══╗"


sudo apt-get update

# Install gmapping, amcl, move_base etc.
sudo apt-get install -y \
    ros-${ROS_DISTRO}-joy \
    ros-${ROS_DISTRO}-teleop-twist-joy \
    ros-${ROS_DISTRO}-teleop-twist-keyboard \
    ros-${ROS_DISTRO}-laser-proc \
    ros-${ROS_DISTRO}-rgbd-launch \
    ros-${ROS_DISTRO}-depthimage-to-laserscan \
    ros-${ROS_DISTRO}-rosserial-arduino \
    ros-${ROS_DISTRO}-rosserial-python \
    ros-${ROS_DISTRO}-rosserial-server \
    ros-${ROS_DISTRO}-rosserial-client \
    ros-${ROS_DISTRO}-rosserial-msgs \
    ros-${ROS_DISTRO}-amcl \
    ros-${ROS_DISTRO}-map-server \
    ros-${ROS_DISTRO}-move-base \
    ros-${ROS_DISTRO}-urdf \
    ros-${ROS_DISTRO}-xacro \
    ros-${ROS_DISTRO}-compressed-image-transport \
    ros-${ROS_DISTRO}-rqt-image-view \
    ros-${ROS_DISTRO}-gmapping \
    ros-${ROS_DISTRO}-navigation \
    ros-${ROS_DISTRO}-interactive-markers

# Install rtabmap, octomap etc.
sudo apt-get install -y \
    ros-${ROS_DISTRO}-octomap \
    ros-${ROS_DISTRO}-octomap-mapping \
    ros-${ROS_DISTRO}-octomap-rviz-plugins \
    ros-${ROS_DISTRO}-rtabmap \
    ros-${ROS_DISTRO}-rtabmap-ros \
    ros-${ROS_DISTRO}-pointcloud-to-laserscan \
    ros-${ROS_DISTRO}-ira-laser-tools


echo "╚══╣ Install: Sobit Navigation Stack (FINISHED) ╠══╝"


echo "Install Finished"
