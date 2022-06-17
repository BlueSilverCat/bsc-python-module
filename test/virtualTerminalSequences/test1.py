import os

from virtualTerminalSequences import VTS

os.system("CLS")  # 画面をクリア
print("NORMAL")
print(f"{VTS.BOLD}BOLD{VTS.RESET}")
# print(f"{AnsiEscapeCode.FAINT}FAINT{AnsiEscapeCode.RESET}")
# print(f"{AnsiEscapeCode.ITALIC}ITALIC{AnsiEscapeCode.RESET}")
# print(f"{AnsiEscapeCode.SLOW_BLINK}SLOW_BLINK{AnsiEscapeCode.RESET}")
# print(f"{AnsiEscapeCode.RAPID_BLINK}RAPID_BLINK{AnsiEscapeCode.RESET}")
# print(f"{AnsiEscapeCode.REVERSE}REVERSE{AnsiEscapeCode.RESET}")
# print(f"{AnsiEscapeCode.CONCEAL}CONCEAL{AnsiEscapeCode.RESET}")
# print(f"{AnsiEscapeCode.CROSSED_OUT}CROSSED_OUT{AnsiEscapeCode.RESET}")
# print(f"{AnsiEscapeCode.DEFAULT_FONT}DEFAULT_FONT{AnsiEscapeCode.RESET}")
# print(f"{AnsiEscapeCode.getAlternativeFont(1)}ALTERNATIVE_FONT1{AnsiEscapeCode.RESET}")
# print(f"{AnsiEscapeCode.getAlternativeFont(2)}ALTERNATIVE_FONT2{AnsiEscapeCode.RESET}")
# print(f"{AnsiEscapeCode.getAlternativeFont(3)}ALTERNATIVE_FONT3{AnsiEscapeCode.RESET}")
# print(f"{AnsiEscapeCode.getAlternativeFont(4)}ALTERNATIVE_FONT4{AnsiEscapeCode.RESET}")
# print(f"{AnsiEscapeCode.getAlternativeFont(5)}ALTERNATIVE_FONT5{AnsiEscapeCode.RESET}")
# print(f"{AnsiEscapeCode.getAlternativeFont(6)}ALTERNATIVE_FONT6{AnsiEscapeCode.RESET}")
# print(f"{AnsiEscapeCode.getAlternativeFont(7)}ALTERNATIVE_FONT7{AnsiEscapeCode.RESET}")
# print(f"{AnsiEscapeCode.getAlternativeFont(8)}ALTERNATIVE_FONT8{AnsiEscapeCode.RESET}")
# print(f"{AnsiEscapeCode.getAlternativeFont(9)}ALTERNATIVE_FONT9{AnsiEscapeCode.RESET}")
# print(f"{AnsiEscapeCode.FRAKTUR}FRAKTUR{AnsiEscapeCode.RESET}")
# print(f"{AnsiEscapeCode.FRAKTUR}FRAKTUR{AnsiEscapeCode.RESET}")
# print(f"{AnsiEscapeCode.DOUBLY_UNDERLINE}DOUBLY_UNDERLINE{AnsiEscapeCode.RESET}")
# print(f"{VTS.BOLD}BOLD")
# print(f"{AnsiEscapeCode.NORMAL_INTENSITY}NORMAL_INTENSITY")
print(f"{VTS.UNDERLINE}UNDERLINE")
print(f"{VTS.UNDERLINE_OFF}UNDERLINE_OFF")
# print(f"{AnsiEscapeCode.PROPORTIONAL_SPACING}PROPORTIONAL_SPACING{AnsiEscapeCode.RESET}")
print(f"{VTS.REVERSE}REVERSE")
print(f"{VTS.REVERSE_OFF}REVERSE_OFF")

# print(f"{AnsiEscapeCode.FRAMED}FRAMED{AnsiEscapeCode.RESET}")
# print(f"{AnsiEscapeCode.ENCIRCLED}ENCIRCLED{AnsiEscapeCode.RESET}")
# print(f"{AnsiEscapeCode.OVERLINED}OVERLINED{AnsiEscapeCode.RESET}")
# print(f"{AnsiEscapeCode.IDEOGRAM_UNDERLINE}IDEOGRAM_UNDERLINE{AnsiEscapeCode.RESET}")
# print(f"{AnsiEscapeCode.IDEOGRAM_DOUBLE_UNDERLINE}IDEOGRAM_DOUBLE_UNDERLINE{AnsiEscapeCode.RESET}")
# print(f"{AnsiEscapeCode.IDEOGRAM_OVERLINE}IDEOGRAM_OVERLINE{AnsiEscapeCode.RESET}")
# print(f"{AnsiEscapeCode.IDEOGRAM_DOUBLE_OVERLINE}IDEOGRAM_DOUBLE_OVERLINE{AnsiEscapeCode.RESET}")
# print(f"{AnsiEscapeCode.IDEOGRAM_STRESS_MAKING}IDEOGRAM_STRESS_MARKING{AnsiEscapeCode.RESET}")
# print(f"{AnsiEscapeCode.SUPERSCRIPT}SUPERSCRIPT{AnsiEscapeCode.RESET}")
# print(f"{AnsiEscapeCode.SUBSCRIPT}SUBSCRIPT{AnsiEscapeCode.RESET}")

# [print(f"{VTS.getForegroundColor(key)}$", end="") for key in VTS.FOREGROUND_COLORS.keys()]
[print(f"{VTS._getForegroundColorName(key)}$", end="") for key in VTS.FOREGROUND_COLORS.keys()]
VTS.reset()
[print(f"{VTS._getForegroundColorNumber(n)}$", end="") for n in range(256)]
VTS.reset()
[print(f"{VTS._getForegroundColorRGB(r,0,0)}$", end="") for r in range(256)]
VTS.reset()
[print(f"{VTS._getForegroundColorRGB(0,g,0)}$", end="") for g in range(256)]
VTS.reset()
[print(f"{VTS._getForegroundColorRGB(0,0,b)}$", end="") for b in range(256)]
VTS.reset()

[print(f"{VTS._getBackgroundColorName(key)}_", end="") for key in VTS.BACKGROUND_COLORS.keys()]
VTS.reset()
[print(f"{VTS._getBackgroundColorNumber(n)}_", end="") for n in range(256)]
VTS.reset()
[print(f"{VTS._getBackgroundColorRGB(r,0,0)}_", end="") for r in range(256)]
VTS.reset()
[print(f"{VTS._getBackgroundColorRGB(0,g,0)}_", end="") for g in range(256)]
VTS.reset()
[print(f"{VTS._getBackgroundColorRGB(0,0,b)}_", end="") for b in range(256)]
VTS.reset()

print(VTS.getColorMessage("色々な色", "red", "blue"))
print(VTS.getColorMessage("色々な色", 3, 6))
print(VTS.getColorMessage("色々な色", (200, 200, 200), (100, 100, 100), False))
print(VTS.getUnderlineMessage("河川に下線"))
print(VTS.getBoldMessage("太い痩せ猫", False))
print(VTS.getReverseMessage("裏返る裏切り"))
print(VTS.getReverseMessage("裏返る裏切り"))
string1 = VTS.getColorMessage("abc", "red", "green")
string2 = VTS.getColorMessage("def", "green", "blue")
string3 = VTS.getColorMessage("ghi", "blue", "red")
print(string1 + string2 + string3)
