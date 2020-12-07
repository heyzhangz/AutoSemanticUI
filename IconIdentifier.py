import os
import json
import numpy as np
import pickle

from keras.models import load_model
from keras.preprocessing.image import ImageDataGenerator
from PIL import Image

from AnomalyDetector import AnomalyDetector

IMAGE_POSTFIX = (".png", ".jpg", ".jpeg")
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
MODEL_PATH = os.path.join(CURRENT_PATH, "models", "icon_models", "small_cnn_weights_100_512.h5")
ANOMALY_MODEL_PATH = os.path.join(CURRENT_PATH, "models", "icon_models", "anomaly.pkl")
ANOMALY_INV_MODEL_PATH = os.path.join(CURRENT_PATH, "models", "icon_models", "inv_anomaly.pkl")

DATA_GEN_PATH = os.path.join(CURRENT_PATH, "models", "icon_models", "datagen.pkl")
CLASS_LIST = os.path.join(CURRENT_PATH, "config", "icon_class_list.json")
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
    boxWidth = grabbox[3] - grabbox[1]
    boxLength = grabbox[2] - grabbox[0]
    boxPixel = boxWidth * boxLength
    
    aspectRatio = boxLength / boxWidth if boxLength < boxWidth else boxWidth / boxLength
    areaRatio = boxPixel / allPixel

    if aspectRatio > 0.75 and areaRatio <= 0.05:
        return True

    return False

def grabImg(imgpath, grabbox):
    """
        截取部分图片
    """

    img = Image.open(imgpath)
    subImg = img.crop(grabbox)

    return subImg

def classifyIconFromNode(image, node, id : IconDetector):

    # TODO
    pass

class IconDetector:

    def __init__(self):
        
        self.model = load_model(MODEL_PATH)

        self.anomalyModel = AnomalyDetector()
        self.anomalyModel.load(ANOMALY_MODEL_PATH)
        self.anomalyModel.load_inv(ANOMALY_INV_MODEL_PATH)

        with open(DATA_GEN_PATH, 'rb') as dgfile:
            self.datagen = pickle.load(dgfile, encoding='latin1')
        with open(CLASS_LIST, 'r') as clfile:
            self.classList = json.load(clfile)
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
        prediction = self.model.predict(x)

        anomalies = np.zeros(1)
        if self.anomalyModel:
            anomalies = self.anomalyModel.predict(prediction)

        predictClass = np.argmax(prediction, axis=1)
        return self.classList[predictClass[0]] if not anomalies[0] else 'anomaly'
        

if __name__ == "__main__":
    # print(getInputFileList("./icons/cart_1.png"))
    id = IconDetector()
    id.preprocessImgpath("./icons/anomaly_1.png")
    res = id.predict()
    print(res)