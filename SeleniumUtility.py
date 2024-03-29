import datetime
import time
import logging
import os
import re

from bs4 import BeautifulSoup
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
# from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.common.exceptions import (
  UnexpectedAlertPresentException,
  NoAlertPresentException,
  # ElementNotVisibleException,
  TimeoutException,
  NoSuchElementException,
  ElementClickInterceptedException,
  ElementNotInteractableException,  # cSpell:disable-line
)

import Utility as U
import Javascript as JS
import Path

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


def getElementInfo(element, html=False, prettify=True):
  if not isinstance(element, webdriver.remote.webelement.WebElement):  #cspell: disable-line
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
    "cssDisplay": element.value_of_css_property("display"),
    # "css_display2": element.get_attribute("display"),
    # "css_display3": element.get_property("display"),
    "cssVisibility": element.value_of_css_property("visibility"),
    # "css_visibility2": element.get_attribute("visibility"),
    # "css_visibility3": element.get_property("visibility"),
    "cssDisplayed": element.is_enabled() and isDisplayed(element),
    "text": element.text,
    "textContext": element.get_attribute("textContent")
  }
  s = ""
  if html:
    s = BeautifulSoup(element.get_property('outerHTML'), 'lxml')
    if prettify:
      s = s.prettify()
  return info, s


def printElementInfo(element, html=False, prettify=True):
  i, h = getElementInfo(element, html, prettify)
  print(i)
  if h != "":
    print(h)


def strElementInfo(element, html=False, prittify=True):
  i, h = getElementInfo(element, html, prittify)
  return f"{i}\n{h}\n"


