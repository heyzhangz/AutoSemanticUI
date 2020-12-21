import random
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_NAME = 'config'
COLOR_NAME = 'color_dict.json'
COLOR_PATH = os.path.join(BASE_DIR, CONFIG_NAME, COLOR_NAME)

class Color_dict:


    def __init__(self):
        self.class_count = 0
        self.color_list = []
        self.load_color()
    
    def init_dict(self, class_count=512):
        self.add_color(class_count)
        

    def load_color(self):
        if not os.path.exists(COLOR_PATH):
            self.init_dict()
        with open(COLOR_PATH, 'r', encoding='utf-8') as f:
            self.color_list = json.load(f)
        self.class_count = len(self.color_list)
    
    def get_color(self, class_id):
        class_id = int(class_id)
        if class_id < 0:
            return ()
        if class_id > self.class_count:
            self.add_color(class_id-self.class_count)
        #IPython.embed()
        return tuple(self.color_list[class_id])
 
    def add_color(self, add_count):
        for count in range(add_count):
            color = [30*((count//81)%9), 30*((count//9)%9), 30*(count%9)]
            self.color_list.append(color)
        #    print(color)
        with open(COLOR_PATH, 'w', encoding = 'utf-8') as f:
            json.dump(self.color_list, f, indent=1, ensure_ascii=False)
            