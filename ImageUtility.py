import math

from PIL import Image, ImageFilter, ImageOps
import cv2
import numpy as np
from matplotlib import pyplot as plt

import Utility as U
import Decorator as D


def concat(image1, image2, vertical=False, coordinate1=(0, 0), coordinate2=(0, 0)):
  return concatVertical(image1, image2, coordinate1, coordinate2) if vertical else concatHorizontal(image1, image2, coordinate1, coordinate2)


# cv2.hconcat
def concatHorizontal(image1, image2, coordinate1=(0, 0), coordinate2=(0, 0)):
  height = image1.height if image1.height > image2.height else image2.height
  image = Image.new('RGB', (image1.width + image2.width, height))
  image.paste(image1, coordinate1)
  image.paste(image2, (image1.width + coordinate2[0], coordinate2[1]))
  return image


# cv2.vconcat
def concatVertical(image1, image2, coordinate1=(0, 0), coordinate2=(0, 0)):
  width = image1.width if image1.width > image2.width else image2.width
  image = Image.new('RGB', (width, image1.height + image2.height))
  image.paste(image1, coordinate1)
  image.paste(image2, (coordinate2[0], image1.height + coordinate2[1]))
  return image

  # OpenCv


def getMaxL2(height, width, dtype=np.uint8):
  info = np.iinfo(dtype)
  white = np.ones((height, width, 3), dtype) * info.min
  black = np.ones((height, width, 3), dtype) * info.max
  return cv2.norm(white, black, cv2.NORM_L2)


@D.stopwatchPrintSE
def isSameImage(image1, image2, percent=0.99, maxL2=None):
  if image1.shape != image2.shape:
    print(f"shape ng:{image1.shape} {image2.shape}")
    return False
  if maxL2 is None:
    maxL2 = getMaxL2(image1.shape[0], image1.shape[1])
  l2 = cv2.norm(image1, image2, cv2.NORM_L2)
  similarity = 1 - l2 / maxL2
  # print(f"Similarity = {similarity}, L2 = {l2}")
  # print(f"({image1.shape[0]}, {image1.shape[1]}) Similarity = {similarity}, L2 = {l2}, L1 = {l1}, {math.sqrt(l1)}, {image1.shape[0] * image1.shape[1] * 255}")
  if similarity > percent:
    return True
  return False


# convert PIL to CV
def pilToCv(image):
  newImage = np.array(image, dtype=np.uint8)
  if newImage.ndim == 2:  # モノクロ
    pass
  elif newImage.shape[2] == 3:  # カラー
    newImage = cv2.cvtColor(newImage, cv2.COLOR_RGB2BGR)
  elif newImage.shape[2] == 4:  # 透過
    newImage = cv2.cvtColor(newImage, cv2.COLOR_RGBA2BGRA)
  return newImage


# convert CV to PIL
def cvToPil(image):
  newImage = image.copy()
  if newImage.ndim == 2:  # モノクロ
    pass
  elif newImage.shape[2] == 3:  # カラー
    newImage = cv2.cvtColor(newImage, cv2.COLOR_BGR2RGB)
  elif newImage.shape[2] == 4:  # 透過
    newImage = cv2.cvtColor(newImage, cv2.COLOR_BGRA2RGBA)
  newImage = Image.fromarray(newImage)
  return newImage


def applyFilter(image, filters):
  for filt in filters:
    if isinstance(filt, str):
      if filt == "blur":
        image = image.filter(ImageFilter.BLUR)
      elif filt == "contour":
        image = image.filter(ImageFilter.CONTOUR)
      elif filt == "detail":
        image = image.filter(ImageFilter.DETAIL)
      elif filt == "edgeEnhance":
        image = image.filter(ImageFilter.EDGE_ENHANCE)
      elif filt == "edgeEnhanceMore":
        image = image.filter(ImageFilter.EDGE_ENHANCE_MORE)
      elif filt == "emboss":
        image = image.filter(ImageFilter.EMBOSS)
      elif filt == "findEdges":
        image = image.filter(ImageFilter.FIND_EDGES)
      elif filt == "sharpen":
        image = image.filter(ImageFilter.SHARPEN)
      elif filt == "smooth":
        image = image.filter(ImageFilter.SMOOTH)
      elif filt == "smoothMore":
        image = image.filter(ImageFilter.SMOOTH_MORE)
      else:
        print(f"unknown filter: {filt}")
    elif isinstance(filt, list) or isinstance(filt, tuple):
      if filt[0] == "color3DLUT":
        pass
        # image = image.filter(ImageFilter.Color3DLUT(*filt))
      elif filt[0] == "boxBlur":
        image = image.filter(ImageFilter.BoxBlur(*filt[1:]))
      elif filt[0] == "gaussianBlur":
        image = image.filter(ImageFilter.GaussianBlur(*filt[1:]))
      elif filt[0] == "unsharpMask":
        image = image.filter(ImageFilter.UnsharpMask(*filt[1:]))
      elif filt[0] == "kernel":
        image = image.filter(ImageFilter.Kernel(*filt[1:]))
      else:
        print(f"unknown filter: {filt}")
  return image


