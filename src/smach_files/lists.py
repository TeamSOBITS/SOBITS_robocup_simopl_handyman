#!/usr/bin/env python
#coding:utf-8

#正解ラベルのリスト
remove_words = [
    "please",
    "Please",
   ",",
    ".",
    "?",
    "\t",
    "\n"
]

verb_list = [
    "go",
    "bring",
    "follow",
    "guide",
    "find",
    "ask",
    "answer",
    "else"
]

prep_list = [
    "in",
    "on",
    "under",
    "above",
    "into",
    "out",
    "right",
    "left",
    "top",
    "behind",
    "near", # next
    "at"
]

person_names = [
    "operator",
    "Alex",
    "Hayden",
    "Jamie",
    "Jordan",
    "Michael",
    "Morgan",
    "Peyton",
    "Robin",
    "Taylor",
    "Tracy",
    "person"
]

gender = [
    "male",
    "males",
    "boy",
    "boys",
    "man",
    "men",
    "gentleman",
    "gentlemen",
    "female",
    "females",
    "girl",
    "girls",
    "woman",
    "women",
    "lady",
    "ladies"
    ]

item_names = [
    "apple",
    "bag",
    "banana",
    "beer", #"beers",
    "box",
    "cereal",
    "chips", #"potato chips",
    "chocoflake", #"choco flakes", "choco cereal", "choco cereals",
    "chocolate",
    "coke", #"cokes",
    "cookies",
    "cup",
    "dish", #"dishes",
    "fork",
    "glass",
    "it",
    "key",
    "knife",
    "melon",
    "milk",
    "mug",
    "napkin",
    "noodles", #"noodle",
    "object", #"objects", "item", "items",
    "pasta", #"spaghetti",
    "peach",
    "pear",
    "pickles", #"pickle",
    "shampoo",
    "soap",
    "sponge",
    "spoon",
    "tea",
    "teaspoon", #"tea spoon", "tea spoons", "spoon",
    "tray",
    "toothpaste",
    "towel",
    "tuna", #"tuna fish",
    "water"
]

furniture_names = [
    "bar",
    "bed",
    "bookshelf", #"shelf",
    "bowl",
    "cabinet",
    "chair", #"armchair",
    "couch", #"TV couch",
    "counter",
    "cupboard",
    "desk",
    "dishwasher", #"dish washer", "washer",
    "drawer", #"cutlery drawer",
    "dresser",
    "fireplace",
    "fridge", #"freezer",
    "microwave",
    "nightstand",
    "shower",
    "sink",
    "sofa",
    "stove",
    "table", #"side table", "dining table", "coffee table", "center table",
    "towel_rack",
    "tub", #"bathtub",
    "washing_machine"
]

room_names = [
    "bathroom",
    "bedroom",
    "dining_room",
    "kitchen",
    "living_room"
]

location_names = [
    "bar",
    "corridor", #"CORRIDOR",
    "entrance",
    "hallway",
    "toilet",
    "wardrobe"
]

category_list = [
    "task",
    "target",
    "prep_T",
    "location_T",
    "room_T",
    "destination",
    "prep_D",
    "location_D",
    "room_D",
    "WYS",
    "FIND",
    "obj_option",
    "obj_num",
    "gesture",
    "room_F"
]

what_you_say = [
    "name",
    "yourself",
    "country",
    "affiliation",
    "joke",
    "time",
    "date",
    "day_of_week"
]
find_type = [
    "name",
    "count",
    "gender",
    "where",
    "gesture"
]
superlatives = [
    "largest", #"biggest"
    "smallest", #"littlest"
    "heaviest",
    "lightest",
    "thinnest", #"flimsiest", "skinniest", "narrowest"
    "most"
]

quantity = [
    "2",
    "3"
]

gestures = [
    "waving",
    "rising_left_arm",
    "rising_right_arm",
    "pointing_left",
    "pointing_right",
    "sitting",
    "standing",
    "lying"
]