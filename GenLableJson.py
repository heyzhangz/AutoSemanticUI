import os
import json
import re

LABLE_FILE = "Lable_json.json"
OUT_IMG = 'screenshot_color.jpg'
RAN_IMG = 'screenshot_random.jpg'
ONE_IMG = 'screenshot_one.jpg'
DATASET = "testcase"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, DATASET)

def lable_interface():
    if not os.path.exists(os.path.join(BASE_DIR, DATASET, LABLE_FILE)):
        lable_json = dict()
    else:
        with open(os.path.join(BASE_DIR, DATASET, LABLE_FILE), 'r', encoding = 'utf-8') as f:
            lable_json = json.load(f)
    return lable_json


def write_lablejson(ui_path, regions_list):
    #size = os.path.getsize(os.path.join(BASE_DIR, packagename, ui, IN_IMG))
    lable_json = dict()
    lable_name = ui_path+".jpg"
    lable_value = {"filename": [os.path.join(ui_path, OUT_IMG), os.path.join(ui_path, RAN_IMG), os.path.join(ui_path, ONE_IMG)], "regions": regions_list, "file_attributes":{"image_url": ""}}
    lable_json.update({lable_name: lable_value})
    with open(os.path.join(DATASET_PATH, ui_path, LABLE_FILE), 'w', encoding = 'utf-8') as f:
        json.dump(lable_json, f, indent=4, ensure_ascii=False)


def get_regions_list(bounds, class_id, descri, regions_list):
    bounds = re.findall("\d+", bounds)
    shape_attributes_value = {"name": "polygon", "all_points_x": [int(bounds[0]), int(bounds[2]), int(bounds[2]), int(bounds[0])], "all_points_y": [int(bounds[1]), int(bounds[1]), int(bounds[3]), int(bounds[3])]}
    region_attributes_value = {"name": descri, "class": str(class_id), "image_quality":{"frontal":True}}
    regions_value = {"shape_attributes": shape_attributes_value, "region_attributes": region_attributes_value}
    regions_list.append(regions_value)