# 画像のモーメント
# 面積(area): moments["m00"]
# 重心(centroid): (moments["m10"]/moments["m00"], moments["m01"]/moments["m00"])
def getMoments(image, doBinarize=False):
  if doBinarize:
    image = binarize(image)
  moments = cv2.moments(image)
  return moments


# cv2.contourArea(contour)
def getArea(moments):
  area = moments["m00"]
  center = (0, 0)
  if area != 0:
    center = (
      moments["m10"] / moments["m00"],
      moments["m01"] / moments["m00"],
    )
  return (area, center)


def getStartEnd(contour):
  return np.append(contour.min(axis=0), contour.max(axis=0), axis=0)


# 2値化
def binarize(image, thresh=127, maxval=255, type=cv2.THRESH_OTSU, pil=False):
  image = pilToCv(image) if pil else image
  if image.ndim != 2:
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  _, image = cv2.threshold(image, thresh=thresh, maxval=maxval, type=type)
  image = cvToPil(image) if pil else image
  return image


def adaptiveBinarize(image, blockSize=3, C=2, pil=False):
  image = pilToCv(image) if pil else image
  if image.ndim != 2:
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, blockSize=blockSize, C=C)
  image = cvToPil(image) if pil else image
  return image


def approxPolyDP(contour, epsilon=0.005):
  arcLen = cv2.arcLength(contour, True)
  contour = cv2.approxPolyDP(contour, epsilon=epsilon * arcLen, closed=True)
  return contour, len(contour)


def canny(image, threshold1, threshold2, apertureSize=3, L2gradient=False, pil=False):
  image = pilToCv(image) if pil else image
  image = cv2.Canny(image, threshold1=threshold1, threshold2=threshold2, apertureSize=apertureSize, L2gradient=L2gradient)
  image = cvToPil(image) if pil else image
  return image


def invert(image):
  return np.invert(image)


def equalizeHist(image, channels=(2,), pil=False):
  image = pilToCv(image) if pil else image
  chs = list(cv2.split(image))
  for i in channels:
    chs[i] = cv2.equalizeHist(chs[i])
  image = cv2.merge(chs)
  image = cvToPil(image) if pil else image
  return image


def equalizeAdaptiveHist(image, channels=(2,), clipLimit=40.0, tileGridSize=(8, 8), pil=False):
  image = pilToCv(image) if pil else image
  chs = list(cv2.split(image))
  clahe = cv2.createCLAHE(clipLimit=clipLimit, tileGridSize=tileGridSize)
  for i in channels:
    chs[i] = clahe.apply(chs[i])
  image = cv2.merge(chs)
  image = cvToPil(image) if pil else image
  return image


# code=cv2.COLOR_BGR2GRAY
# code=cv2.COLOR_BGR2HSV
# code=cv2.COLOR_BGR2HSV_FULL
# code=cv2.COLOR_HSV2BGR
# code=cv2.COLOR_HSV2BGR_FULL
def covetColor(image, code=cv2.COLOR_BGR2GRAY, pil=False):
  image = pilToCv(image) if pil else image
  image = cv2.cvtColor(image, code=code)
  image = cvToPil(image) if pil else image
  return image


# 画像を拡張する
def addBorder(image, widths=(1, 1, 1, 1), borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0), pil=False):
  image = pilToCv(image) if pil else image
  image = cv2.copyMakeBorder(image, *widths, borderType=borderType, value=value)
  image = cvToPil(image) if pil else image
  return image


# 画像を拡張しない
# 四隅が少し汚い
def drawBorder(image, color=(0, 0, 0), thickness=1, lineType=cv2.LINE_8, pil=False):
  image = pilToCv(image) if pil else image
  offset = int(thickness / 2)
  image = cv2.rectangle(image, (offset, offset), (image.shape[1] - offset - 1, image.shape[0] - offset - 1), color=color, thickness=thickness, lineType=lineType)
  image = cvToPil(image) if pil else image
  return image


def getHistgram(image, mask=None, pil=False):
  image = pilToCv(image) if pil else image
  hist0 = cv2.calcHist([image], [0], mask, [256], [0, 256])
  hist1 = cv2.calcHist([image], [1], mask, [256], [0, 256])
  hist2 = cv2.calcHist([image], [2], mask, [256], [0, 256])
  return (hist0, hist1, hist2)


def plotHistgram(hist0, hist1, hist2):
  plt.title("Histgram")
  plt.plot(hist0, c='blue', label='blue')
  plt.plot(hist1, c='green', label='green')
  plt.plot(hist2, c='red', label='red')
  # plt.xlim([0, 256])
  plt.grid()