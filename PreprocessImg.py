import os
import sys
import xml.dom.minidom
import json
import re
import argparse
from PIL import Image
import numpy as np
import random
import copy
from functools import cmp_to_key
import IPython
from Color import *
from IconIdentifier import *
from multiprocessing import Process
import GenLableJson
 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LABLE_FILE = "Lable_json.json"
DATASET = 'testcase'
LAYOUT = 'layout.xml'
IMG = 'screenshot.jpg'
OUT_IMG = 'screenshot_color.jpg'
RAN_IMG = 'screenshot_random.jpg'
ONE_IMG = 'screenshot_one.jpg'
DATASET_PATH = os.path.join(BASE_DIR, DATASET)

# testallwidget = {}

def get_test_path():
    test_path = []
    for root, dirs, files in os.walk(os.path.join(DATASET_PATH, 'test')):
        for file in files:
            if '.jpg' in file:
                test_path.append(os.path.join(root, file))
    return test_path

def package_path():
    package_list = []
    for root, dir, files in os.walk(DATASET_PATH):
        ui_basename = os.path.basename(root)
        if re.match(r"ui_\d+_\d+", ui_basename):
            ui_dirname = os.path.dirname(root)
            ui_basedirname = os.path.basename(ui_dirname)
            ui_path = os.path.join(ui_basedirname, ui_basename)

            package_name = ui_basedirname.split('_')[0]
            package_list.append({'package_name': package_name, 'ui_path':ui_path})

    print(package_list)
    return package_list

def get_class_num():
    class_dict = dict()
    for package in os.listdir(DATASET_PATH):
        for ui in os.listdir(os.path.join(DATASET_PATH, package)):
            with open(os.path.join(DATASET_PATH, package, ui, 'Lable_json.json'), 'r', encoding='utf-8') as f:
                lable_json = json.load(f)
            lable_list = list(lable_json.values())[0]
            for region in lable_list['regions']:
                class_dict.update({region['region_attributes']['class']: region['region_attributes']['name']})
    
    with open(os.path.join(DATASET_PATH), 'w', encoding='utf-8') as f:
        json.dump(class_dict, f, indent=4, ensure_ascii=False)

