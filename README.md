# robocup_simopl_handyman
Handyman is one of the competitions in [RoboCup Japan](https://www.robocup.or.jp/)@[Home League Simulation Open Platform League](https://www.robocup.or.jp/robocup-athome/s-opl/). The Handyman competition evaluates the ability of robots to perform transportation tasks within a household setting. In this competition, the robot's autonomous execution of tasks within a domestic environment is evaluated through simulation in a virtual reality space. Specifically, the competition assesses the robot's ability to autonomously navigate within a room, locate and retrieve objects, and transport them to designated destinations. The robot's capability to identify errors in human instructions is also evaluated. The Handyman competition aims to promote technological development for the utilization of robots in domestic settings.

<details>
  <summary>※Click here for outline</summary>

  - [Environments](https://github.com/TeamSOBITS/robocup_simopl_handyman/tree/rcjp_2023#environments)
  - [Installation](https://github.com/TeamSOBITS/robocup_simopl_handyman/tree/rcjp_2023#installation)
  - [Required packages](https://github.com/TeamSOBITS/robocup_simopl_handyman/tree/rcjp_2023#required-packages)
  - [How to use](https://github.com/TeamSOBITS/robocup_simopl_handyman/tree/rcjp_2023#how-to-use)
  - [Caution](https://github.com/TeamSOBITS/robocup_simopl_handyman/tree/rcjp_2023#caution)
  - [License](https://github.com/TeamSOBITS/robocup_simopl_handyman/tree/rcjp_2023#license)

</details>

## Environments
For the implementation of Handyman, it is necessary to set up two environments: the ROS environment and the SIGVerse environment.
- Please refer to the following website for information on the version and setup of SIGVerse.
    - [SIGVerse Tutorial](http://www.sigverse.org/wiki/en/index.php?Installation#t38cb130)
- ROS Environment
    - OS : Ubuntu20.04
    - ROS version : Noetic Ninjemys
    - CUDAバージョン：11.7（Reason: yolov5_ros will be used in this package）
    - Pytorch : 1.13.1


## Installation
- Other relevant packages are being used．

```bash
# Move to catkin_ws/src
$ cd ~/catkin_ws/src
# Clone this package from github
$ git clone https://github.com/TeamSOBITS/robocup_simopl_handyman.git
# Move to robocup_simopl_handyman
$ cd robocup_simopl_handyman
# To simplify the environment setup (as it includes private packages, it is necessary to modify the package names within the setup.sh file to the names used by your team.)
$ bash setup.sh
# Build this package
$ cd ~/catkin_ws && catkin_make
```

## Required packages

### SIGVerse ROS Package
- [sigverse_ros_package(Public) (branch: master)](https://github.com/SIGVerse/sigverse_ros_package)
    - Purpose: A common package for communication between SIGVerse and ROS.
    - Please refer to the external GitHub page for more details.

### HSR Minimal Function
- [SOBITS_hsr_commmon_sim(Public) (branch: noetic-devel)](https://github.com/TeamSOBITS/SOBITS_hsr_common_sim)
    - Purpose: A common package for utilizing HSR on SIGVerse.
- [sobit_common(Private) (branch: noetic-devel)](https://github.com/TeamSOBITS/sobit_common)
    - The required packages include [cv_bridge](http://wiki.ros.org/cv_bridge)，[geometry](http://wiki.ros.org/geometry)，[geometry2](http://wiki.ros.org/geometry2)，[image_geometry](http://wiki.ros.org/image_geometry)
        - Purpose of cv_bridge: To facilitate the conversion of image data between OpenCV and ROS
        - Purpose of geometry: To provide geometric data structures for representing robot movements and sensor information (such as point clouds, poses, and transformations)
        - Purpose of geometry2: An improved version of the「geometry」package
        - Purpose of image_geometry: To provide geometric operations for camera images

### Navigation
- [SOBIT Navigation Stack(Private) (branch: main)](https://github.com/TeamSOBITS/sobit_navigation_stack)
    - Purpose:Autonomous movement
    - The package was created based on [Navigation](http://wiki.ros.org/navigation).
- [HSR Navigation Stack(Private) (branch: noetic_sigverse_2022)](https://github.com/TeamSOBITS/hsr_navigation_stack/tree/noetic_sigverse_2022)
    - Purpose:An autonomous navigation package customized for HSR by adjusting the parameters of the SOBIT_Navigation_Stack

### Robot Position Estimator
- [standing_position_estimator(Private) (branch: noetic_sigverse_2022)](https://github.com/TeamSOBITS/standing_position_estimator/tree/noetic_sigverse_2022)
    - Purpose:Estimation of the robot's standing position
- [placeable_position_estimator(Private) (branch: noetic_sigverse_2022)](https://github.com/TeamSOBITS/placeable_position_estimator/tree/noetic_sigverse_2022)
    - Purpose:Detection of the placeable furniture surface
- [box_entry_gate_detection(Private) (branch: noetic_sigverse_2022)](https://github.com/TeamSOBITS/box_entry_gate_detection/tree/noetic_sigverse_2022)
    - Purpose:Detection of the trash bin's entry point

### Object Detector
- [ssd_node(Private) (branch: noetic_sigverse_2022)](https://github.com/TeamSOBITS/ssd_node/tree/noetic_sigverse_2022)
    - Purpose:In Handyman, when transferring a grasped object to an avatar, the detection of the avatar is required
    - Reference package:[ssd.pytorch](https://github.com/amdegroot/ssd.pytorch)

- [yolov5_ros(Public) (branch: handyman_2023)](https://github.com/TeamSOBITS/yolov5_ros/tree/handyman_2023)
    - Purpose:Detection and recognition of object
    - Reference package:[yolov5_ros](https://github.com/mats-robotics/yolov5_ros)


## How to use
- There are two methods available.
  - Method ①: Launching ①-A and ①-B separately on different terminals without combining them
  - Method ②: Launching them together as a combined process

### Method①
To launch multiple terminals, follow these steps

#### Method①-A
Launch order(launch the following commands on separate terminals)
- yolov5_ros
```bash
$ roslaunch yolov5_ros yolov5_with_tf.launch
```
- placeable_position_estimator
```bash
$ roslaunch placeable_position_estimator placeable_position_estimator_hsr.launch
```
- box_entry_gate_detection
```bash
$ roslaunch box_entry_gate_detection box_detection.launch
```
- ssd_node
```bash
$ roslaunch ssd_node object_detect_with_tf_wrs.launch
```
- hsr_ros
```bash
$ rosrun hsr_ros sub_obj_depth
```

#### Method①-B
After launching Method①-A, launch the following launch files in sequence separately
- hsr_rosのminimal
```bash
$ roslaunch hsr_ros minimal.launch
```
- robocup_simopl_handymanのhandyman
```bash
$ roslaunch robocup_simopl_handyman handyman.launch
```

### Method②
Launch everything in one command
```bash
$ roslaunch robocup_simopl_handyman handyman_all.launch
```

## Caution
- This package is intended for public use. Each team should clone the Git repository and rename the package to "robocup_simopl_handyman" for their own usage.
- After launching handyman.launch, you will see "Wait_command" in the terminal. Please start SIGVerse after seeing this message.
- When you want to end handyman.launch, please stop SIGVerse first before terminating the launch file. (If you do it in reverse, it may take some time for SIGVerse to establish communication in the next launching.)
- Once all the launches are started, you don't need to restart the launches other than handyman.launch. They will continue to function without restarting (this can be convenient for practice sessions, but it is **not recommended for competition**).

## License
The source code of this website is licensed under the MIT License, and the details can be found in the [LICENSE](https://github.com/TeamSOBITS/robocup_simopl_handyman/blob/rcjo2023/LISENCE) file.
