#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from __future__ import barry_as_FLUFL
import nltk
from robocup_simopl_handyman.msg import robocup_simopl_handymanCommand
from smach_files import room_data_manager, obj_data_manager, predict

nltk.download('punkt')

Location_list = ["lobby", "kitchen", "living", "bedroom"] #living_roomに関して，問題文はliving_roomではなくliving roomなのでlivingを用いて判定
Other_list = []
Object_list = []
location_tokens = []
object_tokens = []
furniture_tokens = []
msg_for_command_analyzer =[]
location_grasp_for_command_analyzer = []

kitchen_furniture = []
lobby_furniture = []
livingroom_furniture = []
bedroom_furniture = []


#文章のトークン化
def word_tokenizing(msg):
    global location_tokens, object_tokens, furniture_tokens, msg_for_command_analyzer, location_grasp_for_command_analyzer
    tokens = nltk.word_tokenize(msg)  #トークン化
    i = j = 0

    #"Go to the xxx,", "grasp the YYY", "and ZZZ"で文字列を分割
    for w in tokens:
        if tokens[i] == "Go":
            msg_for_command_analyzer = tokens[i+5:]#['Go', 'to', 'the', 'xxx', ',']この5つの要素
            location_grasp_for_command_analyzer = tokens[i+3] #xxxの部分を取り出す
        if tokens[i] == "grasp":
            location_tokens = tokens[:i]
            msg_for_command_analyzer = tokens[i:]
            j = i
        if tokens[i] == "between":
            while (tokens[i] != "and"):
                i += 1
            i += 1
        if tokens[i] == "and":
            object_tokens = tokens[j:i]
            furniture_tokens = tokens[i:]
            break
        i += 1

    return [location_tokens, object_tokens, furniture_tokens, msg_for_command_analyzer, location_grasp_for_command_analyzer]


#location_grasp抽出
def location_grasp_extraction(location_tokens):
    global Location_list
    location_grasp = []
    location_grasp = list(set(Location_list) & set(location_tokens))  #set()内のlistで重複したものを抽出(setはlistをアルファベット順にする)
    return location_grasp