class ProIMG():

    def __init__(self, name, task_list, id, color):
        super().__init__()
        self.name = name
        self.task_list = task_list
        self.id = id
        self.color = color


    def run(self):
        for task in self.task_list:
            print("[DOING]: " + task['ui_path'])
            regions_list = []
            self.process_main(task['ui_path'], task['package_name'], regions_list)
            GenLableJson.write_lablejson(task['ui_path'], regions_list)
                
    def process_main(self, ui_path, package_name, regions_list):
        nodes = []
        (root, img) = self.load_img_layout(ui_path)
        if root == None or img == None:
            return
        self.parse_dom(root, package_name, nodes)
        nodes = sorted(nodes, key=cmp_to_key(self.cmp_bound))
        #分类染色
        
        white_img = np.zeros([img.size[1], img.size[0], 3], dtype=np.uint8)
        
        white_img[:][:][:] = 255
        for node in nodes:
            #IPython.embed()
            class_id, descri = self.classify(node, img)
            #class_id, descri = self.classify_3(node, img)
            #color_3 = [[255,0,0], [0,255,0], [0,0,255]]
            #self.dye_color(tuple(color_3[class_id]), white_img, node.getAttribute("bounds"))
            self.dye_color(self.color.get_color(class_id), white_img, node.getAttribute("bounds"))
            GenLableJson.get_regions_list(node.getAttribute("bounds"), class_id, descri, regions_list)

            out_img = Image.fromarray(white_img)
            out_img = out_img.convert("RGB")
            out_img.save(os.path.join(DATASET_PATH, ui_path, OUT_IMG))
            print("[DONE] " + ui_path + ' classify color')

            
            #随机染色
            white_img[:][:][:] = 255
            for node in nodes:
                self.dye_color(self.color.get_color(random.randint(0,500)), white_img, node.getAttribute("bounds"))
            out_img = Image.fromarray(white_img)
            out_img = out_img.convert("RGB")
            out_img.save(os.path.join(DATASET_PATH, ui_path, RAN_IMG))
            print("[DONE] " + ui_path + ' random color')

            #一种颜色
            white_img[:][:][:] = 255
            for node in nodes:
                self.dye_color(self.color.get_color(300), white_img, node.getAttribute("bounds"))
            out_img = Image.fromarray(white_img)
            out_img = out_img.convert("RGB")
            out_img.save(os.path.join(DATASET_PATH, ui_path, ONE_IMG))
            print("[DONE] " + ui_path + ' one color')
            

    def cmp_bound(self, node1, node2):
        location1 = node1.getAttribute("bounds")
        location1 = re.findall("\d+", location1)
        location2 = node2.getAttribute("bounds")
        location2 = re.findall("\d+", location2)
        if (int(location2[2])-int(location2[0]))*(int(location2[3])-int(location2[1])) < (int(location1[2])-int(location1[0]))*(int(location1[3])-int(location1[1])):
            return -1
        if (int(location1[2])-int(location1[0]))*(int(location1[3])-int(location1[1])) < (int(location2[2])-int(location2[0]))*(int(location2[3])-int(location2[1])):
            return 1
        return 0


    def classify_3(self, node, img):
        # TODO 不适用了
        if node.getAttribute("class") == "android.widget.ImageView" or node.getAttribute("class") ==  "android.widget.Image":
            predict_class, descri = 0, 'image'
        elif re.match(r'.*Text.*', node.getAttribute("class"), re.I):
            predict_class, descri = 1, 'text'
        else:
            predict_class, descri = 2, 'other'
        return predict_class, descri



    def classify(self, node, img):

        predict_class = 499 # 默认other类
        node_class = node.getAttribute("class")
        node_text = node.getAttribute("text")

        # 1. 图片处理 只处理图片相关控件 class:100 image_default 图片类控件  0~100
        if True in [node_class.endswith(keyword) for keyword in id.widgetClassList["100"]]:
            predict_class, descri = classifyIconFromNode(img, node, self.id)
        # 2. 文字处理 不管控件类别, 直接读text属性 400~450
        elif node_text:
            predict_class, descri = classifyTextFromNode(node, self.id)
        # 3. 控件处理 处理功能性控件 200~380 499
        else:
            predict_class, descri = classifyWidgetFromNode(node, self.id)

        if node_class in testallwidget:
            testallwidget[node_class].add(descri)
        else:
            testallwidget[node_class] = set()
            testallwidget[node_class].add(descri)

        return predict_class, descri
     

    def dye_color(self, colorr, white_img, bounds):
        location = re.findall("\d+", bounds)
        #周围加一圈白边
        white_img[int(location[1]):int(location[3]), int(location[0]):int(location[2])] = np.array([255,255,255])
        wight = int((int(location[2]) - int(location[0]))*0.95)
        hight = int((int(location[3]) - int(location[1]))*0.95)
        location[0] = int(int(location[0]) + ((int(location[2])-int(location[0]))-wight)//2)
        location[1] = int(int(location[1]) + ((int(location[3])-int(location[1]))-hight)//2)
        white_img[int(location[1]):int(location[1])+hight,int(location[0]):int(location[0])+wight] = np.array(list(colorr)) 
    

    def load_img_layout(self, ui_path):
        try:
            dom = xml.dom.minidom.parse(os.path.join(DATASET_PATH, ui_path, LAYOUT))
        except Exception as e:
            print("[ERROR] " + os.path.join(ui_path, LAYOUT) + ' ' + str(e))
            dom = None
        if dom == None:
            return (None, None)
        root = dom.documentElement
        ElementLists = root.childNodes
        img = Image.open(os.path.join(DATASET_PATH, ui_path, IMG))
        return (ElementLists ,img)
    

    def parse_dom(self, ElementLists, package_name, nodes):
        for node in ElementLists:
            if isinstance(node, xml.dom.minidom.Text):
                continue
            elif isinstance(node, xml.dom.minidom.Element):
                if node.childNodes == []:
                    if node.getAttribute("package") == package_name and "Layout" not in node.getAttribute("class"):
                        nodes.append(node)
                else:
                    self.parse_dom(node.childNodes, package_name, nodes)
            else:
                print("[ERROR] node not is Text or Element")

    
    


if __name__ == '__main__':
    #输入参数，进程数
    parser = argparse.ArgumentParser(description='PreProcess screenshot image.')
    parser.add_argument('--process_count', required=False, default=4)
    args = parser.parse_args()
    process_count = int(args.process_count)

    #初始化
    
    package_list = package_path()


    task_count = len(package_list)//process_count
    for pro_id in range(process_count):
        id = IconDetector()
        color = Color_dict()
        p = ProIMG('pro_'+str(pro_id), package_list[pro_id*task_count: (pro_id+1)*task_count], id, color) if pro_id != process_count-1 else ProIMG('pro_'+str(pro_id), package_list[pro_id*task_count:], id, color)
        p.run()
    
    # for k, v in testallwidget.items():
    #     testallwidget[k] = list(v)

    # with open("./widgets.json", "w") as f:
    #     json.dump(testallwidget, f, indent=4)