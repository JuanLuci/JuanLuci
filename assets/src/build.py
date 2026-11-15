"""Gera os SVGs do README de perfil (banner, botões de língua, cartões).

Fontes embutidas como woff2 com subset (Pixelify Sans e Inter, ambas OFL).
Rodar: python build.py  (precisa de fontTools, brotli e Pillow)
"""
import base64, io, math, os
from fontTools import subset
from fontTools.ttLib import TTFont
from PIL import ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)

ACCENT = "#5d9c3f"
VIOLET = "#5d3fa8"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def font_data(name, text):
    f = TTFont(os.path.join(HERE, name + ".ttf"))
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["*"]
    s = subset.Subsetter(opts)
    s.populate(text=text + " ")
    s.subset(f)
    buf = io.BytesIO()
    f.flavor = "woff2"
    f.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


def font_css(px_text="", in_text=""):
    css = []
    if px_text:
        css.append("@font-face{font-family:PX;font-weight:400 700;src:url(data:font/woff2;base64,%s) format('woff2')}" % font_data("pixelify", px_text))
    if in_text:
        css.append("@font-face{font-family:IN;font-weight:400 700;src:url(data:font/woff2;base64,%s) format('woff2')}" % font_data("inter", in_text))
    return "".join(css)


_fonts = {}


def width(text, size, weight, fam="inter"):
    key = (fam, size, weight)
    if key not in _fonts:
        f = ImageFont.truetype(os.path.join(HERE, fam + ".ttf"), size)
        f.set_variation_by_axes([weight])
        _fonts[key] = f
    return _fonts[key].getlength(text)


