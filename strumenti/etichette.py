"""Etichette 12042, formato 50 x 25 mm.

Uso:  python strumenti/etichette.py 31 60
      python strumenti/etichette.py 31 60 2027
          crea etichette/etichette-0031-0060.pdf (al massimo 30 numeri per volta);
          l'anno sull'etichetta è quello in corso, oppure quello indicato.

      python strumenti/etichette.py --svg 31 2026
          stampa l'SVG dell'etichetta n. 0031, da incollare nella scheda.

Richiede:  pip install segno reportlab fonttools
Font: Host Grotesk (licenza SIL OFL), in strumenti/font/.
"""
import sys, os, datetime
import segno

FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "font")
REGOLARE = os.path.join(FONT, "HostGrotesk-Regular.ttf")
GRASSETTO = os.path.join(FONT, "HostGrotesk-Bold.ttf")
BLU, ROSSO = "#007EB7", "#D22329"

# Il disegno originale misura 171,3 x 85,61 mm. Tutte le misure sono in quel
# riferimento (y dall'alto) e vengono scalate alla misura reale.
RIF_W, RIF_H = 171.3, 85.61
BORDO = dict(x=2.99, y=3.89, w=165.32, h=77.83, r=5.25, spessore=0.926)
RIGA = dict(x1=8.9, x2=91.74, y=43.7)
QR = dict(x=99.97, y=11.61, lato=62.43)
STELLA = [(92.04, 69.92), (90.37, 71.36), (90.70, 74.01), (88.90, 72.91), (86.41, 74.01),
          (86.89, 71.98), (85.08, 69.92), (87.30, 69.71), (88.56, 67.39), (89.35, 69.27)]


def scritte(numero, anno):
    """(grassetto?, testo, x, linea di base, corpo, fine o None): fine allarga o stringe il testo fino lì."""
    return [
        (True, "12042", 8.88, 30.32, 23.83, 85.11),
        (True, "RIPARA. RIUSA. RISPETTA.", 8.9, 38.63, 6.95, 91.74),
        (False, "NUMERO", 8.9, 51.04, 5.56, None),
        (False, "ANNO", 57.92, 51.04, 5.56, None),
        (True, numero, 8.9, 61.58, 10.42, None),
        (True, str(anno), 57.99, 61.58, 10.42, None),
        (False, f"12042.it/r/{numero}", 8.9, 73.03, 5.56, 52.4),
    ]


def matrice(numero):
    return [[bool(v) for v in r] for r in
            segno.make(f"https://12042.it/r/{numero}", error="m", boost_error=False).matrix]


def strisce(m):
    """Moduli scuri del QR riuniti in strisce orizzontali: (colonna, riga, lunghezza)."""
    for yy, r in enumerate(m):
        xx = 0
        while xx < len(r):
            if r[xx]:
                e = xx
                while e < len(r) and r[e]: e += 1
                yield xx, yy, e - xx; xx = e
            else:
                xx += 1


# ---------------------------------------------------------------- SVG per le schede

def svg(n, anno):
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    numero = f"{n:04d}"
    font = {True: TTFont(GRASSETTO), False: TTFont(REGOLARE)}
    d = []
    for grassetto, testo, x, base, corpo, fine in scritte(numero, anno):
        f = font[grassetto]; gs = f.getGlyphSet(); cmap = f.getBestCmap(); s = corpo / f["head"].unitsPerEm
        larghezza = sum(gs[cmap[ord(ch)]].width for ch in testo) * s
        spazio = (fine - x - larghezza) / (len(testo) - 1) if fine else 0
        pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
        for ch in testo:
            g = gs[cmap[ord(ch)]]
            g.draw(TransformPen(pen, (s, 0, 0, -s, x, base)))
            x += g.width * s + spazio
        d.append(pen.getCommands())
    b = BORDO; m = matrice(numero); mod = QR["lato"] / len(m)
    qr = "".join(f"M{QR['x']+c*mod:.2f} {QR['y']+r*mod:.2f}h{l*mod:.2f}v{mod:.2f}h{-l*mod:.2f}z" for c, r, l in strisce(m))
    stella = "M" + "L".join(f"{x} {y}" for x, y in STELLA) + "Z"
    return f"""<svg class="etichetta" viewBox="0 0 {RIF_W} {RIF_H}" role="img" aria-label="Etichetta 12042, ripara, riusa, rispetta, numero {numero}, anno {anno}, con codice QR per 12042.it/r/{numero}">
        <rect width="{RIF_W}" height="{RIF_H}" rx="{b['r']+b['x']}" fill="#fff"/>
        <rect x="{b['x']}" y="{b['y']}" width="{b['w']}" height="{b['h']}" rx="{b['r']}" fill="none" stroke="{BLU}" stroke-width="{b['spessore']}"/>
        <path d="M{RIGA['x1']} {RIGA['y']}H{RIGA['x2']}" stroke="{BLU}" stroke-width="{b['spessore']}"/>
        <path fill="{BLU}" d="{''.join(d)}"/>
        <path fill="{ROSSO}" d="{stella}"/>
        <path fill="{BLU}" shape-rendering="crispEdges" d="{qr}"/>
      </svg>"""