#object抽出
def object_extraction(location_grasp, object_tokens):
    global Location_list, Object_list, Other_list, kitchen_furniture, lobby_furniture, livingroom_furniture, bedroom_furniture
    bedroom_furniture, kitchen_furniture, livingroom_furniture, lobby_furniture   = room_data_manager.get_furniture_name_list() #レイアウト更新時にリストも更新されるように修正
    object_target = []
    object_on = []
    object_close = []
    i = 0

    #lobby内検索
    if location_grasp[0] == Location_list[0]:
        for w in object_tokens:
            if object_tokens[i] == "the":  #'the'の次の単語とlist内の単語を比較
                if object_tokens[i + 1] in Object_list: #theの次にくる単語は名詞確定だし，sigverseの場合white_side_tableみたいに1つの単語になっている
                    object_target.append(object_tokens[i + 1])
                    if len(object_tokens) > i + 2:
                        if object_tokens[i + 2] == "on":    #object_on抽出
                            i += 3
                            print ("###########################家具###########################")
                            print (object_tokens[i+1:i+2])
                            print (lobby_furniture)
                            print ("物体が乗っている家具 :")
                            print (list(set(lobby_furniture) & set(object_tokens[i+1:i+2])))
                            print ("###########################################################")
                            ### 同じレイアウト内に複数の同じ家具がある場合の処理 ###
                            #object_on.extend(list(set(lobbyroom_furniture) & set(object_tokens[i+1:i+2])))
                            for j in range(len(object_tokens[i+1:i+2])):
                                for same_name_check in lobby_furniture:
                                    if object_tokens[i+1:i+2][j] == same_name_check or object_tokens[i+1:i+2][j] + '_' in same_name_check: #sofa, sofa_2, sofa_3は取りたいけどcorner_sofaは欲しくない
                                        object_on.append(same_name_check)
                    object_close.extend(list(set(Object_list) & set(object_tokens[i+2:])))            #object_close抽出(Object_list)
                    object_close.extend(list(set(lobby_furniture) & set(object_tokens[i+2:])))        #object_close抽出(lobby_furniture)
                    object_close.extend(list(set(Other_list) & set(object_tokens[i+2:])))             #object_close抽出(Other_list)
                    break
            i += 1
    #kitchen内検索
    elif location_grasp[0] == Location_list[1]:
        for w in object_tokens:
            if object_tokens[i] == "the":  #'the'の次の単語とlist内の単語を比較
                if object_tokens[i + 1] in Object_list:
                    object_target.append(object_tokens[i + 1])
                    if len(object_tokens) > i + 2:
                        if object_tokens[i + 2] == "on":    #object_on抽出
                            i += 3
                            print ("###########################家具###########################")
                            print (object_tokens[i+1:i+2])
                            print (kitchen_furniture)
                            print ("物体が乗っている家具 :")
                            print (list(set(kitchen_furniture) & set(object_tokens[i+1:i+2])))
                            print ("###########################################################")
                            ### 同じレイアウト内に複数の同じ家具がある場合の処理 ###
                            #object_on.extend(list(set(kitchen_furniture) & set(object_tokens[i+1:i+2])))
                            for j in range(len(object_tokens[i+1:i+2])):
                                for same_name_check in kitchen_furniture:
                                    if object_tokens[i+1:i+2][j] == same_name_check or object_tokens[i+1:i+2][j] + '_' in same_name_check: #sofa, sofa_2, sofa_3は取りたいけどcorner_sofaは欲しくない
                                        object_on.append(same_name_check)
                    object_close.extend(list(set(Object_list) & set(object_tokens[i+2:])))            #object_close抽出(Object_list)
                    object_close.extend(list(set(kitchen_furniture) & set(object_tokens[i+2:])))      #object_close抽出(kitchen_furniture)
                    object_close.extend(list(set(Other_list) & set(object_tokens[i+2:])))             #object_close抽出(Other_list)
                    break
            i += 1
    #livingroom内検索
    elif location_grasp[0] == Location_list[2]:
        for w in object_tokens:
            if object_tokens[i] == "the":  #'the'の次の単語とlist内の単語を比較
                if object_tokens[i + 1] in Object_list:
                    object_target.append(object_tokens[i + 1])
                    if len(object_tokens) > i + 2:
                        if object_tokens[i + 2] == "on":    #object_on抽出
                            i += 3
                            print ("###########################家具###########################")
                            print (object_tokens[i+1:i+2])
                            print (livingroom_furniture)
                            print ("物体が乗っている家具 :")
                            print (list(set(livingroom_furniture) & set(object_tokens[i+1:i+2])))
                            print ("###########################################################")
                            ### 同じレイアウト内に複数の同じ家具がある場合の処理 ###
                            #object_on.extend(list(set(livingroom_furniture) & set(object_tokens[i+1:i+2])))
                            for j in range(len(object_tokens[i+1:i+2])):
                                for same_name_check in livingroom_furniture:
                                    if object_tokens[i+1:i+2][j] == same_name_check or object_tokens[i+1:i+2][j] + '_' in same_name_check: #sofa, sofa_2, sofa_3は取りたいけどcorner_sofaは欲しくない
                                        object_on.append(same_name_check)
                    object_close.extend(list(set(Object_list) & set(object_tokens[i+2:])))                #object_close抽出(Object_list)
                    object_close.extend(list(set(livingroom_furniture) & set(object_tokens[i+2:])))       #object_close抽出(livingroom_furniture)
                    object_close.extend(list(set(Other_list) & set(object_tokens[i+2:])))                 #object_close抽出(Other_list)
                    break
            i += 1
    #bedroom内検索
    elif location_grasp[0] == Location_list[3]:
        for w in object_tokens:
            if object_tokens[i] == "the":  #'the'の次の単語とlist内の単語を比較
                if object_tokens[i + 1] in Object_list:
                    object_target.append(object_tokens[i + 1])
                    if len(object_tokens) > i + 2:
                        if object_tokens[i + 2] == "on":    #object_on抽出
                            i += 3
                            print ("###########################家具###########################")
                            print (object_tokens[i+1:i+2])
                            print (bedroom_furniture)
                            print ("物体が乗っている家具 :")
                            print (list(set(bedroom_furniture) & set(object_tokens[i+1:i+2])))
                            print ("###########################################################")
                            ### 同じレイアウト内に複数の同じ家具がある場合の処理 ###
                            #object_on.extend(list(set(bedroom_furniture) & set(object_tokens[i+1:i+2])))
                            for j in range(len(object_tokens[i+1:i+2])):
                                for same_name_check in bedroom_furniture:
                                    if object_tokens[i+1:i+2][j] == same_name_check or object_tokens[i+1:i+2][j] + '_' in same_name_check: #sofa, sofa_2, sofa_3は取りたいけどcorner_sofaは欲しくない
                                        object_on.append(same_name_check)

                    object_close.extend(list(set(Object_list) & set(object_tokens[i+2:])))            #object_close抽出(Object_list)
                    object_close.extend(list(set(bedroom_furniture) & set(object_tokens[i+2:])))      #object_close抽出(bedroom_furniture)
                    object_close.extend(list(set(Other_list) & set(object_tokens[i+2:])))             #object_close抽出(Other_list)
                    break
            i += 1
    else:
        object_target = ''

    return object_target, object_on, object_close


