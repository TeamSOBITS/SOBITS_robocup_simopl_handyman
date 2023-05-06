#!/usr/bin/env python
#coding:utf-8

class dict:
    def __init__(self):
        self.itos = []
        self.stoi = {}

    def create_dict(self,list):
        self.itos = list
        for i, w in enumerate(list):
            self.stoi[w] = i


#正解ラベルの辞書
verc_dict = {
    "bring":0,
    "follow":1,
    "guide":2,
    "answer":3,
    "find":4,
    "go":5,
    "ask":6,
    "else":7
}


replace_words = {
    "boy":"male",
    "boys":"male",
    "males":"male",
    "man":"male",
    "men":"male",
    "gentleman":"male",
    "gentlemen":"male",
    "girl":"female",
    "girls":"female",
    "females":"female",
    "woman":"female",
    "women":"female",
    "lady":"female",
    "ladies":"female",
    "chocoflackes":"chocoflacke"
}


replace_phrases = {
    "what's":"what is",
    "who's":"who is",
    "he's":"he is",
    "there's":"there is",
    "i'll":"i will",
    "i'd":"i would",
    "choco flacke":"chocoflacke",
    "choco flackes":"chocoflacke",
    "choco cereal":"chococereal",
    "choco cereals":"chococereal",
    "tea spoon":"teaspoon"
}


gender_dict = {
    "male":["male", "males", "boy", "boys", "man", "men", "gentleman", "gentlemen",],
    "female":["female", "females", "girl", "girls", "woman", "women", "lady", "ladies"]
    }


item_names_dict = {
    "apple":["apple"],
    "bag":["bag"],
    "banana":["banana"],
    "beer":["beer", "beers"],
    "box":["box"],
    "cereal":["cereal"],
    "chips":["chips", "potato chips"],
    "chocoflake":["chocoflake", "choco flakes", "choco cereal", "choco cereals"],
    "chocolate":["chocolate"],
    "coke":["coke", "cokes"],
    "cookies":["cookies"],
    "cup":["cup"],
    "dish":["dish", "dishes"],
    "fork":["fork"],
    "glass":["glass"],
    "key":["key"],
    "knife":["knife"],
    "melon":["melon"],
    "milk":["milk"],
    "mug":["mug"],
    "napkin":["napkin"],
    "noodles":["noodles", "noodle"],
    # "object":["object", "objects", "it", "item", "items"],
    "pasta":["pasta", "spaghetti"],
    "peach":["peach"],
    "pear":["pear"],
    "pickles":["pickles", "pickle"],
    "shampoo":["shampoo"],
    "soap":["soap"],
    "sponge":["sponge"],
    "spoon":["spoon"],
    "tea":["tea"],
    "teaspoon":["teaspoon", "tea spoon", "tea spoons", "spoon"],
    "tray":["tray"],
    "toothpaste":["toothpaste"],
    "towel":["towel"],
    "tuna":["tuna", "tuna fish"],
    "water":["water"]
}


furniture_names_dict = {
    "bar":["bar"],
    "bed":["bed"],
    "bookshelf":["bookshelf", "shelf"],
    "bowl":["bowl"],
    "cabinet":["cabinet"],
    "chair":["chair", "armchair"],
    "couch":["couch", "TV couch"],
    "counter":["counter"],
    "cupboard":["cupboard"],
    "desk":["desk"],
    "dishwasher":["dishwasher", "dish washer", "washer"],
    "drawer":["drawer", "cutlery drawer"],
    "dresser":["dresser"],
    "fireplace":["fireplace"],
    "fridge":["fridge", "freezer"],
    "microwave":["microwave"],
    "nightstand":["nightstand"],
    "shower":["shower"],
    "sink":["sink"],
    "sofa":["sofa"],
    "stove":["stove"],
    "table":["side table", "dining table", "coffee table", "center table"], # "table",
    "towel_rack":["towel rack"],
    "tub":["tub", "bathtub"],
    "washing_machine":["washing machine", "wash"]
}


room_names_dict = {
    "bathroom":["bathroom"],
    "bedroom":["bedroom"],
    "dining_room":["dining room","dining"],
    "kitchen":["kitchen"],
    "living_room":["living room", "living"]
}


result_dict = {
    "task":"<none>",
    "target":"<none>",
    "prep_T1":"<none>",
    "location_T1":"<none>",
    "prep_T2":"<none>",
    "location_T2":"<none>",
    "room_T":"<none>",
    "destination":"<none>",
    "prep_D1":"<none>",
    "location_D1":"<none>",
    "prep_D2":"<none>",
    "location_D2":"<none>",
    "room_D":"<none>",
    "WYS":"<none>",
    "FIND":"<none>",
    "obj_option":"<none>",
    "obj_num":"<none>",
    "gesture":"<none>",
    "room_F":"<none>"
}