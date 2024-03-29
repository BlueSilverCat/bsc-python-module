from operator import sub
import re
import os
import functools
import statistics
from ctypes import Structure, c_long, byref
if os.name == "nt":
  from ctypes import windll
import unicodedata
import time
import random

import requests
import psutil

import TimeUtility as TU
from VirtualTerminalSequences import VTS

# cSpell: words backslashreplace surrogateescape xmlcharrefreplace surrogatepass namereplace

VTS.enable()

########################################################################################################################
## Print
########################################################################################################################


# 現在時刻付きprint
def printTime(string):
  print(f"{TU.getNowTime()}: {string}")


def printList(lt, color=True):
  length = len(lt)
  maxLen = len(str(length))
  if color:
    VTS.enable()
  for i, x in enumerate(lt):
    if color:
      message = [
        (f"{i:>{maxLen}}", "black", "white"),
        (" : ", "", ""),
        (f"{x}", "", ""),
      ]
      VTS.printColoredList(message)
    else:
      print(f"{i:>{maxLen}} : {x}")


def printDict(d, color=True, fc="black", bc="gray", end="\n", indent=0):
  if color:
    VTS.enable()
  maxLen = getMaxLen(d)
  for key, value in d.items():
    if color:
      message = [
        (f" " * indent, "", ""),
        (f"{key:<{maxLen}}", fc, bc),
        (" : ", "", ""),
        (f" {value}", "", ""),
      ]
      VTS.printColoredList(message, end=end)
    else:
      print(f"{' ' * indent}{key:<{maxLen}}: {value}", end=end)
  if end != "\n":
    print("")


def printDictList(lt, color=True, lfc="gray", lbc="black", bfc="black", bbc="gray", end="\n"):
  length = len(lt)
  maxLen = len(str(length))
  if color:
    VTS.enable()
  for i, x in enumerate(lt):
    if color:
      message = [
        (f"{i:>{maxLen}}", lfc, lbc),
        (" : ", "", ""),
      ]
      VTS.printColoredList(message)
    else:
      print(f"{i:>{maxLen}}:")
    printDict(x, color, indent=2, fc=bfc, bc=bbc, end=end)


def printDir(obj):
  for attr in dir(obj):
    print(f"{attr}: {getattr(obj, attr)}")


def printMember(v, pat=None):
  members = dir(v)
  for member in members:
    if pat and pat.search(member) is not None:
      print(member)
    else:
      print(member)


def printType(x):
  print(f"{type(x)}: {x}")


def printLen(x):
  print(f"{len(x):3}: {x}")


# debug
def checkUnpack(*args):
  for arg in args:
    print(arg)


# リストのインデックスを文字列にする。インデックスを表示させたい時に使う。
def getListIndices(lt, s=0):
  if len(lt) == 0:
    return "><"
  maxLen = len(str(max(lt)))
  text = functools.reduce(lambda x, y: x + y, [f"{i+s:{maxLen}}, " for i, x in enumerate(lt)], ">")
  return f"{text[:-2]}<"


# リストの中身を等間隔にした文字列にする。表示させたい時に使う。
def listToFormattedString(lt):
  if len(lt) == 0:
    return "[]"
  maxLen = len(str(max(lt)))
  text = functools.reduce(lambda x, y: x + y, [f"{x:{maxLen}}, " for x in lt], "[")
  return f"{text[:-2]}]"


def printStatistics(lt, fmt=" .10f"):
  print(f"{lt}")
  print(f"合計      : {sum(lt):{fmt}}")
  print(f"平均      : {statistics.mean(lt):{fmt}}")
  print(f"中央値    : {statistics.median(lt):{fmt}}")
  print(f"最頻値    : {statistics.mode(lt):{fmt}}")
  print(f"母標準偏差: {statistics.pstdev(lt):{fmt}}")
  print(f"母分散    : {statistics.pvariance(lt):{fmt}}")


