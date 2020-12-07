import random
import os
import json
import IPython

class Color_dict:


    def __init__(self, base_dir):
        self.class_count = 0
        self.base_dir = base_dir
        self.R = list()
        self.G = list()
        self.B = list()
        self.load_color()
    
    def init_dict(self, class_count=500):
        self.add_color(class_count)
        

    def load_color(self):
        if not os.path.exists(os.path.join(self.base_dir, 'color_dict.json')):
            self.init_dict()
        with open(os.path.join(self.base_dir, 'color_dict.json'), 'r', encoding='utf-8') as f:
            color_list = json.load(f)
        self.R = color_list[0]
        self.G = color_list[1]
        self.B = color_list[2]
        self.class_count = len(self.R)
    
    def get_color(self, class_id):
        if class_id <= 0:
            return ()
        if class_id > self.class_count:
            self.add_color(class_id-self.class_count)
        #IPython.embed()
        return tuple([self.R[class_id-1], self.G[class_id-1], self.B[class_id-1]])
    
    def add_color(self, add_count):
        for count in range(add_count):
            color = random.sample(range(0,256), 3)
            while color[0] in self.R and color[1] in self.G and color[2] in self.B:
                color = random.sample(range(0,256), 3)
            self.R.append(color[0])
            self.G.append(color[1])
            self.B.append(color[2])

        self.class_count += add_count
        with open(os.path.join(self.base_dir, 'color_dict.json'), 'w', encoding='utf-8') as f:
            json.dump([self.R, self.G, self.B], f, ensure_ascii=False)