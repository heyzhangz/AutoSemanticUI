import os
import sys
import xml.dom.minidom
import json
import re
from PIL import Image
import numpy as np
import random
import copy
from Color import *
from LablePkg import *
from IconIdentifier import *
import GenLableJson

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
    img = Image.open(os.path.join(base_dir, packagename, ui, "screenshot.jpg"))
    img_Icon = copy.deepcopy(img)
    (img_row, img_col) = img.size
    for row in range(img_row):
        for col in range(img_col):
            img.putpixel((row, col), (255,255,255))
    #IPython.embed()
    regions_list = []
    parse_Element(root, img, img_Icon, regions_list)
    img = img.convert("RGB")
    img.save(os.path.join(base_dir, packagename, ui, "screenshot_color.jpg"))
    GenLableJson.write_lablejson(packagename, ui, regions_list, lable_json)

def parse_Element(Elements, img, img_Icon, regions_list):
    for node in Elements:
        if isinstance(node, xml.dom.minidom.Text):
            continue
        elif isinstance(node, xml.dom.minidom.Element):
            if node.childNodes == []:
                if node.getAttribute("package") != "com.android.systemui" and node.getAttribute("class") != "android.view.View" and "Layout" not in node.getAttribute("class"):
                    dye_image(node.getAttribute("bounds"), classify(node, img_Icon, regions_list), img)
            else:
                parse_Element(node.childNodes, img, img_Icon, regions_list)
        else:
            print(type(node))


def classify(node, img, regions_list):
    if node.getAttribute("class") == "android.widget.ImageView":
        predict_class, descri = classifyIconFromNode(img, node, id)
    elif node.getAttribute("class") == "android.widget.TextView":
        predict_class, descri = classifyTextFromNode(node, id)
    else:
        predict_class, descri = other_class(node)
    GenLableJson.get_regions_list(node.getAttribute("bounds"), predict_class, descri, regions_list)
    return predict_class

def other_class(node):
    return 299, "other"    
  


def dye_image(loc, class_id, img):
    location = re.findall("\d+", loc)
    for row in range(int(location[0]), int(location[2])):
        for col in range(int(location[1]), int(location[3])):
            img.putpixel((row, col), color.get_color(class_id))
    
    



if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    color = Color_dict(base_dir)
    #log = LablePkg(base_dir)
    id = IconDetector()
    lable_json = GenLableJson.lable_interface()
    for ui in os.listdir(os.path.join(base_dir, 'testcase/com.gome.eshopnew_202011301918')):
        print(ui)
        if ui[:2] != 'ui':
            continue
        pre_img(base_dir, 'testcase/com.gome.eshopnew_202011301918', ui)
    #log.lable_pkg(packagename)