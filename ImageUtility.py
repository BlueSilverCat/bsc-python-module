# cSpell:Ignore intp, ndim, imshow

# import math
import os.path
import subprocess
import copy
import itertools

from PIL import Image, ImageFilter, ImageOps
import cv2
import numpy as np
from matplotlib import pyplot as plt

import Utility as U
import Decorator as D
import Path


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


def getSimilarity(image1, image2, maxL2=None):
  if image1.shape != image2.shape:
    print(f"shape ng:{image1.shape} {image2.shape}")
    return 0.0
  if maxL2 is None:
    maxL2 = getMaxL2(image1.shape[0], image1.shape[1])
  l2 = cv2.norm(image1, image2, cv2.NORM_L2)
  similarity = 1 - l2 / maxL2
  return similarity


def isSameImage(image1, image2, threshold=0.90, maxL2=None):
  if image1.shape != image2.shape:
    return False
  if np.array_equal(image1, image2):
    return True

  similarity = getSimilarity(image1, image2, maxL2)
  print(similarity)
  return True if similarity >= threshold else False


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


def getStartEnd(contour):
  return np.append(contour.min(axis=0), contour.max(axis=0), axis=0)


def adaptiveBinarize(image, blockSize=3, C=2):
  if image.ndim != 2:
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, blockSize=blockSize, C=C)
  return image


def canny(image, threshold1, threshold2, apertureSize=3, L2gradient=False):
  image = cv2.Canny(image, threshold1=threshold1, threshold2=threshold2, apertureSize=apertureSize, L2gradient=L2gradient)
  return image


def invert(image):
  return np.invert(image)


def equalizeHist(image, channels=(2,)):
  chs = list(cv2.split(image))
  for i in channels:
    chs[i] = cv2.equalizeHist(chs[i])
  image = cv2.merge(chs)
  return image


def equalizeAdaptiveHist(image, channels=(2,), clipLimit=40.0, tileGridSize=(8, 8)):
  chs = list(cv2.split(image))
  clahe = cv2.createCLAHE(clipLimit=clipLimit, tileGridSize=tileGridSize)
  for i in channels:
    chs[i] = clahe.apply(chs[i])
  image = cv2.merge(chs)
  return image


# code=cv2.COLOR_BGR2GRAY
# code=cv2.COLOR_BGR2HSV
# code=cv2.COLOR_BGR2HSV_FULL
# code=cv2.COLOR_HSV2BGR
# code=cv2.COLOR_HSV2BGR_FULL
def covetColor(image, code=cv2.COLOR_BGR2GRAY):
  image = cv2.cvtColor(image, code=code)
  return image


# image = pilToCv(image) if pil else image


# 画像を拡張する
def addBorder(image, widths=(1, 1, 1, 1), borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0)):
  image = cv2.copyMakeBorder(image, *widths, borderType=borderType, value=value)
  return image


# 画像を拡張しない
# 四隅が少し汚い
def drawBorder(image, color=(0, 0, 0), thickness=1, lineType=cv2.LINE_8):
  offset = int(thickness / 2)
  image = cv2.rectangle(image, (offset, offset), (image.shape[1] - offset - 1, image.shape[0] - offset - 1), color=color, thickness=thickness, lineType=lineType)
  return image


def getHistogram(image, mask=None):
  hist0 = cv2.calcHist([image], [0], mask, [256], [0, 256])
  hist1 = cv2.calcHist([image], [1], mask, [256], [0, 256])
  hist2 = cv2.calcHist([image], [2], mask, [256], [0, 256])
  return (hist0, hist1, hist2)


def plotHistogram(hist0, hist1, hist2):
  plt.title("Histogram")
  plt.plot(hist0, c='blue', label='blue')
  plt.plot(hist1, c='green', label='green')
  plt.plot(hist2, c='red', label='red')
  # plt.xlim([0, 256])
  plt.grid()


def getKernel(n=5, dtype=np.float32):
  return np.ones((n, n), dtype) / n**2


def binarize(image, thresh=127, maxval=255, type=cv2.THRESH_OTSU):
  if image.ndim != 2:
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  _, image = cv2.threshold(image, thresh=thresh, maxval=maxval, type=type)
  return image


def filter2D(image, n, ddepth=-1):
  image = cv2.filter2D(image, ddepth, getKernel(n))
  return image


def blur(image, n):
  image = cv2.blur(image, (n, n))
  return image


def gaussianBlur(image, n, borderType=cv2.BORDER_DEFAULT):
  image = cv2.GaussianBlur(image, (n, n), borderType)
  return image


