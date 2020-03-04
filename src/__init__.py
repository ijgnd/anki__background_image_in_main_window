# Copyright: 2020- ijgnd
#            Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html 
#
# This add-on contains a file named web/wikigears.svg from
# https://commons.wikimedia.org/wiki/File:Gear-kegelzahnrad.svg
# (backup: https://web.archive.org/web/20161207153533/https://commons.wikimedia.org/wiki/File:Gear-kegelzahnrad.svg)
# that was originally uploaded according to that page by the wikimedia user "MyriamThyes"
# It contains the following Licensing Information:
#     I , the copyright holder of this work, release this work into the public domain. 
#     This applies worldwide.
#     In some countries this may not be legally possible; if so:
#     I grant anyone the right to use this work for any purpose, 
#     without any conditions, unless such conditions 
#     are required by law.

"""
classic approach with wrap doesn't work: in main.py deckbrowser is instantiated 
before add-ons are loaded. Arthur's "Deck name in title" used a custom wrapping
function for bound methods to work around this. He plans to abandon this approach
by adding a new style hook "deck_browser_did_render" to Anki, see below.


new hooks don't help in 2020-03-01:
- gui_hooks.deck_browser_did_render is only called if the containing method is called
  with a non-default argument reuse=True which rarely happens
  this hooks was added by Arthur for the add-on "Deck name in title"
- gui_hooks.deck_browser_will_render_content(self, content): content is useless for me
  since it is:
          content = DeckBrowserContent(
            tree=self._renderDeckTree(self._dueTree),
            stats=self._renderStats(),
            countwarn=self._countWarn(),
        )
- gui_hooks.deck_browser_will_show_options_menu: useless
"""

import os
from anki.utils import pointVersion
from anki.hooks import wrap
import aqt
from aqt import mw
from aqt import gui_hooks
from aqt.deckbrowser import DeckBrowser


def gc(arg, fail=False):
    conf = mw.addonManager.getConfig(__name__)
    if conf:
        return conf.get(arg, fail)
    return fail


addon_path = os.path.dirname(__file__)
addonfoldername = os.path.basename(addon_path)
regex = r"(user_files.*|web.*)"
mw.addonManager.setWebExports(__name__, regex)


fileversions_for_anki_version = {
    "20": "css_files/20_deckbrowser.css",
    "21": "css_files/20_deckbrowser.css",  # version for 20 and 21 are identical
}


v = pointVersion()
if v in fileversions_for_anki_version:
    dbcss = fileversions_for_anki_version[v]
else:  # for newer Anki versions try the latest version and hope for the best
    dbcss = fileversions_for_anki_version[max(fileversions_for_anki_version, key=int)]

dbcss_abs = os.path.join(addon_path, dbcss)
imgname = gc("image name for file in user_files subfolder", "anki.png")
img_web_rel_path  = f"/_addons/{addonfoldername}/user_files/{imgname}"
merged = "web/deckbrowser.css"
merged_abs = os.path.join(addon_path, merged)
merged_web_rel_path  = f"/_addons/{addonfoldername}/{merged}"

with open(dbcss_abs) as f:
    cont = f.read()
old = "body {"
new = f"""{old}\nbackground-image: url("{img_web_rel_path}");"""
cont = cont.replace(old, new)


with open(merged_abs, "w") as f:
    f.write(cont)


def replace_css(web_content, context):
    if isinstance(context, aqt.deckbrowser.DeckBrowser):
        for idx, filename in enumerate(web_content.css):
            if filename == "deckbrowser.css":
                web_content.css[idx] = merged_web_rel_path
gui_hooks.webview_will_set_content.append(replace_css)



def replace_gears(deck_browser, content):
    print(f"in replace_gears and type of content.tree is {type(content.tree)}")  # that's a string
    old = """<img src='/_anki/imgs/gears.svg'"""
    new = f"""<img src='/_addons/{addonfoldername}/web/wikigear.svg'"""
    content.tree = content.tree.replace(old, new)
gui_hooks.deck_browser_will_render_content.append(replace_gears)


## discarded unfinised idea: use js to modify the css after loading
'''
# This doesn't work:
myjs = """
console.log("%s");
var bg = document.getElementById("body");
bg.style.backgroundImage = url("%s");
""" % (img_web_rel_path, img_web_rel_path)

def showimage(deckbrowserinstance):
    deckbrowserinstance.web.eval(myjs)
# DeckBrowser.refresh = wrap(DeckBrowser.refresh, showimage)
gui_hooks.deck_browser_did_render.append(showimage)
'''