#furniture抽出
def furniture_extraction(location_grasp, furniture_tokens):
    global Location_list, kitchen_furniture, lobby_furniture, livingroom_furniture, bedroom_furniture
    exception_list = ['me', 'Moderator','here']
    furniture_target = []
    furniture_near = []
    furniture_near_lobby = []
    furniture_near_kitchen = []
    furniture_near_living = []
    furniture_near_bed = []
    location_send = []
    location_send_eval = [0, 0, 0, 0]  #location_send推定用評価変数
    max = 0
    i = 0

    for w in furniture_tokens:
        if "trash can" in furniture_tokens:
            furniture_tokens = furniture_tokens.replace("trash can", "trash_box_for_bottle_can")
        if furniture_tokens[i] == "the":  #'the'の次の単語とlist内の単語を比較
            #lobby内検索
            if furniture_tokens[i + 1] in lobby_furniture:
                location_send_eval[0] += 1
                furniture_target.append(furniture_tokens[i + 1])
                furniture_near.extend(list(set(Object_list) & set(furniture_tokens[i + 2:])))
                furniture_near_lobby = list(set(lobby_furniture) & set(furniture_tokens[i + 2:]))
            #kitchen内検索
            if furniture_tokens[i + 1] in kitchen_furniture:
                location_send_eval[1] += 1
                if len(furniture_target) == 0:
                    furniture_target = []  #list内の初期化
                    furniture_target.append(furniture_tokens[i + 1])
                if len(furniture_near) == 0:
                    furniture_near = []  #list内の初期化
                    furniture_near.extend(list(set(Object_list) & set(furniture_tokens[i + 2:])))
                furniture_near_kitchen = list(set(kitchen_furniture) & set(furniture_tokens[i + 2:]))
            #livingroom内検索
            if furniture_tokens[i + 1] in livingroom_furniture:
                location_send_eval[2] += 1
                if len(furniture_target) == 0:
                    furniture_target = []  #list内の初期化
                    furniture_target.append(furniture_tokens[i + 1])
                if len(furniture_near) == 0:
                    furniture_near.extend(list(set(Object_list) & set(furniture_tokens[i + 2:])))
                    furniture_near = []  #list内の初期化
                furniture_near_living = list(set(livingroom_furniture) & set(furniture_tokens[i + 2:]))
            #bedroom内検索
            if furniture_tokens[i + 1] in bedroom_furniture:
                location_send_eval[3] += 1
                if len(furniture_target) == 0:
                    furniture_target = []  #list内の初期化
                    furniture_target.append(furniture_tokens[i + 1])
                if len(furniture_near) == 0:
                    furniture_near = []  #list内の初期化
                    furniture_near.extend(list(set(Object_list) & set(furniture_tokens[i + 2:])))
                furniture_near_bed = list(set(bedroom_furniture) & set(furniture_tokens[i + 2:]))

            if len(furniture_target) > 0:

                if len(furniture_near_lobby) > 0:
                    location_send_eval[0] += 1
                    if furniture_near_lobby not in furniture_near:
                        furniture_near.extend(furniture_near_lobby)
                if len(furniture_near_kitchen) > 0:
                    location_send_eval[1] += 1
                    if furniture_near_kitchen not in furniture_near:
                        furniture_near.extend(furniture_near_kitchen)
                if len(furniture_near_living) > 0:
                    location_send_eval[2] += 1
                    if furniture_near_living not in furniture_near:
                        furniture_near.extend(furniture_near_living)
                if len(furniture_near_bed) > 0:
                    location_send_eval[3] += 1
                    if furniture_near_bed not in furniture_near:
                        furniture_near.extend(furniture_near_bed)

                if len(list(set(Location_list) & set(furniture_tokens[i + 2:]))) > 0:
                    location_send = list(set(Location_list) & set(furniture_tokens[i + 2:]))
                else:
                    i = 0
                    for i in range(0, 4):
                        if 0 <  location_send_eval[i]:
                            location_send.append(Location_list[i])
                        i += 1

                furniture_near.extend(list(set(Other_list) & set(furniture_tokens[i + 2:])))

                break

        i += 1

    #例外処理 "me"など
    if furniture_target == []:
        furniture_target = list(set(exception_list) & set(furniture_tokens))
        if furniture_target == []:
            furniture_target = ['']


    return furniture_target, furniture_near, location_send


