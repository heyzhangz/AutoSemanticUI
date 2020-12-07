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


def pre_img(base_dir, packagename, ui):
    #loc_list = []
    try:
        dom = xml.dom.minidom.parse(os.path.join(base_dir, packagename, ui, "layout.xml"))
    except Exception as e:
        print(os.path.join(base_dir, packagename, ui, "layout.xml") + ' error :' + str(e))
        dom = None
    if dom == None:
        return
    root = dom.documentElement
    root = root.childNodes
    #root = del_toptar(root)
    img = Image.open(os.path.join(base_dir, packagename, ui, "screenshot.jpg"))
    (img_row, img_col) = img.size
    for row in range(img_row):
        for col in range(img_col):
            img.putpixel((row, col), (255,255,255))
    #IPython.embed()
    parse_Element(root, img)
    img = img.convert("RGB")
    img.save(os.path.join(base_dir, packagename, ui, "screenshot_color.jpg"))


def parse_Element(Elements, img):
    for node in Elements:
        if isinstance(node, xml.dom.minidom.Text):
            continue
        elif isinstance(node, xml.dom.minidom.Element):
            if node.childNodes == []:
                #只给textvivew和button染色
                
                #if node.getAttribute("class") == "android.widget.TextView" or node.getAttribute("class") == "android.widget.Button" or node.getAttribute("class") == "android.widget.ImageView":
                if node.getAttribute("package") != "com.android.systemui" and node.getAttribute("class") != "android.view.View" and "Layout" not in node.getAttribute("class"):
                    dye_image(node.getAttribute("bounds"), random.randint(0,299), img)
            else:
                parse_Element(node.childNodes, img)
        else:
            print(type(node))
"""
def classify(node):
    if node.getAttribute("class") == "android.widget.TextView":
        return text_class(node)
    
    elif node.getAttribute("class") == "android.widget.ImageView":
        return icon_class(node)
    else:
        return other_class(node)    
"""  

"""
def dye_image(loc_list, image_path, out_image_path, color_dict):
    
    for loc in loc_list:
        location = re.findall("\d+", loc)
        for col in range(int(location[0]), int(location[2])):
            for row in range(int(location[1]), int(location[3])):
                img.putpixel((col, row), color_dict.get_color(int(location[4])))
    
    img = img.convert("RGB")
    img.save(out_image_path)
"""
def dye_image(loc, class_id, img):
    #print(str(class_id) + ':' + str(color.get_color(class_id)))
    location = re.findall("\d+", loc)
    for row in range(int(location[0]), int(location[2])):
        for col in range(int(location[1]), int(location[3])):
            img.putpixel((row, col), color.get_color(class_id))
    
    


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
            print(ui)
            if ui[:2] != 'ui':
                continue
            pre_img(base_dir, packagename, ui)
            #dye_image(loc_list, os.path.join(base_dir, packagename, ui, 'screenshot.jpg'), os.path.join(base_dir, packagename, ui, 'screenshot_color.jpg'), color)
        log.lable_pkg(packagename)