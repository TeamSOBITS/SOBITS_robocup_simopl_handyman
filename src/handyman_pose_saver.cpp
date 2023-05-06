#include "ros/ros.h"
#include "geometry_msgs/Pose.h"
#include <stdio.h>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <map>
#include <cctype>

#include <termios.h>
#include <unistd.h>
#include <fcntl.h>
#include <tf2_msgs/TFMessage.h>
#include <nav_msgs/Odometry.h>
#include <tf/transform_listener.h>
#include <sys/types.h>
#include <stdlib.h>
#include <ros/package.h>

#include <time.h>
#include <sstream>
#include <stdlib.h>

using namespace std;

//グローバル変数
string unknown_obj_name;

int room_num;
int name_check_num;
int save_count;

bool first_flag;
bool finish_flag;
bool name_true_flag;

vector<string> sharp_vec;
vector<string> furniture_count_num_vec;

vector<bool> unknown_obj_flag_vec;

vector<int> furniture_num_vec;
vector<int> room_num_vec;

vector<float> translation_x;
vector<float> translation_y;
vector<float> translation_z;

vector<float> rotation_x;
vector<float> rotation_y;
vector<float> rotation_z;
vector<float> rotation_w;

vector<double> furniture_stage_vec;

vector<string> unknown_obj_name_vec;

class pose_keep{

public:

    pose_keep(){

    // 座標登録のファイル保存のパス
    std::string save_location_folder_path;// 保存席　hsr_ros/map
    ros::param::get( "save_location_folder_path", save_location_folder_path );

    // 現在時間
		time_t now = time(NULL);
    struct tm *pnow = localtime(&now);

    // 保存するファイル名
	  file_name << save_location_folder_path << "/saved_location_"<< pnow->tm_mon + 1 <<"_"<< pnow->tm_mday <<"_"<< pnow->tm_hour <<"_"<< pnow->tm_min <<".yaml";
    std::cout << "file_name : " << file_name.str() << std::endl;

    // 部屋の候補
    room_candidate[0] = "";
    room_candidate[1] = "kitchen";
    room_candidate[2] = "bed room";
    room_candidate[3] = "lobby";
    room_candidate[4] = "living_room";

    // 家具の候補と家具の高さ
    furniture_candidate[0] = "";
    furniture_candidate[1] = "armchair";
    furniture_candidate[2] = "cardboard_box@";
    furniture_candidate[3] = "corner_sofa";
    furniture_candidate[4] = "dining_table";
    furniture_candidate[5] = "iron_bed";
    furniture_candidate[6] = "round_low_table";
    furniture_candidate[7] = "square_low_table";
    furniture_candidate[8] = "trash_box_for_bottle_can@";
    furniture_candidate[9] = "trash_box_for_burnable@";
    furniture_candidate[10] = "trash_box_for_recycle@";
    furniture_candidate[11] = "wagon";
    furniture_candidate[12] = "white_side_table";
    furniture_candidate[13] = "wooden_bed";
    furniture_candidate[14] = "wooden_shelf";
    furniture_candidate[15] = "wooden_side_table";
    furniture_candidate[16] = "blue_cupboard";
    furniture_candidate[17] = "changing_table";
    furniture_candidate[18] = "custom_kitchen";
    furniture_candidate[19] = "sofa";
    furniture_candidate[20] = "white_rack";
    furniture_candidate[21] = "white_chair";
    furniture_candidate[22] = "white_round_table";
    furniture_candidate[23] = "white_shelf";
    furniture_candidate[24] = "wide_shelf";
    furniture_candidate[25] = "wooden_cupboard";
    furniture_candidate[26] = "--未知物体に名前をつける--";

    // 登録回数
    save_count = 0;
    furniture_count = 0;

    // 家具の名前を登録しないフラグと仮の値の配列番号
    no_furniture_num = 0;

    //フラグ
    first_flag = false;
    finish_flag = false;
    name_true_flag = false;

    Pose_save();


    }
	~pose_keep(){}

  // 座標取得の関数
	void get_pose()
	{
		//tfで変換
		tf::StampedTransform transform;

    listener.waitForTransform("/map","/base_footprint",ros::Time(0),ros::Duration(3.0));
		listener.lookupTransform("/map","/base_footprint",ros::Time(0),transform);

    // 座標保存
		translation_x.push_back(transform.getOrigin().x() );
		translation_y.push_back(transform.getOrigin().y() );
		translation_z.push_back(transform.getOrigin().z() );

		rotation_x.push_back(transform.getRotation().x() );
		rotation_y.push_back(transform.getRotation().y() );
		rotation_z.push_back(transform.getRotation().z() );
		rotation_w.push_back(transform.getRotation().w() );

  }//callback



