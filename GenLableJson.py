import os
import json
import re

LABLE_FILE = "Lable_json.json"
IN_IMG = "screenshot_color.jpg"
CONFIG = "config"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def lable_interface():
    if not os.path.exists(os.path.join(BASE_DIR, CONFIG, LABLE_FILE)):
        lable_json = dict()
    else:
        with open(os.path.join(BASE_DIR, CONFIG, LABLE_FILE), 'r', encoding = 'utf-8') as f:
            lable_json = json.load(f)
    return lable_json

def write_lablejson(packagename, ui, regions_list, lable_json):
    size = os.path.getsize(os.path.join(BASE_DIR, packagename, ui, IN_IMG))
    lable_name = packagename+ui+".jpg"
    lable_value = {"filename": os.path.join(packagename, ui, IN_IMG), "size": size, "regions": regions_list, "file_attributes":{"image_url": os.path.join(packagename, ui, IN_IMG)}}
    lable_json.update({lable_name: lable_value})
    with open(os.path.join(BASE_DIR, CONFIG, LABLE_FILE), 'w', encoding = 'utf-8') as f:
        json.dump(lable_json, f, indent=4, ensure_ascii=False)
    return lable_json


def get_regions_list(bounds, class_id, descri, regions_list):
    bounds = re.findall("\d+", bounds)
    shape_attributes_value = {"name": "polygon", "all_points_x": [int(bounds[0]), int(bounds[2]), int(bounds[0]), int(bounds[2])], "all_points_y": [int(bounds[1]), int(bounds[1]), int(bounds[3]), int(bounds[3])]}
    region_attributes_value = {"name": descri, "class": str(class_id), "image_quality":{"frontal":True}}
    regions_value = {"shape_attributes": shape_attributes_value, "region_attributes": region_attributes_value}
    regions_list.append(regions_value)
