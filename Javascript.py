# javascriptがビジー状態だと読み込みが完了しないのでpython側で待つ必要がある
IsLoadedAllImagesDefine = """\
window.isLoadedAllImages = (rootId = "") => {
  let root = document;
  if (rootId !== "") {
    root = document.getElementById(rootId);
  }
  const images = root.getElementsByTagName("img");
  let completed = true;
  for (const image of images) {
    if (image.complete === false) {
      completed = false;
      break;
    }
  }
  return completed;
}
"""

IsLoadedAllImagesCall = """\
return window.isLoadedAllImages(arguments[0])
"""

IsLoadedAllImages = """\
const images = document.getElementsByTagName("img");
let completed = true;
for (const image of images) {
 if (image.complete === false) {
   completed = false;
   break;
 }
}
return completed;
"""

FocusToElement = """\
element = arguments[0]
element.focus()
"""

# onload が発生した後に定義した場合の挙動が不明
IsLoadWindowDefine = """\
window.onunload = () => {
  window.isLoad = false;
}
window.onload = () => {
  window.isLoad = true;
}
"""

IsLoadWindowCall = """\
return window.isLoad;
"""

GetComputedStyle = """\
elem = arguments[0];
pseudo = arguments[1];
return window.getComputedStyle(elem, pseudo);
"""

GetComputedStyleProperty = """\
elem = arguments[0];
pseudo = arguments[1];
prop = arguments[2];
return window.getComputedStyle(elem, pseudo).getPropertyValue(prop);
"""

SetCookie = """\
const cookies = arguments[0];
let str = "";
for (const cookie of cookies) {
  str = `${cookie["name"]}=${cookie["value"]}`;
  for (const [key, value] of Object.entries(cookie)) {
    if (key !== "name" || key !== "value") {
      str += `; ${key}=${value}`;
    }
  }
  document.cookie = str.trim();
}
"""

Click = """\
arguments[0].click();
"""

KeyDownPageDown = """\
const event = new KeyboardEvent("keydown", {key: "PageDown", code: "PageDown"});
arguments[0].dispatchEvent(event);
"""

KeyUpPageDown = """\
const event = new KeyboardEvent("keyup", {key: "PageDown", code: "PageDown"});
arguments[0].dispatchEvent(event);
"""

# const inputEvent = new Event('input');
# arguments[0].dispatchEvent(inputEvent)

AsyncInput = """\
arguments[arguments.length-1]();
arguments[0].value = arguments[1];
arguments[0].dispatchEvent(new KeyboardEvent('keyup', {keyCode: 13, key: 'Enter'}));
"""

Input = """\
arguments[0].value = arguments[1];
arguments[0].dispatchEvent(new KeyboardEvent('keyup', {keyCode: 13, key: 'Enter'}));
"""

# arguments[0].dispatchEvent(new KeyboardEvent('keydown', {keyCode: 13, key: 'Enter'}));

DisablePageVisibilityAPI = """\
document.getElementsByTagName("html")[0].hidden = false;
"""

# """\
# // const iframe = document.getElementById("hh_game");
# // const iframeDocument = iframe.contentDocument;
# // console.log(iframeDocument);
# element = document.getElementsByTagName("html")[0];
#
# if (typeof stopImmediatePropagation === "undefined") {
#   function stopImmediatePropagation (event) {
#     event.stopImmediatePropagation();
#   }
# }
#
# element.addEventListener(
#   "visibilitychange",
#   stopImmediatePropagation,
#   true
# );
#
# element.addEventListener(
#   "webkitvisibilitychange",
#   stopImmediatePropagation,
#   true
# );
#
# element.addEventListener(
#   "blur",
#   stopImmediatePropagation,
#   true
# );
#
# element.addEventListener(
#   "webglcontextlost",
#   stopImmediatePropagation,
#   true
# );
# """

getUserAgent = """\
return navigator.userAgent
"""