  void Pose_save()
  {
    sleep(5.0f);//tfのlistenerのために待つ

    while(finish_flag==false)
    {
      Room_choose();
      Furniturek_choose();
      Confirm_selected_content();
      Recording_continue();
    }
    std::cout<<"||||||||||||||||||||   FINISH  ||||||||||||||||||||||||||\n\n\n"<<std::endl;
  }//Pose_save



  void Room_choose()
  {
    /* ② 部屋の名前選択 */
    std::cout << "\n\n\n   ================================================"<< std::endl;
    std::cout << "   ||     ① 部屋の名前番号を選択して下さい。     ||" << std::endl;
    std::cout << "   ================================================"<< std::endl;
    for(auto room_itr = room_candidate.begin(); room_itr != room_candidate.end(); ++room_itr) {
      if(room_itr->first == 0){continue;}
      std::cout << "番号 = " << room_itr->first << ", 部屋の名前 = " << room_itr->second << "\n";    // 値を表示
      max_room_num = room_itr->first;
    }
    while(true){
      std::cout << "==▶ ";
      for ( cin >> room_num ; !cin ; cin >> room_num){
               cin.clear();
               cin.ignore();
               cout << "\n ① 押すキーが違います。　再度キーを入力し直して下さい。";
      }//for
      if(room_num>max_room_num || room_num == 0){
        std::cout << "\n ① 押されたキーの番号は部屋の候補にありません。　再度キーを入力し直して下さい。"<< std::endl;
      }
      else{
        std::cout << "   /////////////////////////////////////////////////"<< std::endl;
        std::cout << "   ////  [ " << room_num << " ] の 「 " << room_candidate[room_num] << " 」を選択完了。  ////" << std::endl;
        std::cout << "   /////////////////////////////////////////////////\n\n"<< std::endl;
        room_num_vec.push_back(room_num);
        break;
      }//else
    }//while

    return;
  }//Room_choose