def medianBlur(image, size):
  image = cv2.medianBlur(image, size)
  return image


# sigma 10以下だとほとんど効果がない、一方150以上だと強い効果,
def bilateralFilter(image, d=5, sigmaColor=75, sigmaSpace=75, borderType=cv2.BORDER_DEFAULT):
  image = cv2.bilateralFilter(image, d, sigmaColor, sigmaSpace, borderType=borderType)
  return image


def denoising(image, h=5, templateWindowSize=7, searchWindowSize=21):
  if image.ndim == 2:
    image = cv2.fastNlMeansDenoising(image, h=h, templateWindowSize=templateWindowSize, searchWindowSize=searchWindowSize)
  else:
    image = cv2.fastNlMeansDenoisingColored(image, h=h, templateWindowSize=templateWindowSize, searchWindowSize=searchWindowSize)
    pass
  return image


def showImage(paths, thumbs=False):
  l = [Path.IrfanviewPath] + paths
  if thumbs:
    l.append("/thumbs")
  subprocess.Popen(l)


def showImageMix(paths, thumbs=False):
  files = list(filter(os.path.isfile, paths))
  dirs = list(itertools.filterfalse(os.path.isfile, paths))
  showImage(files, thumbs)
  showImage(dirs, thumbs)


def cv2ShowImage(image, title="output"):
  cv2.imshow(title, image)
  cv2.waitKey(0)
  cv2.destroyAllWindows()


# image: cv2
def performOperations(image, operations):
  for operation in copy.deepcopy(operations):
    if isinstance(operation, str):
      if operation == "invert":
        image = cv2.bitwise_not(image)
      elif operation == "gray":
        image = covetColor(image, cv2.COLOR_BGR2GRAY)
      else:
        print(f"unkown opration: {operation}")

    else:
      name = operation.pop("name")
      if name == "binarize":
        image = binarize(image, **operation)

      elif name == "blur":
        image = blur(image, **operation)

      elif name == "gaussianBlur":
        image = gaussianBlur(image, **operation)

      elif name == "medianBlur":
        image = medianBlur(image, **operation)

      elif name == "bilateralFilter":
        image = bilateralFilter(image, **operation)

      elif name == "denoising":
        image = denoising(image, **operation)

      elif name == "addBorder":
        image = addBorder(image, **operation)

      elif name == "drawBorder":
        image = drawBorder(image, **operation)

      elif name == "canny":
        image = canny(image, **operation)

      elif name == "adaptiveBinarize":
        image = adaptiveBinarize(image, **operation)

      elif name == "equalizeHist":
        image = covetColor(image, cv2.COLOR_BGR2HSV_FULL)
        image = equalizeHist(image, **operation)
        image = covetColor(image, cv2.COLOR_HSV2BGR_FULL)

      elif name == "equalizeAdaptiveHist":
        image = covetColor(image, cv2.COLOR_BGR2HSV_FULL)
        image = equalizeAdaptiveHist(image, **operation)
        image = covetColor(image, cv2.COLOR_HSV2BGR_FULL)

      else:
        print(f"unkown opration: {name}, {operation}")
  return image


################################################################################
## progress
################################################################################


def findContours(image, mode=cv2.RETR_LIST, method=cv2.CHAIN_APPROX_SIMPLE):
  work = image.copy()
  if image.ndim == 3:
    work = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  contours, hierarchy = cv2.findContours(work, mode=mode, method=method)
  return contours, hierarchy


def drawContours(image, contours, path1, path2="", color=(0, 0, 255), thickness=1):
  work = image.copy()
  if image.ndim == 2:
    work = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
  work = cv2.drawContours(work, contours, -1, color, thickness)
  path = path1
  if path2 != "":
    path = os.path.join(path1, path2)
  cv2.imwrite(path, work)
  return work, path


def getApproxPolyDp(contour, epsilon=None, closed=True):
  if epsilon is None:
    epsilon = 0.01 * cv2.arcLength(contour, closed)
  contour = cv2.approxPolyDP(contour, epsilon, closed=True)
  return contour, len(contour)


def getRotatedRectangle(contour):
  rect = cv2.minAreaRect(contour)
  box = cv2.boxPoints(rect)
  return np.intp(box)


def getMinimumEnclosingCircle(contour):
  (x, y), radius = cv2.minEnclosingCircle(contour)
  center = (int(x), int(y))
  radius = int(radius)
  return (center, radius)


def getFitEllipse(contour):
  if len(contour) < 5:
    return None, None
  ellipse = cv2.fitEllipse(contour)
  (_, _), (majorAxis, minorAxis), orientation = ellipse
  return ellipse, orientation