def printDiffStatistics(lt1, lt2, fmt=" .10f"):
  print(f"{lt1}\n{lt2}")
  print(list(map(sub, lt1, lt2)))
  print(f"合計      : {sum(lt1):{fmt}}, {sum(lt2):{fmt}}, {sum(lt1) - sum(lt2):{fmt}}")
  print(f"平均      : {statistics.mean(lt1):{fmt}}, {statistics.mean(lt2):{fmt}}, {statistics.mean(lt1) - statistics.mean(lt2):{fmt}}")
  print(f"中央値    : {statistics.median(lt1):{fmt}}, {statistics.median(lt2):{fmt}}, {statistics.median(lt1) - statistics.median(lt2):{fmt}}")
  print(f"最頻値    : {statistics.mode(lt1):{fmt}}, {statistics.mode(lt2):{fmt}}, {statistics.mode(lt1) - statistics.mode(lt2):{fmt}}")
  print(f"母標準偏差: {statistics.pstdev(lt1):{fmt}}, {statistics.pstdev(lt2):{fmt}}, {statistics.pstdev(lt1) - statistics.pstdev(lt2):{fmt}}")
  print(f"母分散    : {statistics.pvariance(lt1):{fmt}}, {statistics.pvariance(lt2):{fmt}}, {statistics.pvariance(lt1) - statistics.pvariance(lt2):{fmt}}")


# def printMembers(obj):
#   members = inspect.getmembers(obj)
#   for member in members:
#     print("{}".format(toString(member)))

########################################################################################################################
## Utility
########################################################################################################################


class POINT(Structure):
  _fields_ = [
    ("x", c_long),
    ("y", c_long),
  ]


def getMousePosition():
  if os.name != "nt":
    return None
  pt = POINT()
  windll.user32.GetCursorPos(byref(pt))
  # return {"x": pt.x, "y": pt.y}
  return (pt.x, pt.y)


########################################################################################################################
## Iterator
########################################################################################################################


def uniqueFilter(lt):
  length = len(lt)
  return [lt[i] for i in range(length) if lt.index(lt[i]) == i]


def uniqueFilter2(lt, fn=None):
  work = lt[:]
  result = []
  while work:
    t = work.pop(0)
    result.append(t)
    if fn is None:
      work = [x for x in work if x != t]
    else:
      work = [x for x in work if not fn(x, t)]
  return result


def duplicateFilter(lt, fn=None):
  work = lt[:]
  result = []
  n = 0
  while work:
    t = work.pop(0)
    for x in work:
      n += 1
      if fn is None and x == t or fn is not None and fn(x, t):
        work.remove(x)
        result.append(x)
  print(n)
  return result


def getSameIndices(lt, value, fn=None):
  result = []
  length = len(lt)
  for i in range(length):
    if fn is None and lt[i] == value:
      result.append(i)
    elif fn and fn(lt[i], value):
      result.append(i)
  return result


def deleteDuplicate(lt, fn=None):
  indices = []
  result = lt[:]
  i = 0
  while i < len(result):
    indices = getSameIndices(result, result[i], fn)
    result = excludeIndices(result, indices[1:])
    i += 1
  return result


# リストから指定したインデックスのリストを返す
def includeIndices(lt, indices):
  return [x for i, x in enumerate(lt) if i in indices]


# リストから指定したインデックスを除いたリストを返す
def excludeIndices(lt, indices):
  return [x for i, x in enumerate(lt) if i not in indices]


# リストから指定した値を除いたリストを返す
def excludeValues(lt, values):
  return [v for i, v in enumerate(lt) if v not in values]
  # return list(filter(lambda x: x not in values, lt))


def filterIndex(condition, lt):
  return [i for i, x in enumerate(lt) if condition(i, x)]


# listの要素の最大の長さを返す
def getMaxLen(lt):
  return max(map(len, lt))


# indexが存在しない場合にdefaultを返す。
def getFromList(lt, index, default=None):
  try:
    return lt[index]
  except IndexError:
    return default


