import datetime
import time
import logging

from bs4 import BeautifulSoup
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
# from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
  UnexpectedAlertPresentException,
  NoAlertPresentException,
  ElementNotVisibleException,
  TimeoutException,
  NoSuchElementException,
  ElementClickInterceptedException,
  ElementNotInteractableException,
)

import Utility as U
import Javascript as JS

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def clickJavaScript(element):
  js = "arguments[0].click()"
  element.parent.execute_script(js, element)


def sendKeyPageDown(element):
  try:
    element.parent.execute_script(JS.KeyDownPageDown, element)
    time.sleep(0.1)
    element.parent.execute_script(JS.KeyUpPageDown, element)
    time.sleep(0.1)
  except Exception as e:
    print(type(e), e)
    logger.error(type(e), e)
    raise


def isDisplayed(element, limit=None):
  js = """\
  let element = arguments[0]
  let limit = arguments[1]
  while (element.nodeType === 1) {
    if (limit !== null && element === limit.parentNode) {
      return true;
    }
    style = window.getComputedStyle(element);
    if (
      style.getPropertyValue("display") === "none" ||
      style.getPropertyValue("visibility") === "hidden"
    ) {
      return false;
    }
      element = element.parentNode;
    }
    return true;
  """
  return element.parent.execute_script(js, element, limit)


def checkElementStateNoWait(element, state="enabled"):
  if state == "enabled":
    return element.is_enabled()
  elif state == "disabled":
    return not element.is_enabled()
  elif state == "selected":
    return element.is_selected()
  # elif state == "unselected":
  #   return not element.is_selected()
  elif state == "displayed":
    return element.is_displayed()
  elif state == "undisplayed":
    return not element.is_displayed()
  elif state == "clickable":
    return element.is_enabled() and element.is_displayed()
  elif state == "cssDisplayed":
    return element.is_enabled() and isDisplayed(element)
  else:
    return False


# 現状見つかったもののstateが条件に合っていないとFalseを返す
# 条件に合った最初のものを返すわけではない
class CheckState():

  def __init__(self, locator=(), element=None, state="enabled"):
    self.locator = locator
    self.element = element
    self.state = state

  def __call__(self, driver):
    try:
      if self.element is not None and self.locator == ():
        element = self.element
      elif self.element is not None and self.locator != ():
        element = self.element.find_element(*self.locator)
      elif self.locator != ():
        element = driver.find_element(*self.locator)
      else:
        return False

      return element if checkElementStateNoWait(element, self.state) else False
    except Exception as _:
      # logger.debug(f"CheckState: {type(_)}, {_}, {self.locator}, {self.element}, {self.state}")
      return False


def focusElement(element, preventScroll=False):
  js = """\
  arguments[0].focus({"preventScroll": arguments[1]})
  """
  element.parent.execute_script(js, element, preventScroll)


# start, center, end, nearest
def scrollIntoView(element, block="start", inline="nearest"):
  js = """\
  element = arguments[0]
  old = element.getBoundingClientRect()
  for(let i=0; i < 3; ++i){
    element.scrollIntoView(arguments[1])
    now = element.getBoundingClientRect()
    if (old.y !== now.y || old.x !== now.x){
      return true
    }
  }
  return false
  """
  return element.parent.execute_script(js, element, {"block": block, "inline": inline})


def getParentElement(element):
  js = """\
  return arguments[0].parentElement
  """
  return element.parent.execute_script(js, element)


def alertAccept(driver):
  try:
    #alert = driver.switch_to.alert()
    # alert.accept()
    Alert(driver).accept()
    return True
  except UnexpectedAlertPresentException:
    # print("UnexpectedAlertPresentException")
    return False
  except NoAlertPresentException:
    # print("NoAlertPresentException")
    return False


###


def addCookie(driver, cookies):
  for cookie in cookies:
    driver.add_cookie(cookie)


def elementInfo(element, html=False):
  if isinstance(element, webdriver.remote.webelement.WebElement) == False:  #cspell: disable-line
    # if isinstance(element, webdriver.firefox.webelement.FirefoxWebElement) == False:
    # and isinstance(element, webdriver.chrome.webelement.ChromeWebElement) == False:
    return None

  info = {
    "tag": element.tag_name,
    "id": element.get_attribute("id"),
    "class": element.get_attribute("class"),
    "enabled": element.is_enabled(),
    "selected": element.is_selected(),
    "displayed": element.is_displayed(),
    "css_display": element.value_of_css_property("display"),
    # "css_display2": element.get_attribute("display"),
    # "css_display3": element.get_property("display"),
    "css_visibility": element.value_of_css_property("visibility"),
    # "css_visibility2": element.get_attribute("visibility"),
    # "css_visibility3": element.get_property("visibility"),
  }
  if html == True:
    info["html"] = BeautifulSoup(element.get_property('outerHTML'), 'lxml')
  return info