def getAspectRatio(contour):
  x, y, w, h = cv2.boundingRect(contour)
  return w / h


def getExtent(contour):
  area = cv2.contourArea(contour)
  x, y, w, h = cv2.boundingRect(contour)
  rectArea = w * h
  return area / rectArea


def getSolidity(contour):
  area = cv2.contourArea(contour)
  hull = cv2.convexHull(contour)
  hullArea = cv2.contourArea(hull)
  if hullArea == 0:
    return 0
  return area / hullArea


def getEquivalentDiameter(contour):
  area = cv2.contourArea(contour)
  return np.sqrt(4 * area / np.pi)


def getExtremePoints(contour):
  leftmost = tuple(contour[contour[:, :, 0].argmin()][0])
  rightmost = tuple(contour[contour[:, :, 0].argmax()][0])
  topmost = tuple(contour[contour[:, :, 1].argmin()][0])
  bottommost = tuple(contour[contour[:, :, 1].argmax()][0])
  return {
    "leftmost": leftmost,
    "rightmost": rightmost,
    "topmost": topmost,
    "bottommost": bottommost,
  }


def getBoundingRectangle(contour, area=None):
  if area is None:
    area = cv2.contourArea(contour)
  x, y, w, h = cv2.boundingRect(contour)
  aspectRatio = float(w / h)
  extent = area / (w * h)
  return (x, y, w, h), aspectRatio, extent


# 画像のモーメント
# 面積(area): moments["m00"]
# 重心(centroid): (moments["m10"]/moments["m00"], moments["m01"]/moments["m00"])
def getContourInfo(contour, epsilon=None, closed=True, clockwise=True, returnPoints=True, distType=cv2.DIST_L2):
  pointNumber = len(contour)
  moments = cv2.moments(contour)
  area = moments["m00"]
  area_ = cv2.contourArea(contour)
  center = (0, 0)
  if area != 0:
    center = (
      int(moments["m10"] / moments["m00"]),
      int(moments["m01"] / moments["m00"]),
    )
  arcLength = cv2.arcLength(contour, closed)
  approx, corners = getApproxPolyDp(contour, epsilon, closed)
  isContourConvex = cv2.isContourConvex(contour)
  convexHull = cv2.convexHull(contour, clockwise=clockwise, returnPoints=returnPoints)
  boundingRect, aspectRatio, extent = getBoundingRectangle(contour, area)
  # boundingRect = {
  #   "x": x,
  #   "y": y,
  #   "w": w,
  #   "h": h,
  # }
  # aspectRatio = float(w / h)
  # extent = area / (w * h)

  solidity = getSolidity(contour)
  equivalentDiameter = getEquivalentDiameter(contour)
  box = getRotatedRectangle(contour)
  mecCenter, mecRadius = getMinimumEnclosingCircle(contour)
  ellipse, orientation = getFitEllipse(contour)
  fitLine = cv2.fitLine(contour, distType, 0, 0.01, 0.01)
  # fitLine = list(map(int, fitLine))
  fitLine = {
    "vx": fitLine[0],
    "vy": fitLine[1],
    "x": fitLine[2],
    "y": fitLine[3],
  }
  extremePoints = getExtremePoints(contour)
  return {
    "pointNumber": pointNumber,
    "moments": moments,
    "area": area,
    "area_": area_,
    "center": center,
    "arcLength": arcLength,
    "approx": approx,
    "corners": corners,
    "approxLen": len(approx),
    "isContourConvex": isContourConvex,
    "convexHull": convexHull,
    "straightBoundingRectangle": boundingRect,
    "aspectRatio": aspectRatio,
    "extent": extent,
    "solidity": solidity,
    "equivalentDiameter": equivalentDiameter,
    "rotatedRectangle": box,
    "minimumEnclosingCircle": (mecCenter, mecRadius),
    "fittingEllipse": ellipse,
    "orientation": orientation,
    "fitLine": fitLine,
    "extremePoints": extremePoints,
  }


def drawRectangle(image, points, path1, path2="", color=(0, 0, 255), thickness=1):
  work = image.copy()
  if image.ndim == 2:
    work = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
  work = cv2.rectangle(work, (points["x"], points["y"]), (points["x"] + points["w"], points["y"] + points["h"]), color, thickness)
  path = path1
  if path2 != "":
    path = os.path.join(path1, path2)
  cv2.imwrite(path, work)
  return work, path


