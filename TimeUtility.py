import time
import datetime
import re
import math

Iso8601Basic = "%Y%m%dT%H%M%S%z"
Iso8601Extended = "%Y-%m-%dT%H:%M:%S"  # [+-]hh:mm


# 現在時刻を取得
def getNowTime():
  return datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
  # return time.strftime("%H:%M:%S")


# 現在の日付を取得 datetime.isoformat()
def getDateTime(fmt="basic"):
  if fmt == "basic":
    return time.strftime(Iso8601Basic)
  elif fmt == "extended":
    reTimeZone = re.compile("([+-]\\d\\d)(\\d\\d)")
    timeZone = reTimeZone.sub("\\1:\\2", time.strftime("%z"))
    return time.strftime(f"{Iso8601Extended}{timeZone}")


def epochToStr(e, fmt="basic"):
  if fmt == "basic":
    return time.strftime(Iso8601Basic, time.localtime(e))  # gmtime()を使う場合は、tm_gmtoffを加算する
  elif fmt == "extended":
    timeStr = time.strftime(Iso8601Extended, time.localtime(e))
    reTimeZone = re.compile("([+-]\\d\\d)(\\d\\d)$")
    timeZone = time.strftime("%z", time.localtime(e))
    timeZone = reTimeZone.sub("\\1:\\2", timeZone)
    return timeStr + timeZone


def strToEpoch(string, fmt="basic"):
  if fmt == "basic":
    return time.mktime(time.strptime(string, Iso8601Basic))
  elif fmt == "extended":
    reTimeZone = re.compile("(.+)([+-]\\d\\d):(\\d\\d)$")
    timeStr = reTimeZone.sub("\\1\\2\\3", string)
    return time.mktime(time.strptime(timeStr, f"{Iso8601Extended}%z"))


def timeToLocalTime(t):
  return time.strftime("%H:%M:%S", time.localtime(t))


# 次の時刻の開始までの時間を取得
# addition = sec
def getNextHourWait(addition=0):
  now = datetime.datetime.now()
  wait = 3600 - (now.minute * 60 + now.second + now.microsecond * 10**-6)
  return time.time() + wait + addition


def secToTime(sec):
  work = float(sec)
  day, work = divmod(work, 3600 * 24)
  h, work = divmod(work, 3600)
  m, work = divmod(work, 60)
  s = work
  f, _ = math.modf(work)
  output = f"{h:0>2.0f}:{m:0>2.0f}"
  if f > 0:
    output = output + f":{s:0>6.3f}"
  else:
    output = output + f":{s:0>2.0f}"
  if day > 0:
    output = f"{day:.0f}" + output
  return output


# 時刻差がdelta以上ならばTrue
# datetime.timedelta(hours=9)は、JST 日本標準時 UTC+0900
def compareTime(dt1, dt2, delta, timeZone=datetime.timedelta(hours=9)):
  return abs(dt1 - dt2) > abs(delta)


def convertUTCtoJST(dt):
  return dt.astimezone(datetime.timezone(datetime.timedelta(hours=9)))