# ---------------------------------------------------------------- PDF da stampare

def pdf(primo, ultimo, anno):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    pdfmetrics.registerFont(TTFont("HG", REGOLARE))
    pdfmetrics.registerFont(TTFont("HG-B", GRASSETTO))
    numeri = list(range(primo, ultimo + 1))
    assert 1 <= len(numeri) <= 30, "da 1 a 30 numeri per volta"
    W, H = 50*mm, 25*mm
    k = W / (RIF_W*mm)
    X = lambda v: v*mm*k
    Y = lambda v: (RIF_H - v)*mm*k

    def etichetta(n):
        numero = f"{n:04d}"
        blu, rosso = HexColor(BLU), HexColor(ROSSO)
        b = BORDO
        c.setStrokeColor(blu); c.setLineWidth(X(b["spessore"]))
        c.roundRect(X(b["x"]), Y(b["y"]+b["h"]), X(b["w"]), X(b["h"]), X(b["r"]), stroke=1, fill=0)
        c.line(X(RIGA["x1"]), Y(RIGA["y"]), X(RIGA["x2"]), Y(RIGA["y"]))
        c.setFillColor(blu)
        for grassetto, testo, x, base, corpo, fine in scritte(numero, anno):
            nome = "HG-B" if grassetto else "HG"
            spazio = (X(fine-x) - pdfmetrics.stringWidth(testo, nome, X(corpo))) / (len(testo)-1) if fine else 0
            t = c.beginText(X(x), Y(base)); t.setFont(nome, X(corpo)); t.setCharSpace(spazio); t.textOut(testo)
            c.drawText(t)
        c.setFillColor(rosso)
        p = c.beginPath()
        for i, (x, y) in enumerate(STELLA):
            (p.moveTo if i == 0 else p.lineTo)(X(x), Y(y))
        p.close(); c.drawPath(p, stroke=0, fill=1)
        c.setFillColor(blu)
        m = matrice(numero); mod = X(QR["lato"]) / len(m)
        for col, riga, l in strisce(m):
            c.rect(X(QR["x"]) + col*mod, Y(QR["y"]) - (riga+1)*mod, l*mod, mod, stroke=0, fill=1)

    os.makedirs("etichette", exist_ok=True)
    out = f"etichette/etichette-{primo:04d}-{ultimo:04d}.pdf"
    PW, PH = A4; M = 8*mm; COLS = 3
    c = canvas.Canvas(out, pagesize=A4)
    c.setTitle(f"Etichette 12042, n. {primo:04d}-{ultimo:04d}")
    c.setFillGray(0.45); c.setFont("HG", 6.5)
    c.drawString(M, PH-M-7, f"Etichette 50 x 25 mm, anno {anno}. Stampare al 100%, senza adattare alla pagina.")
    ytop = PH - M - 10
    for i, num in enumerate(numeri):
        x = M + (i % COLS)*W; y = ytop - (i//COLS + 1)*H
        c.setStrokeGray(0.72); c.setLineWidth(0.2); c.rect(x, y, W, H, stroke=1, fill=0)
        c.saveState(); c.translate(x, y); etichetta(num); c.restoreState()
    c.showPage(); c.save()
    print("Creato", out)


if __name__ == "__main__":
    oggi = datetime.date.today().year
    if sys.argv[1] == "--svg":
        print(svg(int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else oggi))
    else:
        pdf(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else oggi)