  void Furniturek_choose()
  {
    /* ② 家具の名前選択 */
    std::cout << "\n\n\n   =========================================="<< std::endl;
    std::cout << "   ||     ② 家具の名前を登録しますか？     ||" << std::endl;
    std::cout << "   =========================================="<< std::endl;

    std::cout << "はい -> 「1」を押す/ いいえ -> 「2」を押す" << std::endl;
    while(true){
      std::cout << "==▶ ";
      for ( cin >> furniture_rec ; !cin ; cin >> furniture_rec){
               cin.clear();
               cin.ignore();
               cout << "\n ② 押すキーが違います。　再度キーを入力し直して下さい。";
      }//for
      if(furniture_rec==1){
        std::cout << "〜家具の名前番号を選択して下さい〜" << std::endl;
        for(auto furniture_itr = furniture_candidate.begin(); furniture_itr != furniture_candidate.end(); ++furniture_itr) {
          if (furniture_itr->first == 0){continue;}
          std::cout << "番号 = " << furniture_itr->first << ", 家具の名前 = " << furniture_itr->second << "\n";    // 値を表示
          max_furniture_num = furniture_itr->first;
        }//for
        while(true){
          std::cout << "==▶ ";
          for ( cin >> furniture_num ; !cin ; cin >> furniture_num){
                   cin.clear();
                   cin.ignore();
                   cout << "\n ② 押すキーが違います。　再度キーを入力し直して下さい。";
          }//for
          if(furniture_num>max_furniture_num || furniture_num == 0){
            std::cout << " ② 押されたキーの番号は家具の候補にありません。　再度キーを入力し直して下さい。\n"<< std::endl;
          }//if
          else{
            if(furniture_candidate[furniture_num]=="--未知物体に名前をつける--"){
              std::cout << " [ 名前を入力して下さい。 ]\n"<< std::endl;
              while(true){
                std::cout << "==▶ ";
                for ( cin >> unknown_obj_name ; !cin ; cin >> unknown_obj_name){
                         cin.clear();
                         cin.ignore();
                         cout << "\n ② 押すキーが違います。　再度キーを入力し直して下さい。";
                }//for
                std::cout << "\n\n\n  未知物体の名前は [ " << unknown_obj_name << " ] でよろしですか？ \n"<< std::endl;
                std::cout << "はい -> 「1」を押す/ いいえ -> 「2」を押す"<< std::endl;
                while(true){
                  for ( cin >> name_check_num ; !cin ; cin >> name_check_num){
                           cin.clear();
                           cin.ignore();
                           cout << "\n ② 押すキーが違います。　再度キーを入力し直して下さい。";
                  }//for
                  if(name_check_num==1){
                    unknown_obj_name_vec.push_back(unknown_obj_name);
                    name_true_flag = true;
                    break;
                  }//if
                  else if(name_check_num==2){
                    // 選択した内容の削除
                    unknown_obj_name = "";
                    break;
                  }//else if
                  else{
                    std::cout << "\n ② 押すキーが違います。　再度キーを入力し直して下さい。"<< std::endl;
                  }//else
                }//while
                if(name_true_flag==false){
                  std::cout << " 再度 →　[ 名前を入力して下さい。 ]\n"<< std::endl;
                }//if
                else{
                  std::cout << "             選択した内容を保存しました。\n"<< std::endl;
                  //初期化
                  name_true_flag = false;
                  break;
                }
              }//while
              unknown_obj_flag_vec.push_back(true);
              furniture_num_vec.push_back(0);
              furniture_count_num_vec.push_back("");
            }//if
            else{
              unknown_obj_flag_vec.push_back(false);
              furniture_num_vec.push_back(furniture_num);
              std::cout << "   /////////////////////////////////////////////////////////"<< std::endl;
              std::cout << "   ////////  [ " << furniture_num << " ] の 「 " << furniture_candidate[furniture_num] << " 」を選択完了。  ////////" << std::endl;
              std::cout << "   /////////////////////////////////////////////////////////\n\n"<< std::endl;

              // 同じ部屋に同じ家具が何回登録されたか、配列番号で確認
              room_num_vec_size = room_num_vec.size();
              for(int i=0;i<room_num_vec_size;i++){
                if(room_num_vec[i] == room_num_vec[room_num_vec_size-1]){
                  some_room_num_vec.push_back(i);
                }//if
              }//for

              if(false == some_room_num_vec.empty()){
                furniture_num_vec_size = furniture_num_vec.size();
                for(int j=0;j<some_room_num_vec.size();j++){
                  if(furniture_num_vec[some_room_num_vec[j]] == furniture_num_vec[furniture_num_vec_size-1]){
                    furniture_count+=1;
                  }//if
                }//for
                //初期化
                some_room_num_vec.clear();
              }//if

              if(furniture_count>1){//2個以上登録されたか判定
                ostringstream oss;
                oss << "_" << furniture_count;
                furniture_count_num_vec.push_back(oss.str().c_str());
              }//if
              else{
                furniture_count_num_vec.push_back("");
              }//else
              furniture_count=0;//初期化
              unknown_obj_name_vec.push_back("");
            }//else
            sharp_vec.push_back("#");
            break;
          }//else
        }//while
        break;
      }//if
      else if(furniture_rec==2){
        std::cout << "   //////////////////////////////////////////////////////"<< std::endl;
        std::cout << "   ////////  家具の名前を登録しません。  ////////"<< std::endl;
        std::cout << "   //////////////////////////////////////////////////////\n\n"<< std::endl;
        sharp_vec.push_back("");
        furniture_num_vec.push_back(no_furniture_num);
        furniture_count_num_vec.push_back("");
        unknown_obj_flag_vec.push_back(false);
        unknown_obj_name_vec.push_back("");
        break;
      }//else if
      else{
        std::cout << "\n ② 押すキーが違います。　再度キーを入力し直して下さい。"<< std::endl;
      }//else
    }//while

    return;
  }//Furniturek_choose

