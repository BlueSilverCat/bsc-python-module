import os
from ctypes import wintypes, byref

if os.name == "nt":
  from ctypes import windll

####################################################################################################
# VirtualTerminalSequences
####################################################################################################


class VTS:
  RESET = "\x1b[0m"  # reset
  BOLD = "\x1b[1m"
  UNDERLINE = "\x1b[4m"
  REVERSE = "\x1b[07m"  # reverse foreground and background colors
  UNDERLINE_OFF = "\x1b[24m"
  REVERSE_OFF = "\x1b[27m"
  FOREGROUND_COLORS = {
    "BLACK": "\x1b[30m",
    "RED": "\x1b[31m",
    "GREEN": "\x1b[32m",
    "YELLOW": "\x1b[33m",
    "BLUE": "\x1b[34m",
    "MAGENTA": "\x1b[35m",
    "CYAN": "\x1b[36m",
    "WHITE": "\x1b[37m",
    "DEFAULT_COLOR": "\x1b[39m",
    "GRAY": "\x1b[90m",
    "BRIGHT_RED": "\x1b[91m",
    "BRIGHT_GREEN": "\x1b[92m",
    "BRIGHT_YELLOW": "\x1b[93m",
    "BRIGHT_BLUE": "\x1b[94m",
    "BRIGHT_MAGENTA": "\x1b[95m",
    "BRIGHT_CYAN": "\x1b[96m",
    "BRIGHT_WHITE": "\x1b[97m",
  }
  FC = FOREGROUND_COLORS
  BACKGROUND_COLORS = {
    "BLACK": "\x1b[40m",
    "RED": "\x1b[41m",
    "GREEN": "\x1b[42m",
    "YELLOW": "\x1b[43m",
    "BLUE": "\x1b[44m",
    "MAGENTA": "\x1b[45m",
    "CYAN": "\x1b[46m",
    "WHITE": "\x1b[47m",
    "DEFAULT_COLOR": "\x1b[49m",
    "GRAY": "\x1b[100m",
    "BRIGHT_RED": "\x1b[101m",
    "BRIGHT_GREEN": "\x1b[102m",
    "BRIGHT_YELLOW": "\x1b[103m",
    "BRIGHT_BLUE": "\x1b[104m",
    "BRIGHT_MAGENTA": "\x1b[105m",
    "BRIGHT_CYAN": "\x1b[106m",
    "BRIGHT_WHITE": "\x1b[107m",
  }
  BC = BACKGROUND_COLORS

  INVALID_HANDLE_VALUE = -1
  STD_OUTPUT_HANDLE = -11
  STD_ERROR_HANDLE = -12
  ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
  ENABLE_LVB_GRID_WORLDWIDE = 0x0010

  @staticmethod
  def enable():
    if os.name != "nt":
      return True
    hOut = windll.kernel32.GetStdHandle(VTS.STD_OUTPUT_HANDLE)
    if hOut == VTS.INVALID_HANDLE_VALUE:
      return False
    dwMode = wintypes.DWORD()
    if windll.kernel32.GetConsoleMode(hOut, byref(dwMode)) == 0:
      return False
    dwMode.value |= VTS.ENABLE_VIRTUAL_TERMINAL_PROCESSING
    # dwMode.value |= ENABLE_LVB_GRID_WORLDWIDE
    if windll.kernel32.SetConsoleMode(hOut, dwMode) == 0:
      return False
    return True

  @staticmethod
  def reset():
    print(VTS.RESET)

  @staticmethod
  def isTupleOrList(x):
    return isinstance(x, tuple) or isinstance(x, list)

  @staticmethod
  def exchange(name):
    name = name.upper()
    match name:
      case "BK":
        return "BLACK"
      case "R":
        return "RED"
      case "G":
        return "GREEN"
      case "Y":
        return "YELLOW"
      case "B":
        return "BLUE"
      case "M":
        return "MAGENTA"
      case "C":
        return "CYAN"
      case "W":
        return "WHITE"
      case "GY":
        return "GRAY"
      case "BR" | "B_R":
        return "BRIGHT_RED"
      case "BG" | "B_G":
        return "BRIGHT_GREEN"
      case "BY" | "B_Y":
        return "BRIGHT_YELLOW"
      case "BB" | "B_B":
        return "BRIGHT_BLUE"
      case "BM" | "_BM":
        return "BRIGHT_MAGENTA"
      case "BC" | "BC":
        return "BRIGHT_CYAN"
      case "BW" | "BW":
        return "BRIGHT_WHITE"
      case _:
        return name

  @staticmethod
  def printColored(msg, fc="DEFAULT_COLOR", bc="DEFAULT_COLOR", end="\n"):
    print(VTS.getColorMessage(msg, fc, bc), end=end)

  # lt = "[(msg, fc, bc), (msg, fc, bc), ...]""
  @staticmethod
  def printColoredList(lt, end="\n"):
    for data in lt:
      print(VTS.getColorMessage(*data), end="")
    print("", end=end)

  @staticmethod
  def getColor(value="DEFAULT_COLOR", isBc=False):
    if isinstance(value, str):
      return VTS._getColorName(value, isBc)
    elif isinstance(value, int):
      return VTS._getColorNumber(value, isBc)
    elif VTS.isTupleOrList(value) and len(value) == 3:
      return VTS._getColorRGB(*value, isBc)
    else:
      return VTS._getDefaultColor(isBc)

  @staticmethod
  def _getDefaultColor(isBc=False):
    if isBc:
      return VTS.BACKGROUND_COLORS["DEFAULT_COLOR"]
    return VTS.FOREGROUND_COLORS["DEFAULT_COLOR"]

  @staticmethod
  def _getColorName(name="DEFAULT_COLOR", isBc=False):
    name = name.upper()
    name = VTS.exchange(name)
    if isBc:
      return VTS.BACKGROUND_COLORS.get(name, VTS.BACKGROUND_COLORS["DEFAULT_COLOR"])
    return VTS.FOREGROUND_COLORS.get(name, VTS.FOREGROUND_COLORS["DEFAULT_COLOR"])

  @staticmethod
  def _getColorNumber(n, isBc=False):
    if n < 0 and n > 255:
      return VTS._getDefaultColor(isBc)
    if isBc:
      return f"\x1b[48;5;{n}m"
    return f"\x1b[38;5;{n}m"

  @staticmethod
  def _getColorRGB(r, g, b, isBc=False):
    if r < 0 and r > 255 and g < 0 and g > 255 and b < 0 and b > 255:
      return VTS._getDefaultColor(isBc)
    if isBc:
      return f"\x1b[48;2;{r};{g};{b}m"
    return f"\x1b[38;2;{r};{g};{b}m"

  @staticmethod
  def getColorMessage(msg, fc="DEFAULT_COLOR", bc="DEFAULT_COLOR", reset=True):
    msg = f"{VTS.getColor(fc, False)}{VTS.getColor(bc, True)}{msg}"
    if not reset:
      return msg
    return f"{msg}{VTS.RESET}"

  @staticmethod
  def getBoldMessage(msg, reset=True):
    msg = f"{VTS.BOLD}{msg}"
    if not reset:
      return msg
    return f"{msg}{VTS.RESET}"

  @staticmethod
  def getUnderlineMessage(msg, reset=True):
    msg = f"{VTS.UNDERLINE}{msg}"
    if not reset:
      return msg
    return f"{msg}{VTS.RESET}"

  @staticmethod
  def getReverseMessage(msg, reset=True):
    msg = f"{VTS.REVERSE}{msg}"
    if not reset:
      return msg
    return f"{msg}{VTS.RESET}"

  @staticmethod
  def testColor():
    for kBc, _vBc in VTS.BACKGROUND_COLORS.items():
      for kFc, _vFc in VTS.FOREGROUND_COLORS.items():
        string = VTS.getColorMessage(f"{kFc:<14}, {kBc:<14}", kFc, kBc)
        print(string)
    VTS.reset()
