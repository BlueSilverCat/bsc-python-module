import time
import functools
import TimeUtility
import gc


# 関数名と起動時刻の表示
def printName(func):

  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    print(f"{func.__name__}: {TimeUtility.getNowTime()}")
    result = func(*args, **kwargs)
    return result

  return wrapper


# 実行時間の表示
def stopwatchPrint(func):

  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    gc.collect()
    gc.disable()
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    diff = end - start
    print(f"{func.__name__}: {TimeUtility.secToTime(diff)}({diff:.3f})")
    gc.enable()
    return result

  return wrapper


def stopwatchPrintSE(func):

  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    gc.collect()
    gc.disable()
    print(f"{TimeUtility.getNowTime()} - Start {func.__name__}")
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    diff = end - start
    print(f"{TimeUtility.getNowTime()} - End   {func.__name__} {TimeUtility.secToTime(diff)}({diff:.3f})")
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