"""Genera il PDF delle etichette 12042 in tre formati.

Uso:  python strumenti/etichette.py 31 60
      crea etichette/etichette-0031-0060.pdf (al massimo 30 numeri per volta)

Richiede:  pip install segno reportlab
"""
import sys, os
import segno
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

primo, ultimo = int(sys.argv[1]), int(sys.argv[2])
numeri = list(range(primo, ultimo + 1))
assert 1 <= len(numeri) <= 30, "da 1 a 30 numeri per volta"
os.makedirs("etichette", exist_ok=True)
OUT = f"etichette/etichette-{primo:04d}-{ultimo:04d}.pdf"
W, H = A4; M = 8*mm
c = canvas.Canvas(OUT, pagesize=A4)
c.setTitle(f"Etichette 12042, n. {primo:04d}-{ultimo:04d}")

def qr(n,qx,qy,size):
    m=[[bool(v) for v in r] for r in segno.make(f'https://12042.it/r/{n}',error='m').matrix]
    s=size/len(m); c.setFillGray(0)
    for yy,r in enumerate(m):
        xx=0
        while xx<len(r):
            if r[xx]:
                e=xx
                while e<len(r) and r[e]: e+=1
                c.rect(qx+xx*s, qy+size-(yy+1)*s, (e-xx)*s, s, stroke=0, fill=1); xx=e
            else: xx+=1

def grande(x,y,w,h,n):
    q=16*mm; qx=x+3*mm; qy=y+(h-q)/2; qr(n,qx,qy,q)
    tx=qx+q+3*mm; top=qy+q
    c.setFont('Helvetica-Bold',13); c.drawString(tx,top-10.5,'12042')
    c.setFont('Helvetica',5.5);     c.drawString(tx,top-18,'riparato con passione')
    c.setFont('Helvetica-Bold',9);  c.drawString(tx,top-31,f'n. {n}')
    c.setFont('Helvetica',6);       c.drawString(tx,top-40.5,f'12042.it/r/{n}')
def media(x,y,w,h,n):
    q=11*mm; qx=x+1.5*mm; qy=y+(h-q)/2; qr(n,qx,qy,q)
    tx=qx+q+2*mm; top=qy+q
    c.setFont('Helvetica-Bold',9);  c.drawString(tx,top-8,'12042')
    c.setFont('Helvetica-Bold',7);  c.drawString(tx,top-18,f'n. {n}')
    c.setFont('Helvetica',4.5);     c.drawString(tx,top-27,f'12042.it/r/{n}')
def piccola(x,y,w,h,n):
    q=10*mm; qx=x+(w-q)/2; qy=y+h-1.5*mm-q; qr(n,qx,qy,q)
    c.setFont('Helvetica-Bold',5); c.drawCentredString(x+w/2,qy-5.5,'12042')
    c.drawCentredString(x+w/2,qy-10.8,f'n. {n}')

def blocco(titolo,ytop,w,h,cols,fn,page):
    c.setFillGray(0.45); c.setFont('Helvetica',6.5); c.drawString(M,ytop-7,titolo)
    ytop-=10
    rows=-(-len(numeri)//cols)
    c.setStrokeGray(0.72); c.setLineWidth(0.2)
    for k,num in enumerate(numeri):
        col,row=k%cols,k//cols
        x=M+col*w; y=ytop-(row+1)*h
        c.rect(x,y,w,h,stroke=1,fill=0)
        fn(x,y,w,h,f'{num:04d}')
    return ytop-rows*h

blocco('Formato grande, 50 x 22 mm',H-M,50*mm,22*mm,3,grande,1)
c.showPage()
y=blocco('Formato medio, 34 x 14 mm',H-M,34*mm,14*mm,5,media,2)
blocco('Formato piccolo, 13 x 16 mm',y-8*mm,13*mm,16*mm,14,piccola,2)
c.showPage(); c.save()
print("Creato", OUT)
