"""Timbro 12042 in SVG, con le scritte convertite in tracciati.

Uso:  python strumenti/timbro.py > timbro.svg

Ricostruito dal logo del 25 novembre 2026. Font Montserrat (licenza SIL OFL),
in strumenti/font/. Richiede:  pip install fonttools uharfbuzz
"""
import io, math, os
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "font", "Montserrat-VF.ttf")
BLU, ROSSO = "#0076B0", "#CD071E"
C = 100  # centro del viewBox 0 0 200 200

# Misure in unità del viewBox, con il timbro dritto; alla fine tutto ruota di ROTAZIONE gradi.
P = dict(
    rotazione=11.14,
    anello=(93.68, 4.6),                 # raggio medio e spessore dell'anello esterno
    cerchio=(46.82, 3.77, 23.8),         # cerchio interno: raggio, spessore, metà altezza del taglio
    numero=dict(peso=750, corpo=31.75, base=10.75, x0=-47.3, x2=-29.65, x1=48.0),
    sopra=dict(testo="RIPARA. RIUSA. RISPETTA.", peso=500, corpo=11.9, raggio=65.95, da=-75.9, a=70.7),
    sotto=dict(testo="DAL 2026", peso=550, corpo=12.5, raggio=72.85, da=-21.93, a=26.37),
    stelle=[(-67.39, 0.93), (70.30, 0.93)], stella=9.4,
)

# Stella dell'etichetta (stessa forma), centrata nell'origine e larga 1.
_S = [(92.04, 69.92), (90.37, 71.36), (90.70, 74.01), (88.90, 72.91), (86.41, 74.01),
      (86.89, 71.98), (85.08, 69.92), (87.30, 69.71), (88.56, 67.39), (89.35, 69.27)]
_w = 92.04 - 85.08; _cx = (92.04 + 85.08) / 2; _cy = (74.01 + 67.39) / 2
STELLA = [((x - _cx) / _w, (y - _cy) / _w) for x, y in _S]

_font = {}
def font(peso):
    if peso not in _font:
        f = instantiateVariableFont(TTFont(FONT), {"wght": peso})
        buf = io.BytesIO(); f.save(buf); buf.seek(0); _font[peso] = TTFont(buf)
    return _font[peso]

def n(v): return f"{v:.2f}".rstrip("0").rstrip(".")


def glifi(testo, peso, corpo):
    """Glifi con gli avanzamenti calcolati da HarfBuzz, crenatura compresa."""
    import uharfbuzz as hb
    f = font(peso); gs = f.getGlyphSet(); s = corpo / f["head"].unitsPerEm
    with open(FONT, "rb") as fh:
        hf = hb.Font(hb.Face(fh.read()))
    hf.set_variations({"wght": peso})
    buf = hb.Buffer(); buf.add_str(testo); buf.guess_segment_properties()
    hb.shape(hf, buf, {"kern": True, "liga": False})
    nomi = f.getGlyphOrder()
    return gs, [(gs[nomi[i.codepoint]], p.x_advance * s) for i, p in zip(buf.glyph_infos, buf.glyph_positions)], s


def numero(p):
    """12042: l'inchiostro dell'1 comincia a x0; 2042 va da x2 a x1, con spaziatura uniforme."""
    gs, g, s = glifi("12042", p["peso"], p["corpo"])
    f = font(p["peso"]); glyf = f["glyf"]; cmap = f.getBestCmap()
    uno, due = glyf[cmap[ord("1")]], glyf[cmap[ord("2")]]
    pen = SVGPathPen(gs, ntos=n); y = C + p["base"]
    g[0][0].draw(TransformPen(pen, (s, 0, 0, -s, C + p["x0"] - uno.xMin * s, y)))
    resto = g[1:]
    largo = sum(w for _, w in resto) - due.xMin * s - (f["hmtx"][cmap[ord("2")]][0] - due.xMax) * s
    spazio = ((p["x1"] - p["x2"]) - largo) / (len(resto) - 1)
    x = C + p["x2"] - due.xMin * s
    for gl, w in resto:
        gl.draw(TransformPen(pen, (s, 0, 0, -s, x, y))); x += w + spazio
    return pen.getCommands()


def arco(p, sopra):
    """Testo su arco. Sopra: in senso orario, lettere verso l'esterno. Sotto: leggibile da sinistra a destra."""
    gs, g, s = glifi(p["testo"], p["peso"], p["corpo"])
    R = p["raggio"]; largo = sum(w for _, w in g)
    span = math.radians(p["a"] - p["da"]) * R
    spazio = (span - largo) / (len(g) - 1)
    pen = SVGPathPen(gs, ntos=n); d = 0.0
    for gl, w in g:
        t = math.radians(p["da"]) + (d + w / 2) / R   # angolo del centro del glifo
        ca, sa = math.cos(t), math.sin(t)
        if sopra:   # punto sul cerchio (sin, -cos), glifo ruotato di t
            px, py = C + R * sa, C - R * ca
            m = (s * ca, s * sa, s * sa, -s * ca)
        else:       # angolo dal basso, positivo verso destra; glifo ruotato di -t
            px, py = C + R * sa, C + R * ca
            m = (s * ca, -s * sa, s * sa, s * ca)
            m = (s * ca, -s * sa, -s * sa, -s * ca)
        # origine del glifo: mezzo glifo indietro lungo la tangente
        ox = px - (w / 2) * ca * (1 if sopra else 1)
        oy = py - (w / 2) * sa * (1 if sopra else -1)
        gl.draw(TransformPen(pen, (m[0], m[1], m[2], m[3], ox, oy)))
        d += w + spazio
    return pen.getCommands()


def svg(p=P, classe="timbro"):
    ra, sa = p["anello"]; rc, sc, h = p["cerchio"]
    ro, ri = rc + sc / 2, rc - sc / 2
    xo, xi = math.sqrt(ro**2 - h**2), math.sqrt(ri**2 - h**2)
    cerchio = "".join(
        f"M{n(C-xo)} {n(C+y)}A{n(ro)} {n(ro)} 0 0 {f} {n(C+xo)} {n(C+y)}"
        f"L{n(C+xi)} {n(C+y)}A{n(ri)} {n(ri)} 0 0 {1-f} {n(C-xi)} {n(C+y)}Z"
        for y, f in ((-h, 1), (h, 0)))
    stelle = "".join(
        "M" + "L".join(f"{n(C+x+u*p['stella'])} {n(C+y+v*p['stella'])}" for u, v in STELLA) + "Z"
        for x, y in p["stelle"])
    testo = numero(p["numero"]) + arco(p["sopra"], True) + arco(p["sotto"], False)
    return (f'<svg class="{classe}" viewBox="0 0 200 200" role="img" aria-label="Timbro 12042, ripara, riusa, rispetta, dal 2026">\n'
            f'  <circle cx="100" cy="100" r="100" fill="#fff"/>\n'
            f'  <g transform="rotate({n(-p["rotazione"])} 100 100)">\n'
            f'    <circle cx="100" cy="100" r="{n(ra)}" fill="none" stroke="{BLU}" stroke-width="{n(sa)}"/>\n'
            f'    <path fill="{BLU}" d="{cerchio}{testo}"/>\n'
            f'    <path fill="{ROSSO}" d="{stelle}"/>\n'
            f'  </g>\n</svg>')


if __name__ == "__main__":
    print(svg())
