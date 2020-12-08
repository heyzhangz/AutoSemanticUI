import os
import sys
import xml.dom.minidom
import json
import re
from PIL import Image
import numpy as np
import random
from Color import *
from LablePkg import *
from IconIdentifier import *


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
    img_Icon = img
    (img_row, img_col) = img.size
    for row in range(img_row):
        for col in range(img_col):
            img.putpixel((row, col), (255,255,255))
    #IPython.embed()
    parse_Element(root, img, img_Icon)
    img = img.convert("RGB")
    img.save(os.path.join(base_dir, packagename, ui, "screenshot_color.jpg"))


def parse_Element(Elements, img, img_Icon):
    for node in Elements:
        if isinstance(node, xml.dom.minidom.Text):
            continue
        elif isinstance(node, xml.dom.minidom.Element):
            if node.childNodes == []:
                if node.getAttribute("package") != "com.android.systemui" and node.getAttribute("class") != "android.view.View" and "Layout" not in node.getAttribute("class"):
                    dye_image(node.getAttribute("bounds"), classify(node, img_Icon), img)
            else:
                parse_Element(node.childNodes, img, img_Icon)
        else:
            print(type(node))

def classify(node, img):
    if node.getAttribute("class") == "android.widget.ImageView":
        predict_class = classifyIconFromNode(img, node, id)
        print(predict_class)
        return predict_class
    else:
        return other_class(node)

def other_class(node):
    return 299    
  

def dye_image(loc, class_id, img):
    location = re.findall("\d+", loc)
    for row in range(int(location[0]), int(location[2])):
        for col in range(int(location[1]), int(location[3])):
            img.putpixel((row, col), color.get_color(class_id))
    
    



if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    color = Color_dict(base_dir)
    log = LablePkg(base_dir)
    id = IconDetector()
    for packagename in os.listdir(base_dir):
        print(packagename)
        if os.path.isfile(packagename):
            continue
        for ui in os.listdir(os.path.join(base_dir, packagename)):
            print(ui)
            if ui[:2] != 'ui':
                continue
            pre_img(base_dir, packagename, ui)
        log.lable_pkg(packagename)