########################################################################################################################
## String
########################################################################################################################


def removeAllLineBreak(string, repl=""):
  reLF = re.compile("\n")
  reCR = re.compile("\r")
  string = reLF.sub(repl, string)
  string = reCR.sub("", string)
  return string


def removeLineBreak(string, linebreak="\n"):
  return string.rstrip(linebreak)


def checkTailLineBreak(string):
  if string.endswith("\r\n"):
    return "\r\n"
  if string.endswith("\n"):
    return "\n"
  return ""


# 区切り文字付きsplit
def split(string, separator="\n", replacer="\n"):  # replacer="↲"
  if string == "":
    return [string]
  work = string.split(separator)
  for i in range(len(work) - 1):
    work[i] += replacer
  # if work[len(work) - 1] == "":
  #   work.pop()
  return work


def getZeroFillNumberString(i, maxNum, minLength=0):
  length = len(str(maxNum))
  if length < minLength:
    length = minLength
  return str(i).zfill(length)


def insertLineBreak(string):
  regex = re.compile(r"(?<![Mm][Rr])(?<!\.)([:.]|\.\.\.) ")
  return regex.sub(r"\1\n", string)


def replaceLineBreak(string, repl="_"):
  regex = re.compile(r"[\r\n]")
  return regex.sub(repl, string)


# def toString(tup):
#   str = ""
#   for v in tup:
#     str += "{}, ".format(v)
#   str += "\n"
#   return str


# 複数行にわたる文字列を結合する
def concatenateMultiLines(string1, string2, con=" ", sep="\n"):
  s1 = string1.split(sep)
  s2 = string2.split(sep)
  length = len(s1) if len(s1) > len(s2) else len(s2)
  output = ""
  ls1 = getMaxLen(s1)
  for i in range(length):
    output += f"{getFromList(s1, i, ''): <{ls1}}{con}{getFromList(s2, i, '')}\n"
  return output[:-1]


########################################################################################################################
## file
########################################################################################################################


def getFileNumber(path):
  return sum(os.path.isfile(os.path.join(path, name)) for name in os.listdir(path))


def getDirectoryNumber(path):
  return sum(os.path.isdir(os.path.join(path, name)) for name in os.listdir(path))


def getLineBreak(string):
  crlfCount = string.count("\r\n")
  lfCount = string.count("\n")
  return "\r\n" if crlfCount != 0 and crlfCount == lfCount else "\n"


def makeDir(path):
  if not os.path.exists(path):
    os.makedirs(path)
    return True
  return False


def checkFileName(path, makeDir=False):
  if makeDir:
    parrent = os.path.split(path)[1]
    makeDir(parrent)

  if not os.path.exists(path):
    return path
  root, ext = os.path.splitext(path)
  i = 1
  while True:
    suffix = getZeroFillNumberString(i, 0, 2)
    name = f"{root}_{suffix}{ext}"
    if not os.path.exists(name):
      return name
    i += 1


# Windowsの名前に使えない文字を置き換える
def escapeFileName(path, repl="_"):
  regex = re.compile("[/:*?\"<>|.]")
  return regex.sub(repl, path)


# ディレクトリ配下の全てのファイルのフルパスを返す。
def getAllFiles(path, include="", exclude="", recursive=True):
  result = []
  lt = os.listdir(path)
  for i in lt:
    i = os.path.join(path, i)
    if recursive and os.path.isdir(i):
      lt += os.listdir(i)
      continue
    if exclude != "" and re.search(exclude, i):
      continue
    if include == "" or re.search(include, i):
      result.append(i)
  return result


# return directory, name, extension
def splitPath(path):
  directory, name = os.path.split(path)
  root, ext = os.path.splitext(name)
  return directory, root, ext


################################################################################
## Unicode
################################################################################