def takeScreenShot(driver, name, ignore=True):
  fileName = "{}_{}.png".format(name, datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
  try:
    result = driver.get_screenshot_as_file(fileName)
  except Exception:
    if ignore:
      return False
    raise
  return result


def isDriver(driver):
  if isinstance(driver, webdriver.remote.webdriver.WebDriver):
    return True
  #if isinstance(driver, webdriver.firefox.webdriver.WebDriver):
  #  return True
  #if isinstance(driver, webdriver.chrome.webdriver.WebDriver):
  #  return True
  return False


def isExistElement(
    driver,
    locator=(),
    element=None,
    state="enabled",
    wait=30,
    interval=0.5,
):
  try:
    element = findElement(driver, locator=locator, element=element, state=state, wait=wait, interval=interval, ignore=True)
    if element is not None:
      return True
    return False
  except Exception as e:
    return False


#def isVisible(element):
#  if isInvisible(element, "display", "none") == True:
#    return False
#  if isInvisible(element, "visibility", "hidden") == True:
#    return False
#  return True
#
#
#def isInvisible(element, prop="display", value="none"):
#  e = element
#  if element.value_of_css_property(prop) == value:
#    logger.debug(f"invisible: {elementInfo(e)}")
#    return True
#  element = getParentElement(element)
#  while element is not None:
#    if element.value_of_css_property(prop) == value:
#      logger.debug(f"invisible: {elementInfo(e)}")
#      return True
#    element = getParentElement(element)
#  return False


def checkElementState(element, state="enabled", wait=30, interval=0.5):
  return U.waitFor(checkElementStateNoWait, {
    "element": element,
    "state": state,
  }, wait=wait, interval=interval)


# elementを取得する。見つけられなかったらraise。ただしignoreがTrueならばNoneを返す
def findElement(driver, locator=(), element=None, state="enabled", wait=30, interval=0.5, ignore=False):
  try:
    if element is None and locator == ():
      raise ValueError

    driverWait = WebDriverWait(driver, wait, interval)
    return driverWait.until(CheckState(locator=locator, element=element, state=state))

  except TimeoutException:
    if ignore == True:
      return None
    logger.error(f"findElement: {locator}, {element}, {state}, {wait}, {interval}, {ignore}")
    raise
  except Exception as e:
    if ignore == True:
      return None
    logger.error(f"findElement: {type(e)}, {e}")
    raise


def filterElements(elements, state="enabled"):
  result = []
  for element in elements:
    if checkElementStateNoWait(element, state) == True:
      result.append(element)
  return result


def findElements(driver, locator=(), element=None, state="enabled"):
  elements = []
  if element is not None and locator != ():
    elements = element.find_elements(*locator)
  elif locator != ():
    elements = driver.find_elements(*locator)

  if elements == []:
    return []
  return filterElements(elements, state)


def click(element, scroll=False, focus=True, ignore=False):
  try:
    if scroll == True:
      scrollIntoView(element, block="start")
      # if result == False:
      #   element.location_once_scrolled_into_view
    if focus == True:
      focusElement(element, preventScroll=not scroll)
    element.click()
  except (ElementClickInterceptedException, ElementNotInteractableException):  #cspell: disable-line
    clickJavaScript(element)
  except Exception as e:
    if ignore == True:
      return
    logger.error(f"{type(e)}: {e}, click: {elementInfo(element)}, {scroll}, {focus}, {ignore}")
    raise


def getElementText(element, content=True):
  if element is None:
    return ""
  if content:
    text = element.get_attribute("textContent")
  else:
    text = element.text
  if text is None:
    return ""
  return text


# import const

# def getNowTimeT():
#   return datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]

# def printT(string):
#   print(f"{getNowTimeT()}: {string}")


def printDebug(debug, string):
  if debug:
    U.printTime(string)


# retry はclickを繰り返すのであって、探すのを繰り返すわけではない
# enabledをretryする時は、よく考えないといけない
def findClick(driver, locator=(), element=None, ignore=False, state="clickable", wait=30, interval=0.5, scroll=False, focus=True, retry=0, debug=False):
  # printDebug(debug, "start findClick")
  try:
    element = findElement(driver, locator=locator, element=element, state=state, ignore=ignore, wait=wait, interval=interval)
    for _ in range(retry + 1):
      # printDebug(debug, f"findClick1 {_}: {element}")
      if element is not None:
        if retry == 0:
          click(element, scroll=scroll, focus=focus, ignore=ignore)
          return
        else:
          # printDebug(debug, f"findClick {_}: start click")
          click(element, scroll=scroll, focus=focus, ignore=True)
          # printDebug(debug, f"findClick {_}: end click")
      time.sleep(interval)
      # printDebug(debug, f"findClick2 {_}: {element}")
      element = findElement(driver, locator=locator, element=element, state=state, ignore=True, wait=0, interval=0)
      # printDebug(debug, f"findClick3 {_}: {element}")
      if element is None:
        return

    #logger.debug(f"findClick: {locator}, must={must}, ignore={ignore}, state={state}, scroll={scroll}, focus={focus}")
    #logger.debug(f"{elementInfo(element)}")
    if ignore == True:
      return
    raise ValueError

  except Exception as e:
    if ignore == True:
      return
    logger.error(f"findClick: {type(e)}, {e}, {locator}, ignore={ignore}, state={state}, scroll={scroll}, focus={focus}, retry={retry}")
    raise


def switchToIframe(driver, locator=(By.TAG_NAME, "iframe"), wait=60, interval=1, ignore=False):
  iframe = findElement(driver, locator=locator, wait=wait, interval=interval, ignore=ignore)
  if iframe is not None:
    driver.switch_to.frame(iframe)
  else:
    logger.error(f"switchIframe: {iframe}")


def getSession(driver):
  session = requests.session()
  for cookie in driver.get_cookies():
    session.cookies.set(cookie["name"], cookie["value"])
  return session
