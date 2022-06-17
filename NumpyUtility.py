import functools

import numpy as np


def npInfo(array, showData=True, printContent=True, eol=True):
  output = f"shape={array.shape}, dim={np.ndim(array)}, size={array.size} dtype={array.dtype} type={type(array)}\n"
  output += functools.reduce(lambda x, y: f"{x.strip()}, {y.strip()}", str(array.flags).split("\n")) + "\n"
  if array.base is not None:
    output += "base exists.\n"
  if showData:
    output += str(array)
  if eol:
    output += "\n"
  if printContent:
    print(output)
  return output


def getShape(array):
  return [array.shape[0], array.shape[1]]


def printMatrix(array, eol=True):
  l = len(str(np.amax(array))) + 1
  np.set_printoptions(formatter={"int": lambda x: f"{x:{l}}"})
  height, width = getShape(array)
  if np.ndim(array) == 3:
    for y in range(height):
      output = ""
      for x in range(width):
        output += str(array[y][x]) + " "
      print(output)
  if np.ndim(array) == 2:
    for y in range(height):
      print(str(array[y]))
  if eol:
    print("\n")


def getNonzeroZip(array, values=None):
  if values is None:
    return getZipped(np.nonzero(array))
  return getZipped(np.nonzero(array), values)


def getZippedFlat(array, values=None):
  if len(array) == 2:
    if values is None:
      return list(zip(array[0], array[1]))
    return list(zip(array[0], array[1], values))
  if len(array) == 3:
    if values is None:
      return list(zip(array[0], array[1], array[2]))
    return list(zip(array[0], array[1], array[2], values))
  return None


def getZipped(array, values=None):
  if len(array) == 2:
    indices = zip(array[0], array[1])
    if values is None:
      return list(indices)
    return list(zip(indices, values))
  if len(array) == 3:
    indices = zip(array[0], array[1], array[2])
    if values is None:
      return list(indices)
    return list(zip(indices, values))
  return None
