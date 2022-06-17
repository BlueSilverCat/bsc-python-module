import os

from virtualTerminalSequences import VTS

os.system("CLS")  # 画面をクリア
print("NORMAL")

string = "CAT cat dog Dog"
color = VTS.getForegroundColor("cyan")
print(color + string)
VTS.reset()

color = VTS.getForegroundColor(10)
print(color + string)
VTS.reset()

color = VTS.getForegroundColor((0, 255, 255))
print(color + string)
VTS.reset()

string = "CAT cat dog Dog"
color = VTS.getBackgroundColor("cyan")
print(color + string)
VTS.reset()

color = VTS.getBackgroundColor(10)
print(color + string)
VTS.reset()

color = VTS.getBackgroundColor((0, 255, 255))
print(color + string)
VTS.reset()
