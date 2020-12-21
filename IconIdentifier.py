import os
import json
import numpy as np
import pickle
import xml.dom.minidom
import re

from keras.models import load_model
from keras.preprocessing.image import ImageDataGenerator
from PIL import Image

from AnomalyDetector import AnomalyDetector

IMAGE_POSTFIX = (".png", ".jpg", ".jpeg")
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
# CURRENT_PATH = "/home/zhangz/Downloads/"
MODEL_PATH = os.path.join(CURRENT_PATH, "models", "icon_models", "small_cnn_weights_100_512.h5")
ANOMALY_MODEL_PATH = os.path.join(CURRENT_PATH, "models", "icon_models", "anomaly.pkl")
ANOMALY_INV_MODEL_PATH = os.path.join(CURRENT_PATH, "models", "icon_models", "inv_anomaly.pkl")

DATA_GEN_PATH = os.path.join(CURRENT_PATH, "models", "icon_models", "datagen.pkl")
CLASS_LIST = os.path.join(CURRENT_PATH, "config", "id_class.json")
TEXT_CLASS_LIST = os.path.join(CURRENT_PATH, "config", "text_class.json")
WIDGET_CLASS_LIST= os.path.join(CURRENT_PATH, "config", "widget_class.json")
INPUT_SIZE = 32

def getInputFileList(inputpath):

    if not os.path.exists(inputpath):
        return []

    # 输入单张图标截图
    if os.path.splitext(inputpath)[-1] in IMAGE_POSTFIX:
        return [inputpath]
    
    # 非图片非目录, 鬼知道为啥输入进来=. =
    if not os.path.isdir(inputpath):
        return []
    
    imagelist = []
    for filename in os.listdir(inputpath):
        if os.path.splitext(filename)[-1] in IMAGE_POSTFIX:
            imagelist.append(os.path.join(inputpath, filename))

    return imagelist

def isIcon(screenSize, grabbox):
    """
        判断是否是图标
    """
    allPixel = screenSize[0] * screenSize[1]
    boxLength = grabbox[3] - grabbox[1]
    boxWidth = grabbox[2] - grabbox[0]
    boxPixel = boxWidth * boxLength
    
    aspectRatio = boxWidth / boxLength if boxWidth < boxLength else boxLength / boxWidth
    areaRatio = boxPixel / allPixel

    if aspectRatio > 0.75 and areaRatio <= 0.05:
        return True

    return False

def grabImg(img, grabbox):
    """
        截取部分图片
    """

    #img = Image.open(imgpath)
    subImg = img.crop(grabbox)
    return subImg

def classifyIconFromNode(image, node, id):
    location = re.findall("\d+", node.getAttribute("bounds"))
    #location = [0,255,0,255]
    grabbox = [int(location[0]), int(location[1]), int(location[2]), int(location[3])]

    class_id = 100 # class : 100非图标, 图片型控件
    if isIcon(image.size, grabbox):
        icon_img = grabImg(image, grabbox)
        id.preprocess(icon_img)
        class_id = id.predict()

    return class_id, id.classList[str(class_id)]

def classifyWidgetFromNode(node, id):

    class_id = "499" # default id
    node_class = node.getAttribute("class")

    # 判断原生类别
    for keyid, widgetlist in id.widgetClassList.items():
        # 图片判断过了, 跳过
        if keyid == "100":
            continue
        if True in [node_class.endswith(keyword) for keyword in widgetlist]:
            class_id = keyid
            return class_id, id.classList[class_id]

    # 可能是第三方类别, 专门判断一下
    if re.match(r".*text.*view.*", node_class, re.I):
        class_id = "270" # widget_input
    elif re.match(r".*webview.*", node_class, re.I):
        class_id = "380" # widget_webview

    return class_id, id.classList[class_id]


def searchTextCategory(text, id):
    # 450 text_default 暂未分类的text
    category_id = "450"
    for keyword, classid in id.text_id_map.items():
        # 字典中的某个词命中text，且是该text的主要组成部分(占字长度超过50%)
        if keyword in text and len(keyword) / len(text) >= 0.5:
            category_id = classid
            
    return category_id, id.classList[category_id]
    
def classifyTextFromNode(node, id):
    text = node.getAttribute("text")
    return searchTextCategory(text, id)

class IconDetector:

    def __init__(self):
        
        self.model = load_model(MODEL_PATH)

        self.anomalyModel = AnomalyDetector()
        self.anomalyModel.load(ANOMALY_MODEL_PATH)
        self.anomalyModel.load_inv(ANOMALY_INV_MODEL_PATH)

        with open(DATA_GEN_PATH, 'rb') as dgfile:
            self.datagen = pickle.load(dgfile, encoding='latin1')
            # self.datagen = ImageDataGenerator(
            #     zca_whitening=True,
            # )
        with open(CLASS_LIST, 'r') as clfile:
            self.classList = json.load(clfile)

        with open(TEXT_CLASS_LIST) as f:
            text_class = json.load(f)

        self.text_id_map = {}
        for k, v in text_class.items():
            for t in v:
                self.text_id_map[t] = k
        
        with open(WIDGET_CLASS_LIST) as f:
            self.widgetClassList = json.load(f)

        self.x = None
 
        pass

    def preprocessImgpath(self, imgpath):

        image = Image.open(imgpath)
        self.preprocess(image)

        pass

    def preprocess(self, image):

        imageSize = (INPUT_SIZE, INPUT_SIZE)
        image = image.convert('L').resize(imageSize, Image.ANTIALIAS)

        singleArrSize = (INPUT_SIZE, INPUT_SIZE, 1)
        image = np.asarray(image, dtype='int32')
        image = image.astype('float32')
        image /= 255
        image = image.reshape(singleArrSize)

        xShape = (1, INPUT_SIZE, INPUT_SIZE, 1)
        x = np.zeros(xShape)
        x[0] = image
        self.x = x

        pass

    def predict(self):

        x = self.datagen.flow(self.x, batch_size=1, shuffle=False).next()
        # preImg = Image.fromarray(x.reshape(32, 32) * 255).convert('RGB')
        # preImg.save("./n.png")
        prediction = self.model.predict(x)
        anomalies = np.zeros(1)
        if self.anomalyModel:
            anomalies = self.anomalyModel.predict(prediction)

        predictClass = np.argmax(prediction, axis=1)

        if anomalies[0]:
            print("[INFO] predict result : anomaly")
            return 99 # 其它图标
        else:
            print("[INFO] predict result : " + self.classList[str(predictClass[0])])
            return predictClass[0]
        
        pass

if __name__ == "__main__":
    # print(getInputFileList("./icons/cart_1.png"))
    id = IconDetector()
    id.preprocessImgpath("./icons/good_1.png")
    res = id.predict()
    print(res)