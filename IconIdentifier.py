import os
import json
import numpy as np
import pickle
import xml.dom.minidom
import re
import time

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
CLASS_LIST = os.path.join(CURRENT_PATH, "config", "icon_class_list.json")

TEXT_CLASS_LIST = os.path.join(CURRENT_PATH, "config", "text_class.json")
ID_TEXTCLASS_LIST = os.path.join(CURRENT_PATH, "config", "id_textclass.json")
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

def classifyIconFromNode(image, node, id, savepath=None, filename=None):

    location = re.findall("\d+", node.getAttribute("bounds"))
    grabbox = [int(location[0]), int(location[1]), int(location[2]), int(location[3])]

    if isIcon(image.size, grabbox):
        icon_img = grabImg(image, grabbox)
        id.preprocess(icon_img)
        class_id = id.predict()
        classRes = id.classList[class_id]

        if savepath is not None and filename is not None:
            savepath = os.path.join(savepath, "%d_%s" % (class_id, classRes))
            if not os.path.exists(savepath):
                os.makedirs(savepath)
            icon_img.save(os.path.join(savepath, "%s%f.png") % (filename, time.time()))

        return class_id, classRes
    else:
        return 100, "Icon_default"   #其他imageview时

def searchTextCategory(text, id):
    # 默认199是无法分类的TextView
    category_id = 199
    name = "default"
    for t, i in id.text_id_map.items():
        # 字典中的某个词命中text，且是该text的主要组成部分(占字长度超过50%)
        if t in text and len(t) / len(text) >= 0.5:
            category_id = i
    for item in id.id_textclass.items():
        if item[1] == category_id:
            name = item[0]
    return category_id, "Text_" + name
    
def classifyTextFromNode(node, id):
    text = node.getAttribute("text")
    return searchTextCategory(text, id)
    #pass

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
        with open(ID_TEXTCLASS_LIST) as f:
            self.id_textclass = json.load(f)
        self.text_id_map = {}
        for k, v in text_class.items():
            for t in v:
                self.text_id_map[t] = self.id_textclass[k]

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
            print("[INFO] predict result : " + self.classList[predictClass[0]])
            return predictClass[0]
        
        pass

if __name__ == "__main__":
    # print(getInputFileList("./icons/cart_1.png"))
    id = IconDetector()
    id.preprocessImgpath("./icons/good_1.png")
    res = id.predict()
    print(res)