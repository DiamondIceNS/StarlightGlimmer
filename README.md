<img align="right" width="200" height="200" src="avatar.jpg">

# Starlight Glimmer
A template utility bot based on [Alastair](Make-Alastair-Great-Again) and [Pinkie Pie](https://pastebin.com/Tg1p5AnW).

Currently supports [Pixelcanvas.io](https://pixelcanvas.io/), [Pixelzone.io](https://pixelzone.io/), [Pxls.space](https://pxls.space/), and [Pixelplace.fun](https://pixelplace.fun/).

**Invite:** `https://discordapp.com/oauth2/authorize?&client_id=405480380930588682&scope=bot&permissions=109569`

#### Requires:
- [Python 3.6](https://www.python.org/downloads/release/python-365/)
- [Discord.py rewrite](https://github.com/Rapptz/discord.py/tree/rewrite) (Tested with commit [7f4c57d](https://github.com/Rapptz/discord.py/tree/7f4c57dd5ad20b7fa10aea485f674a4bc24b9547))
- [Pillow](https://pillow.readthedocs.io/en/latest/installation.html) 5.1.0
- [aiohttp](https://aiohttp.readthedocs.io/en/stable/) 3.2.0
- [numpy](https://www.scipy.org/scipylib/download.html) 1.14.4
- [websockets](https://pypi.org/project/websockets/) 4.0.1
- [lz4](https://github.com/python-lz4/python-lz4) 1.1.0

#### Installation:
1. Install Python 3.6
2. Run `pip install -r requirements.txt` in the main directory
3. Put your bot token and other config info in `config/config.json.example`
3. Rename `config.json.example` to `config.json`
4. Run `python glimmer.py`

#### Features:
- Automatic live canvas preview
- Automatic live template checking
- Template storage for easy access to templates you care about most
- Faction creation, to share your templates with other guilds
- Color quantization of templates to canvas palette
- Gridifyer to create gridded, human-readable templates
- Dithering sample charts for assisting color selection when you are making a template
- Configurable roles
- [Animotes](https://github.com/ev1l0rd/animotes) support, just because
- Full language localization

For a more in-depth walkthrough of Glimmer's core functions, see [the wiki page](https://github.com/DiamondIceNS/StarlightGlimmer/wiki).

#### Languages:
- English (US)
- Portuguese (BR) - Special thanks to Ataribr / ✠ /#6703

If you happen to know a language that is not listed and would be willing to translate, please translate the strings in `lang/en_US.py` and submit a pull request.
(Currently looking for: French, Turkish)

#### Help:
If you need assistance with the bot, have a problem, or would like to recommend a feature to me directly, you can contact me [on my support server](https://discord.gg/UtyJx2x). You can also DM me if you see me around -- I am `Fawfulcopter#3432` on Discord.

[avatar]: avatar.jpg