  void Confirm_selected_content()
  {
    /* ③ 選択した内容の確認 */
    std::cout << "\n\n\n   ============================================================================="<< std::endl;
    std::cout << "   ||     ③ 選択した内容は以下でよろしいですか? よろしければ保存します。     ||" << std::endl;
    std::cout << "   =============================================================================\n"<< std::endl;
    if(unknown_obj_flag_vec[save_count]==true){
      std::cout << "             選択内容: [ " << room_candidate[room_num_vec[save_count]] << sharp_vec[save_count] << furniture_candidate[furniture_num_vec[save_count]] << unknown_obj_name_vec[save_count] << " ]\n" << std::endl;
    }
    else{
      std::cout << "             選択内容: [ " << room_candidate[room_num_vec[save_count]] << sharp_vec[save_count] << furniture_candidate[furniture_num_vec[save_count]] << furniture_count_num_vec[save_count] << " ]\n" << std::endl;
    }
    std::cout << "はい -> 「1」を押す/ いいえ -> 「2」を押す"<< std::endl;
    while(true){
      std::cout << "==▶ ";
      for ( cin >> check_num ; !cin ; cin >> check_num){
               cin.clear();
               cin.ignore();
               cout << "\n ③ 押すキーが違います。　再度キーを入力し直して下さい。";
      }//for
      if(check_num==1){
        std::cout << "             選択した内容を保存します。\n"<< std::endl;
        save_count ++;
        //座標登録
        get_pose();
        break;
      }//if
      else if(check_num==2){
        std::cout << "             内容を再度選択し直してください。\n"<< std::endl;
        // 選択した内容の削除
        std::cout << "-------デバック 1 ---------"<< std::endl;
        sharp_vec.pop_back();
        std::cout << "-------デバック 2 ---------"<< std::endl;
        room_num_vec.pop_back();
        std::cout << "-------デバック 3 ---------"<< std::endl;
        furniture_num_vec.pop_back();
        std::cout << "-------デバック 4 ---------"<< std::endl;
        furniture_count_num_vec.pop_back();
        std::cout << "-------デバック 5 ---------"<< std::endl;
        unknown_obj_flag_vec.pop_back();
        std::cout << "-------デバック 6 ---------"<< std::endl;
        break;
      }//else if
      else{
        std::cout << "\n ③ 押すキーが違います。　再度キーを入力し直して下さい。"<< std::endl;
      }//else
    }//while
    return;
  }//Confirm_selected_content

