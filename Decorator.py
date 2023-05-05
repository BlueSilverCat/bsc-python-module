import time
import functools
import gc

import TimeUtility as TU
import Utility as U


# 関数名と起動時刻の表示
def printName(func):

  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    print(f"{func.__name__}: {TU.getNowTime()}")
    result = func(*args, **kwargs)
    return result

  return wrapper


# 実行時間の表示
def printExecutionTime(func):

  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    gc.collect()
    gc.disable()
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    diff = end - start
    print(f"{func.__name__}: {TU.secToTime(diff)}({diff:.3f})")
    gc.enable()
    return result

  return wrapper


def printStartEndExecuteTime(func):

  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    gc.collect()
    gc.disable()
    print(f"{TU.getNowTime()} - Start {func.__name__}")
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    diff = end - start
    print(f"{TU.getNowTime()} - End   {func.__name__} {TU.secToTime(diff)}({diff:.3f})")
    gc.enable()
    return result

  return wrapper


def stopwatchProcessPrint(func):

  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    gc.collect()
    gc.disable()
    start = time.process_time()
    result = func(*args, **kwargs)
    end = time.process_time()
    print(f"{func.__name__}: {end - start:.3f} s.")
    gc.enable()
    return result

  return wrapper


def stopwatchThreadPrint(func):

  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    gc.collect()
    gc.disable()
    start = time.thread_time()
    result = func(*args, **kwargs)
    end = time.thread_time()
    print(f"{func.__name__}: {end - start:.3f} s.")
    gc.enable()
    return result

  return wrapper


def gcDisable(func):
  """gc.collect() -> gc.disable() -> func -> gc.enable()"""

  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    gc.collect()
    gc.disable()
    result = func(*args, **kwargs)
    gc.enable()
    return result

  return wrapper


def gcCollect(func):
  """gc.collect() -> func"""

  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    gc.collect()
    result = func(*args, **kwargs)
    return result

  return wrapper


def printFunc(func):

  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    result = func(*args, **kwargs)
    print(f"name: {func.__name__}, args:{args}, kwargs:{kwargs}, result: {result}")
    if result is not None:
      return result

  return wrapper


def printStartEndTime(func):

  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    U.printTime(f"start: {func.__name__}")
    result = func(*args, **kwargs)
    U.printTime(f"end: {func.__name__}")
    if result is not None:
      return result

  return wrapper


def getExecuteTime(func):

  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    if result is not None:
      return [end - start, result]
    return end - start

  return wrapper