def unicodeInfo(c):
  output = f"version= {unicodedata.unidata_version}\n"
  output += f"code_point= U+{ord(c):04X}({ord(c):,})\n"
  output += f"name= {unicodedata.name(c, 'none')}\n"
  output += f"category= {unicodedata.category(c)}\n"
  output += f"decimal= {unicodedata.decimal(c, 'none')}\n"
  output += f"digit= {unicodedata.digit(c, 'none')}\n"
  output += f"numeric= {unicodedata.numeric(c, 'none')}\n"
  output += f"bidirectional= {unicodedata.bidirectional(c)}\n"
  output += f"combining= {unicodedata.combining(c)}\n"
  output += f"east_asian_width= {unicodedata.east_asian_width(c)}\n"
  output += f"mirrored= {unicodedata.mirrored(c)}\n"
  output += f"decomposition= {unicodedata.decomposition(c)}\n"  # code point
  output += isNormalized(c)
  print(output)
  return output


def isNormalized(string):
  output = ""
  output += f"normalize(NFC)= {unicodedata.normalize('NFC', string)}\n"  # string
  output += f"normalize(NFKC)= {unicodedata.normalize('NFKC', string)}\n"
  output += f"normalize(NFD)= {unicodedata.normalize('NFD', string)}\n"
  output += f"normalize(NFKD)= {unicodedata.normalize('NFKD', string)}\n"
  output += f"is_normalized(NFC)= {unicodedata.is_normalized('NFC', string)}\n"
  output += f"is_normalized(NFKC)= {unicodedata.is_normalized('NFKC', string)}\n"
  output += f"is_normalized(NFD)= {unicodedata.is_normalized('NFD', string)}\n"
  output += f"is_normalized(NFKD)= {unicodedata.is_normalized('NFKD', string)}\n"
  return output


# east_asian_width あまり当てにならない
def getEaWidth(c):
  eaw = unicodedata.east_asian_width(c)
  if eaw == "N" or eaw == "Na" or eaw == "H":
    return 1
  elif eaw == "W" or eaw == "F" or eaw == "A":
    return 2
  else:
    return 1


def getStringEaWidth(string):
  return sum(map(getEaWidth, string))


def getCategory(c):
  return unicodedata.category(c)


ControlCharacters = {
  "\u0000": "\u2400",  # NUL
  "\u0001": "\u2401",  # SOH
  "\u0002": "\u2402",  # STX
  "\u0003": "\u2403",  # ETX
  "\u0004": "\u2404",  # EOT
  "\u0005": "\u2405",  # ENQ
  "\u0006": "\u2406",  # ACK
  "\u0007": "\u2407",  # BEL
  "\u0008": "\u2408",  # BS
  "\u0009": "\u2409",  # HT
  "\u000A": "\u240A",  # LF
  "\u000B": "\u240B",  # VT
  "\u000C": "\u240C",  # FF
  "\u000D": "\u240D",  # CR
  "\u000E": "\u240E",  # SO
  "\u000F": "\u240F",  # SI
  "\u0010": "\u2410",  # DLE
  "\u0011": "\u2411",  # DC1
  "\u0012": "\u2412",  # DC2
  "\u0013": "\u2413",  # DC3
  "\u0014": "\u2414",  # DC4
  "\u0015": "\u2415",  # NAK
  "\u0016": "\u2416",  # SYN
  "\u0017": "\u2417",  # ETB
  "\u0018": "\u2418",  # CAN
  "\u0019": "\u2419",  # EOM
  "\u001A": "\u241A",  # SUB
  "\u001B": "\u241B",  # ESC
  "\u001C": "\u241C",  # FS
  "\u001D": "\u241D",  # GS
  "\u001E": "\u241E",  # RS
  "\u001F": "\u241F",  # US
  #"\u0020": "\u2420",  # SP
  "\u007F": "\u2421",  # DEL
}


def replaceControl(c, repl="_"):
  if unicodedata.category(c) == "Cc":
    return ControlCharacters.get(c, repl)
  return c


def replaceControls(string, repl="_"):
  replace = functools.partial(replaceControl, repl=repl)
  return "".join(list(map(replace, string)))