def wrap(text, size, weight, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if width(t, size, weight) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def img64(name):
    p = os.path.join(HERE, name)
    data = open(p, "rb").read()
    mime = "image/png" if data[:4] == b"\x89PNG" else "image/jpeg"
    return "data:%s;base64,%s" % (mime, base64.b64encode(data).decode())


def write(name, svg):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(svg)
    print(name, len(svg.encode()) // 1024, "KB")


# ---------------------------------------------------------------- banner
def banner(lang, subtitle):
    W, H, B = 832, 220, 16
    grass = dirt = ""
    for i in range(W // B):
        h = 2 + round(1.6 + 1.4 * math.sin(i * 0.31) + 1.1 * math.sin(i * 0.11 + 1.7) + 0.6 * math.sin(i * 0.77))
        if i > 34:
            h += 1
        else:
            h = min(h, 4)
        top = H - h * B
        grass += "M%d %dh%dv%dh-%dz" % (i * B, top, B, B // 2, B)
        dirt += "M%d %dh%dV%dh-%dz" % (i * B, top + B // 2, B, H, B)
    groups = ["", "", ""]
    seed = 7
    for s in range(40):
        seed = (seed * 9301 + 49297) % 233280
        x = int(seed / 233280 * W)
        seed = (seed * 9301 + 49297) % 233280
        y = int(seed / 233280 * 130) + 8
        z = 4 if s % 5 == 0 else 2
        if 24 < x < 560 and 24 < y < 132:
            continue
        if 690 < x < 750 and 20 < y < 80:
            continue
        groups[s % 3] += "M%d %dh%dv%dh-%dz" % (x, y, z, z, z)
    name = "Juan Luci"
    css = font_css(px_text=name + subtitle)
    css += (
        ".tw{animation:tw 4s ease-in-out infinite}.t1{animation-duration:3.1s;animation-delay:-1s}"
        ".t2{animation-duration:5.3s;animation-delay:-2.4s}"
        "@keyframes tw{0%,100%{opacity:.9}50%{opacity:.25}}"
        "@media (prefers-reduced-motion:reduce){.tw{animation:none}}"
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Juan Luci">
<style>{css}</style>
<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#120f2e"/><stop offset=".62" stop-color="#231c5c"/><stop offset="1" stop-color="#3b2f7e"/></linearGradient>
<clipPath id="c"><rect width="{W}" height="{H}" rx="12"/></clipPath>
</defs>
<g clip-path="url(#c)">
<rect width="{W}" height="{H}" fill="url(#sky)"/>
<path class="tw" d="{groups[0]}" fill="#e9e4ff"/>
<path class="tw t1" d="{groups[1]}" fill="#e9e4ff"/>
<path class="tw t2" d="{groups[2]}" fill="#e9e4ff"/>
<rect x="704" y="34" width="32" height="32" fill="#f3efe0"/><rect x="712" y="42" width="8" height="8" fill="#d9d3bd"/><rect x="724" y="52" width="6" height="6" fill="#d9d3bd"/>
<path d="{dirt}" fill="#1a1440"/>
<path d="{grass}" fill="{ACCENT}"/>
<g font-family="PX, monospace">
<text x="44" y="88" font-size="56" font-weight="700" fill="#0b0920" letter-spacing="1">{name}</text>
<text x="40" y="84" font-size="56" font-weight="700" fill="#ffffff" letter-spacing="1">{name}</text>
<text x="40" y="120" font-size="20" font-weight="500" fill="#cfc6ff">{esc(subtitle)}</text>
</g>
</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="11.5" fill="none" stroke="#2d2a5a"/>
</svg>
'''


# ---------------------------------------------------------------- botões de língua
def lang_button(tag, label, active, side):
    tw = width(label, 14, 600 if active else 500)
    bw = int(16 + 26 + 8 + tw + 16)
    W, H = bw + 6, 46
    r = 10
    if side == "left":  # bordas do contêiner: arredonda só a esquerda
        outer = f"M{W} .5H{r}.5A{r} {r} 0 0 0 .5 {r}.5V{H-r}.5A{r} {r} 0 0 0 {r}.5 {H-.5}H{W}"
        bx = 4
        W += 0
    else:
        outer = f"M0 .5H{W-r-.5}A{r} {r} 0 0 1 {W-.5} {r}.5V{H-r}.5A{r} {r} 0 0 1 {W-r-.5} {H-.5}H0"
        bx = 2
    fill_bg = "#161b22"
    btn = VIOLET if active else "none"
    tag_bg, tag_fg = ("#ffffff", "#2a2470") if active else ("#30363d", "#c9d1d9")
    lab_fg, lab_w = ("#ffffff", 600) if active else ("#9198a1", 500)
    css = font_css(px_text=tag, in_text=label)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{label}">
<style>{css}</style>
<path d="{outer}" fill="{fill_bg}" stroke="#30363d"/>
<rect x="{bx}" y="5" width="{bw}" height="36" rx="7" fill="{btn}"/>
<rect x="{bx+16}" y="14" width="26" height="18" rx="3" fill="{tag_bg}"/>
<text x="{bx+29}" y="27.5" text-anchor="middle" font-family="PX, monospace" font-size="12" font-weight="600" fill="{tag_fg}">{tag}</text>
<text x="{bx+50}" y="28" font-family="IN, system-ui, sans-serif" font-size="14" font-weight="{lab_w}" fill="{lab_fg}">{esc(label)}</text>
</svg>
'''


# ---------------------------------------------------------------- cartões
def card_layout(c):
    lines = wrap(c["text"], 14, 400, 368)
    return lines, 20 + 44 + 14 + len(lines) * 21.7 + 14 + 24 + 20


def card(c, height):
    W = 408
    H = math.ceil(height)
    lines, _ = card_layout(c)
    y = 20 + 44 + 14
    text = "".join(
        f'<text x="20" y="{y + 15 + i * 21.7:.1f}">{esc(l)}</text>' for i, l in enumerate(lines)
    )
    cy = y + len(lines) * 21.7 + 14
    chips, cx = "", 20
    for ch in c["chips"]:
        cw = width(ch, 12, 500) + 18
        chips += f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{cw:.1f}" height="22" rx="11" fill="{c["chip_bg"]}"/>'
        chips += f'<text x="{cx + cw/2:.1f}" y="{cy + 15:.1f}" text-anchor="middle">{esc(ch)}</text>'
        cx += cw + 6
    alltext = c["text"] + c["sub"] + "".join(c["chips"])
    css = font_css(px_text=c["title"], in_text=alltext)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(c["title"])}">
<style>{css}</style>
<defs><clipPath id="c"><rect width="{W}" height="{H}" rx="12"/></clipPath><clipPath id="a"><rect x="20" y="20" width="44" height="44" rx="8"/></clipPath></defs>
<g clip-path="url(#c)">
<rect width="{W}" height="{H}" fill="#161b22"/>
<rect width="{W}" height="3" fill="{c["stripe"]}"/>
</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="11.5" fill="none" stroke="#30363d"/>
<image x="20" y="20" width="44" height="44" clip-path="url(#a)" href="{img64(c["avatar"])}" style="image-rendering:pixelated"/>
<text x="76" y="40" font-family="PX, monospace" font-size="22" font-weight="700" fill="#ffffff">{esc(c["title"])}</text>
<text x="76" y="58" font-family="IN, system-ui, sans-serif" font-size="12" fill="#9198a1">{esc(c["sub"])}</text>
<g font-family="IN, system-ui, sans-serif" font-size="14" fill="#c9d1d9">{text}</g>
<g font-family="IN, system-ui, sans-serif" font-size="12" font-weight="500" fill="{c["chip_fg"]}">{chips}</g>
</svg>
'''


STARLING = dict(title="Starling", sub="Java Edition · Android", avatar="starling.png", stripe=VIOLET,
                chip_bg="#2a2148", chip_fg="#cfc6ff")
PURPLE = dict(title="Purplebyte Studio", sub="Bedrock · Marketplace", avatar="purplebyte.png", stripe=ACCENT,
              chip_bg="#1c2a1a", chip_fg="#b5dca3")

LANGS = {
    "en": dict(
        subtitle="I make Minecraft things, on both editions.",
        starling=dict(text="Android port of Horizon, Minecraft: Java Edition rewritten in Rust. Touch controls and native mods.",
                      chips=["Rust", "Vulkan", "Android"]),
        purple=dict(text="Add-ons for the Minecraft Marketplace. A bit of everything, mostly entities.",
                    chips=["Entities", "Script API", "JSON UI"]),
    ),
    "pt": dict(
        subtitle="Eu faço coisas de Minecraft, nas duas edições.",
        starling=dict(text="Port do Horizon, o Minecraft: Java Edition reescrito em Rust, para Android. Controles de toque e mods nativos.",
                      chips=["Rust", "Vulkan", "Android"]),
        purple=dict(text="Add-ons para o Marketplace do Minecraft. Faço de tudo um pouco, principalmente entidades.",
                    chips=["Entidades", "Script API", "JSON UI"]),
    ),
}

if __name__ == "__main__":
    for lang, d in LANGS.items():
        write(f"banner-{lang}.svg", banner(lang, d["subtitle"]))
        s = {**STARLING, **d["starling"]}
        p = {**PURPLE, **d["purple"]}
        h = max(card_layout(s)[1], card_layout(p)[1])
        write(f"card-starling-{lang}.svg", card(s, h))
        write(f"card-purplebyte-{lang}.svg", card(p, h))
    write("lang-en-on.svg", lang_button("EN", "English", True, "left"))
    write("lang-en-off.svg", lang_button("EN", "English", False, "left"))
    write("lang-pt-on.svg", lang_button("PT", "Português", True, "right"))
    write("lang-pt-off.svg", lang_button("PT", "Português", False, "right"))