  void Recording_continue()
  {
    /* ④ 記録を続けるか判定 */

    std::cout<< "\n<<<<<<<<<< 現在、" << save_count << "箇所の座標を登録しています。 >>>>>>>>>>>>>>"<<std::endl;
    std::cout<< "\n\n\n [確認 " << " sharp_vec: " << sharp_vec.size() << " save_count: " << save_count  << "]" << std::endl;

    std::cout << "\n\n\n   =============================================="<< std::endl;
    std::cout << "   ||     ④ 記録を続けるか選択して下さい。     ||" << std::endl;
    std::cout << "   =============================================="<< std::endl;
    std::cout << "続ける -> 「1」を押す/ 終了する -> 「2」を押す"<< std::endl;
    while(true){
      std::cout << "==▶ ";
      for ( cin >> contenue_num ; !cin ; cin >> contenue_num){
               cin.clear();
               cin.ignore();
               cout << "\n ④ 押すキーが違います。　再度キーを入力し直して下さい。";
      }//for
      if(contenue_num==1){
        std::cout << "\n\n\n   --------------　記録を続けます⏬　--------------\n"<< std::endl;
        return;
      }//if
      else if(contenue_num==2){
        while(true){
          ofstream ofs(file_name.str().c_str());
          if(ofs)
          {
            for(int k=0;k<save_count;k++)
            {
              if(unknown_obj_flag_vec[k]==true){
                ofs << std::endl;
                ofs << "# " << room_candidate[room_num_vec[k]] << sharp_vec[k] << furniture_candidate[furniture_num_vec[k]] << unknown_obj_name_vec[k] << " #" << std::endl;
                ofs << std::endl;
                ofs << room_candidate[room_num_vec[k]] << sharp_vec[k] << furniture_candidate[furniture_num_vec[k]] << unknown_obj_name_vec[k] << "_translation_x: " << translation_x[k] << std::endl;
                ofs << room_candidate[room_num_vec[k]] << sharp_vec[k] << furniture_candidate[furniture_num_vec[k]] << unknown_obj_name_vec[k] << "_translation_y: " << translation_y[k] << std::endl;
                ofs << room_candidate[room_num_vec[k]] << sharp_vec[k] << furniture_candidate[furniture_num_vec[k]] << unknown_obj_name_vec[k] << "_translation_z: " << translation_z[k] << std::endl;
                ofs << std::endl;
                ofs << room_candidate[room_num_vec[k]] << sharp_vec[k] << furniture_candidate[furniture_num_vec[k]] << unknown_obj_name_vec[k] << "_rotation_x: " << rotation_x[k] << std::endl;
                ofs << room_candidate[room_num_vec[k]] << sharp_vec[k] << furniture_candidate[furniture_num_vec[k]] << unknown_obj_name_vec[k] << "_rotation_y: " << rotation_y[k] << std::endl;
                ofs << room_candidate[room_num_vec[k]] << sharp_vec[k] << furniture_candidate[furniture_num_vec[k]] << unknown_obj_name_vec[k] << "_rotation_z: " << rotation_z[k] << std::endl;
                ofs << room_candidate[room_num_vec[k]] << sharp_vec[k] << furniture_candidate[furniture_num_vec[k]] << unknown_obj_name_vec[k] << "_rotation_w: " << rotation_w[k] << std::endl;
                ofs << std::endl;
                ofs << "\n#======================================#" << std::endl;
              }//if
              else{
                ofs << std::endl;
                ofs << "# " << room_candidate[room_num_vec[k]] << sharp_vec[k] << furniture_candidate[furniture_num_vec[k]] << furniture_count_num_vec[k] << " #" << std::endl;
                ofs << std::endl;
                ofs << room_candidate[room_num_vec[k]] << sharp_vec[k] << furniture_candidate[furniture_num_vec[k]] << furniture_count_num_vec[k] << "_translation_x: " << translation_x[k] << std::endl;
                ofs << room_candidate[room_num_vec[k]] << sharp_vec[k] << furniture_candidate[furniture_num_vec[k]] << furniture_count_num_vec[k] << "_translation_y: " << translation_y[k] << std::endl;
                ofs << room_candidate[room_num_vec[k]] << sharp_vec[k] << furniture_candidate[furniture_num_vec[k]] << furniture_count_num_vec[k] << "_translation_z: " << translation_z[k] << std::endl;
                ofs << std::endl;
                ofs << room_candidate[room_num_vec[k]] << sharp_vec[k] << furniture_candidate[furniture_num_vec[k]] << furniture_count_num_vec[k] << "_rotation_x: " << rotation_x[k] << std::endl;
                ofs << room_candidate[room_num_vec[k]] << sharp_vec[k] << furniture_candidate[furniture_num_vec[k]] << furniture_count_num_vec[k] << "_rotation_y: " << rotation_y[k] << std::endl;
                ofs << room_candidate[room_num_vec[k]] << sharp_vec[k] << furniture_candidate[furniture_num_vec[k]] << furniture_count_num_vec[k] << "_rotation_z: " << rotation_z[k] << std::endl;
                ofs << room_candidate[room_num_vec[k]] << sharp_vec[k] << furniture_candidate[furniture_num_vec[k]] << furniture_count_num_vec[k] << "_rotation_w: " << rotation_w[k] << std::endl;
                ofs << std::endl;
                ofs << "\n#======================================#" << std::endl;
              }//else
            }//for
            //ファイルを閉じる
            ofs.close();
            std::cout<< "\n\n「　" << file_name.str() << "　」として保存完了。" <<std::endl;
            std::cout<< "\n<<<<<<<<<< 合計で" << save_count << "箇所の座標を登録しました。 >>>>>>>>>>>>>>"<<std::endl;
            std::cout<< "\n\n 最終確認 " << " sharp_vec: " << sharp_vec.size() << " save_count: " << save_count << std::endl;
            std::cout<<"\n以上で終了です。\n"<<std::endl;
            finish_flag = true;
            break;
          }//if
          else{
            // 保存するファイルが開けなかった場合
            std::cout<< "危険!!: " <<std::endl;
            std::cout<< "このままでは " << file_name.str() << "　を作成できません。" <<std::endl;
            std::cout<< "ファイルを保存するパス名を確認してください。" <<std::endl;
            break;
          }//else
        }//while
        break;
      }//else if
      else{
        std::cout << " ④ 押されたキーが違います。　再度キーを入力し直して下さい。\n"<< std::endl;
      }//else
    }//while
  }//Recording_continue



private:
 	ros::NodeHandle nh;

	stringstream file_name;

  tf::TransformListener listener;

  int at_num;
  int furniture_rec;
  int furniture_num;
  int furniture_h_num;
  int contenue_num;
  int furniture_stage_num;
  int max_furniture_num;
  int max_room_num;
  int check_num;
  int no_furniture_num;
  int furniture_num_vec_size;
  int room_num_vec_size;
  int furniture_count;

  vector<int> some_room_num_vec;

  map<int, string> furniture_candidate;
  map<int, string> room_candidate;

};//pose_keep




int main(int argc, char **argv)
{
  ros::init(argc, argv, "handyman_pose_saver");

  std::cout<<"\n         Handyman 部屋と家具の名前・座標の登録開始"<<std::endl;

	pose_keep pk;//上の関数を実行

	ros::spin();

	return 0;
}