# 命令文を解析する処理
def analysis_msg(msg):

    #画像認識の学習時に、rubiks_cubeの物体名で行ったため、すべてrubiks_cubeに統一
    if "rubik's_cube" in msg:
        msg = msg.replace("rubik's_cube", "rubiks_cube")

    location_tokens, object_tokens, furniture_tokens, msg_for_command_analyzer, location_grasp_for_command_analyzer = word_tokenizing(msg)
    #print(msg_for_command_analyzer) #['grasp', 'the', 'filled_plastic_bottle', 'on', 'the', 'white_side_table', 'and', 'put', 'it', 'into', 'the', 'cardboard_box', '.']
    #print(location_grasp_for_command_analyzer) #kitchen
    #print (location_tokens) #['Go', 'to', 'the', 'bedroom', ',']
    #print (object_tokens) #['grasp', 'the', 'tumbler', 'under', 'the', 'basketball_board']
    #print (furniture_tokens) #['and', 'hand', 'it', 'over', 'to', 'me', '.']
    command = []
    move_command = robocup_simopl_handymanCommand()
    grasp_command = robocup_simopl_handymanCommand()
    send_command = robocup_simopl_handymanCommand()
    location_grasp = location_grasp_extraction(location_tokens)
    move_command.command = "move"

    #ルール外の問題文が出てきたときの場合分け
    if (len(location_grasp) > 0):
        if (location_grasp[0] == Location_list[2]):
            move_command.target = location_grasp[0] + '_room'
        else:
            move_command.target = location_grasp[0]

        print ("\ncommand = %s" % move_command.command)
        print ("location_grasp = %s" % move_command.target)

        object_target, object_on, object_close = object_extraction(location_grasp, object_tokens)
        grasp_command.command = "grasp"
        if len(object_target):
            grasp_command.target = object_target[0]
        grasp_command.option1 = object_on
        grasp_command.option2 = object_close
        print ("\ncommand = %s" % grasp_command.command)
        print ("object_target = %s" % grasp_command.target)
        print ("object_on = %s" % grasp_command.option1)
        print ("object_close = %s" % grasp_command.option2) #['basketball_board', 'basketball_board']

        furniture_target, furniture_near, location_send = furniture_extraction(location_grasp, furniture_tokens)
        send_command.command = "send"
        send_command.target = furniture_target[0]

        if(len(location_send) > 0):
            for loc in location_send:
                if(loc == Location_list[2]):
                    send_command.option1.append(loc + '_room')
                else:
                    send_command.option1.append(loc)
        send_command.option2 = furniture_near
        print ("\ncommand = %s" % send_command.command)
        print ("furniture_target = %s" % send_command.target)
        print ("location_send = %s" % send_command.option1)
        print ("furniture_near = %s" % send_command.option2)
        print (bedroom_furniture)
        command.append(move_command)
        command.append(grasp_command)
        command.append(send_command)
        return command
    else:
        msg = (" ".join(msg_for_command_analyzer))
        splitted = list(map(lambda x: x.strip(' .,!?'), msg.split()))
        for w in Object_list:
            if w in splitted:
                target = w
                msg = msg.replace(w, "<item>")
        if "place" in msg:
            msg = msg.replace("place", "bring")
        if "living room" in msg:
            msg = msg.replace("living room", "living_room")
        if "hand" in msg:
            msg = msg.replace("hand", "bring")
        if "give" in msg:
            msg = msg.replace("give", "bring")
        if "send" in msg:
            msg = msg.replace("send", "being")
        if "over" in msg:
            msg = msg.replace("over", "")
        if "me" in msg:
            msg = msg.replace("me", "")

        print(msg)
        command_analyzer = predict.CommandAnalyzer()
        print("Command Analyzer")
        result = command_analyzer.predict(msg)
        print(result)
        if not result:
            return command
        for key, val in result.items():
            print(key, ":", val)
        prep_T1 = result["prep_T1"]
        location_T1 = result["location_T1"]
        room_T = location_grasp_for_command_analyzer
        destination = result["destination"]
        if "me" in msg:
            location_D1 = "me"
        else:
            location_D1 = result["location_D1"]
        location_D2 = result["location_D2"]
        room_D = result["room_D"]
        move_command.target = room_T

        if not destination == "place":
            location_D1 ="me"

        print ("\ncommand = %s" % move_command.command)
        print ("location_grasp = %s" % move_command.target)

        grasp_command.command = "grasp"
        if len(target):
            grasp_command.target = target
        if prep_T1 == "on":
            grasp_command.option1 = location_T1
        elif prep_T1 =="under":
            grasp_command.option2 = location_T1
        print ("\ncommand = %s" % grasp_command.command)
        print ("object_target = %s" % grasp_command.target)
        print ("object_on = %s" % grasp_command.option1)
        print ("object_close = %s" % grasp_command.option2)

        send_command.command = "send"
        send_command.target = location_D1
        send_command.option1 = room_D
        send_command.option2 = location_D2

        print ("\ncommand = %s" % send_command.command)
        print ("furniture_target = %s" % send_command.target)
        print ("location_send = %s" % send_command.option1)
        print ("furniture_near = %s" % send_command.option2)
        print (bedroom_furniture)
        command.append(move_command)
        command.append(grasp_command)
        command.append(send_command)
        return command


