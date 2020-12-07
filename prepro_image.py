import os
import sys
import xml.dom.minidom
import json
import re
import IPython
from PIL import Image
import numpy as np
import random
from Color import *
from LablePkg import *


def get_component_loc(layout_path):
    loc_list = []
    try:
        dom = xml.dom.minidom.parse(layout_path)
    except Exception as e:
        print(layout_path + ' error :' + str(e))
        dom = None
    if dom == None:
        return []
    root = dom.documentElement
    root = root.childNodes
    #root = del_toptar(root)
    
    #IPython.embed()
    parse_Element(root, loc_list)
    return loc_list

def parse_Element(Elements, loc_list):
    for node in Elements:
        if isinstance(node, xml.dom.minidom.Text):
            continue
        elif isinstance(node, xml.dom.minidom.Element):
            if node.childNodes == []:
                #只给textvivew和button染色
                
                #if node.getAttribute("class") == "android.widget.TextView" or node.getAttribute("class") == "android.widget.Button":
                if node.getAttribute("package") != "com.android.systemui":
                    loc_list.append(node.getAttribute("bounds") + str(class_id(node.getAttribute("bounds"))))
            else:
                parse_Element(node.childNodes, loc_list)
        else:
            print(type(node))


def dye_image(loc_list, image_path, out_image_path, color_dict):
    img = Image.open(image_path)
    (img_row, img_col) = img.size
    for row in img_row:
        for col in img_col:
            img.putpixel((row, col), (255,255,255))
    for loc in loc_list:
        location = re.findall("\d+", loc)
        for col in range(int(location[0]), int(location[2])):
            for row in range(int(location[1]), int(location[3])):
                img.putpixel((col, row), color_dict.get_color(int(location[4])))
    
    img = img.convert("RGB")
    img.save(out_image_path)




def class_id(loc):

    return random.randint(1, 100)


if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    color = Color_dict(base_dir)
    log = LablePkg(base_dir)
    for packagename in os.listdir(base_dir):
        print(packagename)
        if os.path.isfile(packagename):
            continue
        for ui in os.listdir(os.path.join(base_dir, packagename)):
            if ui[:2] != 'ui':
                continue
            loc_list = get_component_loc(os.path.join(base_dir, packagename, ui, 'layout.xml'))
            dye_image(loc_list, os.path.join(base_dir, packagename, ui, 'screenshot.jpg'), os.path.join(base_dir, packagename, ui, 'screenshot_color.jpg'), color)
        log.lable_pkg(packagename)
    