def testDecode(b):
  print(f"ignore= {b.decode('utf-8', errors='ignore')}")
  print(f"replace= {b.decode('utf-8', errors='replace')}")
  print(f"backslashreplace= {b.decode('utf-8', errors='backslashreplace')}")
  print(f"surrogateescape= {b.decode('utf-8', errors='surrogateescape')}")
  # print(f"surrogatepass= {b.decode('utf-8', errors='surrogatepass')}") # U+D800 - U+DFFF


def testEncode(c):
  print(f"ignore= {c.encode('utf-8', errors='ignore')}")
  print(f"replace= {c.encode('utf-8', errors='replace')}")
  print(f"backslashreplace= {c.encode('utf-8', errors='backslashreplace')}")
  print(f"surrogateescape= {c.encode('utf-8', errors='surrogateescape')}")
  print(f"xmlcharrefreplace= {c.encode('utf-8', errors='xmlcharrefreplace')}")
  print(f"namereplace= {c.encode('utf-8', errors='namereplace')}")
  # print(f"surrogatepass= {c.encode('utf-8', errors='surrogatepass')}") # U+D800 - U+DFFF


def splitEaWidth(string, width):
  result = ""
  l = len(string)
  w = 0
  for i in range(l):
    result += string[i]
    w += getEaWidth(string[i])
    if w >= width:
      return result, string[i + 1:]
  return string, ""


################################################################################
## Func
################################################################################


# Unpacking Argument Lists
# Noneは渡せない
def unpackFunc(func, arg=None):
  if arg is None:
    return func()
  if isinstance(arg, dict):
    return func(**arg)
  elif hasattr(arg, "__iter__"):
    return func(*arg)
  else:
    return func(arg)


# funcがvalueを返すまで一定時間待つ
def waitFor(func, funcArgs=None, ret=True, wait=5, interval=0.5):
  start = time.time()
  result = unpackFunc(func, funcArgs)
  while result != ret:
    if time.time() - start > wait:
      return None
    time.sleep(interval)
    result = unpackFunc(func, funcArgs)
  return result


def returnValueIfNone(target, value=0):
  if target is None:
    return value
  return target


def subLimitZero(x, y):
  x -= y
  if x < 0:
    return 0
  return x


def outputImage(path, imgData):
  with open(path, mode="wb") as file:
    file.write(imgData)


def getImage(url, headers=None, session=None):
  if session is None:
    session = requests.session()
  for _ in range(5):
    try:
      res = session.get(url, timeout=60, headers=headers)
      return res.content
    except Exception as e:
      pass
  return None


def deleteSpace(string, char=""):
  r = re.compile(" ")
  return r.sub(char, string)


def escapePathName(string, char="_"):
  r1 = re.compile(r'[\\/:*?"<>|]')
  r2 = re.compile(r'[.]')
  temp = r1.sub(char, string)
  return r2.sub("", temp)


# windows: [psutil.REALTIME_PRIORITY_CLASS, psutil.HIGH_PRIORITY_CLASS, psutil.ABOVE_NORMAL_PRIORITY_CLASS, psutil.NORMAL_PRIORITY_CLASS, psutil.BELOW_NORMAL_PRIORITY_CLASS, psutil.IDLE_PRIORITY_CLASS]
# linux: -20 to 20. max priority is -20
def setPriority(priority, pid=None):
  process = psutil.Process(pid)
  process.nice(priority)


################################################################################
## Random
################################################################################


def getRandom(minN, maxN):
  return random.randrange(minN, maxN)


def getRandomStr(string="abcdefghijklmnopqrstuvwxyz", rMin=1, rMax=10):
  return "".join(random.choices(string, k=random.randint(rMin, rMax)))


################################################################################
##
################################################################################


def confirm(msg="confirm? [y/n] "):
  result = input(msg).strip().lower()
  reCheck = re.compile(r"^(yes|y)$")
  if reCheck.search(result):
    return True
  return False
