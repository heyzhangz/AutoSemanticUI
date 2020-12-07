import random
import os
import json
import IPython

class Color_dict:


    def __init__(self, base_dir):
        self.class_count = 0
        self.color_list = []
        self.base_dir = base_dir
        self.load_color()
    
    def init_dict(self, class_count=300):
        self.add_color(class_count)
        

    def load_color(self):
        if not os.path.exists(os.path.join(self.base_dir, 'color_dict.json')):
            self.init_dict()
        with open(os.path.join(self.base_dir, 'color_dict.json'), 'r', encoding='utf-8') as f:
            self.color_list = json.load(f)
        self.class_count = len(self.color_list)
    
    def get_color(self, class_id):
        if class_id < 0:
            return ()
        if class_id > self.class_count:
            self.add_color(class_id-self.class_count)
        #IPython.embed()
        return tuple(self.color_list[class_id])
    """
    def add_color(self, add_count):
        for count in range(add_count):
            print(count)
            color = random.sample(range(0,256), 3)
            while color[0] in self.R and color[1] in self.G and color[2] in self.B:
                color = random.sample(range(0,256), 3)

        self.class_count += add_count
        with open(os.path.join(self.base_dir, 'color_dict.json'), 'w', encoding='utf-8') as f:
            json.dump([self.R, self.G, self.B], f, indent=4, ensure_ascii=False)
    """
    def add_color(self, add_count):
        for count in range(add_count):
            color = [30*((count//81)%9), 30*((count//9)%9), 30*(count%9)]
            self.color_list.append(color)
            print(color)
        with open(os.path.join(self.base_dir, 'color_dict.json'), 'w', encoding = 'utf-8') as f:
            json.dump(self.color_list, f, indent=1, ensure_ascii=False)
            