# 把持できる物体を読み込み
def set_graspable_obj_list(data):
    global Object_list
    Object_list = data


# 把持不可能な物体を読み込み
def set_non_graspable_obj_list(data):
    global Other_list
    Other_list = data


# 家具を読み込み
def set_furniture_name_list(bedroom_furniture_list_, kitchen_furniture_list_, livingroom_furniture_list_, lobby_furniture_list_):
    global bedroom_furniture, kitchen_furniture, livingroom_furniture, lobby_furniture
    bedroom_furniture = bedroom_furniture_list_
    kitchen_furniture = kitchen_furniture_list_
    livingroom_furniture = livingroom_furniture_list_
    lobby_furniture = lobby_furniture_list_
    print('bedroom_furniture')
    print(bedroom_furniture)
    print('livingroom_furniture')
    print(livingroom_furniture)
    print('kitchen_furniture')
    print(kitchen_furniture)
    print('lobby_furniture')
    print(lobby_furniture)


# この部分は「$ python message_analysis.py」の時には実行される
if __name__ == "__main__":
    room_data_manager.launch_slam("Layout2019HM01")
    a, b, c, d = room_data_manager.get_furniture_name_list()
    set_furniture_name_list(a, b, c, d)
    obj_data_manager.read_non_graspable_obj_list()
    obj_data_manager.read_graspable_obj_list()
    set_graspable_obj_list(obj_data_manager.get_graspable_obj_list())
    set_non_graspable_obj_list(obj_data_manager.get_non_graspable_obj_list())

    analysis_msg('Go to the bedroom, grasp the white_cup on the white_side_table and put it on the wooden_side_table in the kitchen.')