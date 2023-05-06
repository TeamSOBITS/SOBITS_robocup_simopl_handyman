# robocup_simopl_handyman
Handymanは，[RoboCup Japan](https://www.robocup.or.jp/)@[Home League Simulation Open Platform League](https://www.robocup.or.jp/robocup-athome/s-opl/)での競技の1つです．Handyman競技とは，ロボットによる家庭内での運搬タスクの能力を評価する競技です．この競技では，ロボットが自律的に家庭内でのタスクを実行する様子を，仮想現実空間でシミュレーションして評価します．具体的には，ロボットが部屋の中を自律的に移動し，物を探して取りに行ったり，目的地に運搬したりする様子が評価されます．また，人間の命令文の間違いを指摘する能力も評価されます．Handyman競技は，家庭内でのロボットの活用に向けた技術開発を促進することを目的としています．


<details>
  <summary>※目次はこちらをクリック</summary>

  - [Environments](https://github.com/TeamSOBITS/robocup_simopl_handyman/tree/rcjp_2023#environments)
  - [Installation](https://github.com/TeamSOBITS/robocup_simopl_handyman/tree/rcjp_2023#installation)
  - [Required packages](https://github.com/TeamSOBITS/robocup_simopl_handyman/tree/rcjp_2023#required-packages)
  - [How to use](https://github.com/TeamSOBITS/robocup_simopl_handyman/tree/rcjp_2023#how-to-use)
  - [Caution](https://github.com/TeamSOBITS/robocup_simopl_handyman/tree/rcjp_2023#caution)
  - [License](https://github.com/TeamSOBITS/robocup_simopl_handyman/tree/rcjp_2023#license)

</details>

## Environments
Handymanを実行するためには，ROSの環境とSIGVerseの環境の2つの環境を整える必要があります．
- SIGVerseのバージョンやセットアップは以下のサイトを参考にしてください．
    - [SIGVerseチュートリアル（qiita）](https://qiita.com/siera_robot/items/e28d1ebc81cd26b5f237)
- ROSの環境では
    - OS : Ubuntu20.04
    - ROS version : Noetic Ninjemys
    - CUDAバージョン：11.7（現在はyolov5_rosを使用しているため）
    - Pytorch : 1.13.1


## Installation
- 関連パッケージも含めます．

```bash
# catkin_ws/srcに移動します
$ cd ~/catkin_ws/src
# 本パッケージをgit cloneします
$ git clone https://github.com/TeamSOBITS/robocup_simopl_handyman.git
# robocup_simopl_handymanに移動します
$ cd robocup_simopl_handyman
# 環境を簡単に構築するため（非公開のパッケージが含まれているため，setup.shファイルの中身にパッケージ名は自分のチームで使用している名前に変更する必要があります．）
$ bash setup.sh
# パッケージのbuildをします
$ cd ~/catkin_ws && catkin_make
```

## Required packages

### SIGVerse ROS Package
- [sigverse_ros_package (branch: master)](https://github.com/SIGVerse/sigverse_ros_package)
    - 用途：SIGVerseとROS通信を行うための共通パッケージ
    - 外部のGitHubページへ移動します．

### HSR Minimal Function
- [hsr_ros(非公開) (branch: handyman_2023)](https://github.com/TeamSOBITS/hsr_ros/tree/handyman_2023)
    - 用途：SIGVerse上でHSRを利用するための共通パッケージ
- [sobit_common(非公開)  (branch: noetic-devel)](https://github.com/TeamSOBITS/sobit_common)
    - 実際に必要なパッケージは[cv_bridge](http://wiki.ros.org/cv_bridge)，[geometry](http://wiki.ros.org/geometry)，[geometry2](http://wiki.ros.org/geometry2)，[image_geometry](http://wiki.ros.org/image_geometry)
        - cv_bridgeの用途：OpenCVとROSの間で画像データを変換するため
        - geometryの用途：ロボットの動きやセンサー情報を表現するための幾何学的なデータ構造を提供するため(ポイントクラウド，ポーズ，トランスフォーム等)
        - geometry2の用途：「geometry」の改良版
        - image_geometryの用途：カメラ画像に対するジオメトリ学的な操作を提供するため

### Navigation
- [SOBIT Navigation Stack(非公開)  (branch: main)](https://github.com/TeamSOBITS/sobit_navigation_stack)
    - 用途：自律移動用
    - [Navigation](http://wiki.ros.org/navigation)を元に作成したパッケージ
- [HSR Navigation Stack(非公開)  (branch: noetic_sigverse_2022)](https://github.com/TeamSOBITS/hsr_navigation_stack/tree/noetic_sigverse_2022)
    - 用途：HSR用にSOBIT_Navigation_Stackのパラメータを調整した自律移動用

### Robot Position Estimator
- [standing_position_estimator(非公開)  (branch: noetic_sigverse_2022)](https://github.com/TeamSOBITS/standing_position_estimator/tree/noetic_sigverse_2022)
    - 用途：ロボットの立ち位置推定
- [placeable_position_estimator(非公開)  (branch: noetic_sigverse_2022)](https://github.com/TeamSOBITS/placeable_position_estimator/tree/noetic_sigverse_2022)
    - 用途：物体を配置することが出来る家具の平面を推定
- [box_entry_gate_detection(非公開)  (branch: noetic_sigverse_2022)](https://github.com/TeamSOBITS/box_entry_gate_detection/tree/noetic_sigverse_2022)
    - 用途：ゴミ箱の投入口検出

### Object Detector
- [ssd_node(非公開)  (branch: noetic_sigverse_2022)](https://github.com/TeamSOBITS/ssd_node/tree/noetic_sigverse_2022)
    - 用途：Handymanでは，把持した物体をアバターに渡す場合，アバターを検出
    - 参考パッケージ：[ssd.pytorch](https://github.com/amdegroot/ssd.pytorch)
- [yolov5_ros(公開)  (branch: handyman_2023)](https://github.com/TeamSOBITS/yolov5_ros/tree/handyman_2023)
    - 用途：物体検出と物体認識
    - 参考パッケージ：[yolov5_ros](https://github.com/mats-robotics/yolov5_ros)


## How to use
- 2つの方法があります．
    - 方法①-Aと①-B 各launchをまとめずにそれぞれ別端末で起動する方法
    - 方法② まとめて起動する方法

### Method①
複数の端末で起動する方法

#### Method①-A
Launch order（以下のコマンドを別々の端末で起動）

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
Method①-Aを起動後，以下のlaunchを順に起動
- hsr_rosのminimal
```bash
$ roslaunch hsr_ros minimal.launch
```
- robocup_simopl_handymanのhandyman
```bash
$ roslaunch robocup_simopl_handyman handyman.launch
```

### Method②
まとめて起動する方法
```bash
$ roslaunch robocup_simopl_handyman handyman_all.launch
```

## Caution
- handyman.launchの起動後，準備完了時に端末に"Wait_command"と出るので，その後SIGVerseを起動してください．
- handyman.launchを終了する場合はSIGVerseを停止してからにしてください（逆にするとSIGVerseが再通信できるようになるまで時間がかかります）．
- 全launch起動後，handyman.launch以外のlaunchは起動しなおさなくても動作しています（練習のときとかには便利かも，**本番には非推奨**）．

## License
このウェブサイトのソースコードは，MITライセンスに基づいてライセンスされており，[LICENSE](https://github.com/TeamSOBITS/robocup_simopl_handyman/blob/rcjp_2023/LISENCE)ファイルに記載されています．