def drawCircle(image, cr, path1, path2="", color=(0, 0, 255), thickness=1):
  work = image.copy()
  if image.ndim == 2:
    work = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
  work = cv2.circle(work, cr[0], cr[1], color, thickness)
  path = path1
  if path2 != "":
    path = os.path.join(path1, path2)
  cv2.imwrite(path, work)
  return work, path


def drawEllipse(image, ellipse, path1, path2="", color=(0, 0, 255), thickness=1):
  work = image.copy()
  if image.ndim == 2:
    work = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
  work = cv2.ellipse(work, ellipse, color, thickness)
  path = path1
  if path2 != "":
    path = os.path.join(path1, path2)
  cv2.imwrite(path, work)
  return work, path


def drawFitLine(image, points, path1, path2="", color=(0, 0, 255), thickness=1):
  work = image.copy()
  if image.ndim == 2:
    work = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

  rows, cols = image.shape[:2]
  lefty = int((-points["x"] * points["vy"] / points["vx"]) + points["y"])
  righty = int(((cols - points["x"]) * points["vy"] / points["vx"]) + points["y"])
  work = cv2.line(work, (cols - 1, righty), (0, lefty), color, thickness)
  path = path1
  if path2 != "":
    path = os.path.join(path1, path2)
  cv2.imwrite(path, work)
  return work, path


def _tt1(allImage, image, path, allName, name, contour, color, thickness):
  all, path1 = drawContours(allImage, contour, path, allName, color, thickness)
  _, path2 = drawContours(image, contour, path, name, color, thickness)
  return all, [path1, path2]


def _tt2(allImage, image, path, allName, name, points, color, thickness):
  all, path1 = drawRectangle(allImage, points, path, allName, color, thickness)
  _, path2 = drawRectangle(image, points, path, name, color, thickness)
  return all, [path1, path2]


def _tt3(allImage, image, path, allName, name, cr, color, thickness):
  all, path1 = drawCircle(allImage, cr, path, allName, color, thickness)
  _, path2 = drawCircle(image, cr, path, name, color, thickness)
  return all, [path1, path2]


def _tt4(allImage, image, path, allName, name, ellipse, color, thickness):
  all, path1 = drawEllipse(allImage, ellipse, path, allName, color, thickness)
  _, path2 = drawEllipse(image, ellipse, path, name, color, thickness)
  return all, [path1, path2]


def _tt5(allImage, image, path, allName, name, points, color, thickness):
  all, path1 = drawFitLine(allImage, points, path, allName, color, thickness)
  _, path2 = drawFitLine(image, points, path, name, color, thickness)
  return all, [path1, path2]


def drawContourInfo(image, info, path, color=(255, 0, 0), thickness=1):
  all, names = _tt1(image, image, path, "all.png", "approx.png", [info["approx"]], color, thickness)
  all, temp = _tt2(all, image, path, "all.png", "straightBoundingRectangle.png", info["straightBoundingRectangle"], color, thickness)
  names.append(temp[-1])
  all, temp = _tt1(all, image, path, names[0], "rotatedRectangle.png", [info["rotatedRectangle"]], (0, 255, 0), thickness)
  names.append(temp[-1])
  all, temp = _tt3(all, image, path, names[0], "minimumEnclosingCircle.png", info["minimumEnclosingCircle"], color, thickness)
  names.append(temp[-1])
  all, temp = _tt4(all, image, path, names[0], "fittingEllipse.png", info["fittingEllipse"], color, thickness)
  names.append(temp[-1])
  all, temp = _tt5(all, image, path, names[0], "fitLine.png", info["fitLine"], color, thickness)
  names.append(temp[-1])
  return names


def rotateImage(image, angle, center=None, scale=1):
  image = image.copy()
  rows, cols = image.shape[:2]
  if center is None:
    center = ((cols - 1) / 2.0, (rows - 1) / 2.0)
  m = cv2.getRotationMatrix2D(center, angle, scale)
  image = cv2.warpAffine(image, m, (cols, rows))
  return image


def clipRectangleImage(image, rectangle, margin=0):
  x, y, w, h = rectangle
  top = y - margin
  bottom = y + h + margin
  left = x - margin
  right = x + w + margin
  return clipImage(image, top, bottom, left, right)


def clipImage(image, top, bottom, left, right):
  return image[top:bottom, left:right]


def writeImage(path, name, image):
  fullpath = os.path.join(path, name)
  cv2.imwrite(fullpath, image)
  return fullpath


# class RotatedRect:

#   def __init__(self, center=(0, 0), size=(0, 0), angle=0.0) -> None:
#     self.center = center
#     self.size = size
#     self.angle = angle

#   def draw(self):
#     pass