def takeScreenShot(driver, path, name="", ignore=True):
  os.makedirs(path, exist_ok=True)
  fileName = os.path.join(path, f"{name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
  try:
    result = driver.get_screenshot_as_file(fileName)
  except Exception:
    if ignore:
      return False
    raise
  return result


def outputSource(driver, path, name):
  os.makedirs(path, exist_ok=True)
  # source = element.get_attribute('innerHTML')
  source = driver.page_source
  fileName = os.path.join(path, f"{name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
  with open(fileName, mode="w", encoding="utf-8") as file:
    soup = BeautifulSoup(source, features="lxml")
    file.write(soup.prettify())


def isDriver(driver):
  if isinstance(driver, webdriver.remote.webdriver.WebDriver):
    return True
  #if isinstance(driver, webdriver.firefox.webdriver.WebDriver):
  #  return True
  #if isinstance(driver, webdriver.chrome.webdriver.WebDriver):
  #  return True
  return False


def isExistElement(driver, locator=(), element=None, state="enabled", wait=30, interval=0.5):
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
    elm, _ = getElementInfo(element)
    logger.error(f"{type(e)}: {e}, click: {elm}, {scroll}, {focus}, {ignore}")
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
def findClick(driver, locator=(), element=None, ignore=False, state="clickable", wait=30, interval=0.2, scroll=False, focus=True, retry=0, retryWait=1, debug=False):
  # printDebug(debug, "start findClick")
  try:
    element = findElement(driver, locator=locator, element=element, state=state, ignore=ignore, wait=wait, interval=interval)
    for _ in range(retry + 1):
      # printDebug(debug, f"findClick1 {_}: {element}")
      if element is not None:
        if retry == 0:
          click(element, scroll=scroll, focus=focus, ignore=ignore)
          return element
        else:
          # printDebug(debug, f"findClick {_}: start click")
          click(element, scroll=scroll, focus=focus, ignore=True)
          # printDebug(debug, f"findClick {_}: end click")
      time.sleep(retryWait)
      # printDebug(debug, f"findClick2 {_}: {element}")
      element = findElement(driver, locator=locator, element=element, state=state, ignore=True, wait=0, interval=interval)
      # printDebug(debug, f"findClick3 {_}: {element}")
      if element is None:
        return None

    #logger.debug(f"findClick: {locator}, must={must}, ignore={ignore}, state={state}, scroll={scroll}, focus={focus}")
    #logger.debug(f"{elementInfo(element)}")
    if ignore == True:
      return None
    raise ValueError

  except Exception as e:
    if ignore == True:
      return None
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


def getUserAgent(driver):
  GetUserAgent = """return navigator.userAgent"""
  userAgent = driver.execute_script(GetUserAgent)
  return {"User-Agent": userAgent}


def closeOtherTabs(driver, handle, sleep=1):
  if driver.window_handles == 1:
    return
  for h in driver.window_handles:
    driver.switch_to.window(h)
    if driver.current_window_handle != handle:
      driver.close()
      time.sleep(sleep)


def closeCurrentTab(driver, handle, sleep=1):
  if driver.window_handles == 1:
    return
  if driver.current_window_handle == handle:
    driver.close()
  for h in driver.window_handles:
    driver.switch_to.window(h)
    return


def getService(exePath=Path.GeckoDriverPath, logPath=os.path.devnull):
  return FirefoxService(executable_path=exePath, log_path=logPath)


def getOptions(firefoxPath=Path.FirefoxPath):
  options = FirefoxOptions()
  # options.add_argument('-headless')
  options.add_argument('-safe-mode')
  options.set_preference("browser.cache.disk.enable", False)
  options.binary_location = firefoxPath
  return options


def getDriver(service, options):
  try:
    return webdriver.Firefox(service=service, options=options)
  except TimeoutException:
    return None


def startFirefox(loadTimeout=300, retry=10, sleep=1):
  service = getService()
  options = getOptions()

  for _ in range(retry):
    driver = getDriver(service, options)
    if driver is not None:
      driver.set_page_load_timeout(loadTimeout)
      return driver
    time.sleep(sleep)
    raise ValueError


def waitUntilUrlChange(driver, currentUrl, reUrl=None, timeout=10):
  try:
    WebDriverWait(driver, timeout).until(lambda driver: currentUrl != driver.current_url if reUrl is None else reUrl.search(driver.current_url) is not None)
    print("ok")
  except TimeoutException:
    print("waitUntilUrlChange timeout")
    return False
  return True


  # 画面遷移する場合に使う
def goTo(driver, buttonBy=By.XPATH, buttonValue="", buttonElement=None, toBy=By.XPATH, toValue="", tryTimes=6, wait=10, interval=0.5, state="clickable"):
  for _ in range(tryTimes):
    if buttonElement is not None:
      click(buttonElement)
    else:
      findClick(driver, locator=(buttonBy, buttonValue), state=state, wait=wait, ignore=True)

    try:
      element = findElement(driver, locator=(toBy, toValue), state=state, wait=1, ignore=True)  # enabled?
      if element is not None:
        time.sleep(interval)
        return
    except (NoSuchElementException, TimeoutException):
      # logger.debug(f"goTo except: {buttonBy}:{buttonValue}, {buttonElement}, {toBy}:{toValue}, {tryTimes}, {wait}, {state}")
      continue
    except Exception as e:
      logger.warning(f"goTo retry: {type(e)}:{e}, {buttonBy}:{buttonValue}, {buttonElement}, {toBy}:{toValue}, {tryTimes}, {wait}, {state}")
  logger.error(f"goTo failed: {buttonBy}:{buttonValue}, {buttonElement}, {toBy}:{toValue}, {tryTimes}, {wait}, {state}")
  raise ValueError


def clickUntilCheckAttribute(driver, path, name, value, wait=10, element=None, scroll=False):
  target = findElement(driver, locator=(By.XPATH, path), element=element, state="enabled", wait=wait)
  attribute = target.get_attribute(name)
  for _ in range(10):
    # print(attribute)
    if re.search(value, attribute) is not None:
      return target
    time.sleep(1)
    target = findClick(driver, locator=(By.XPATH, path), element=element, state="enabled", wait=1, scroll=scroll)
    attribute = target.get_attribute(name)
  return None