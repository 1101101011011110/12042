# 12042. Ripara. Riusa. Rispetta.

Sito di [12042.it](https://12042.it): le schede pubbliche degli oggetti riparati a Bra.
Ogni oggetto riparato porta un'etichetta con un numero e un codice QR che rimanda alla sua scheda.

## Struttura

| Percorso | Contenuto |
|---|---|
| `index.html` | Pagina iniziale con l'elenco delle schede |
| `r/0002/index.html` | Scheda n. 0002, raggiungibile da `12042.it/r/0002` |
| `404.html` | Pagina mostrata quando una scheda non è ancora pubblicata |
| `etichette/` | PDF delle etichette da stampare |
| `strumenti/etichette.py` | Script che genera i PDF delle etichette e l'SVG per la scheda |
| `strumenti/timbro.py` | Script che genera l'SVG del timbro (logo) |
| `strumenti/font/` | Font Host Grotesk e Montserrat (licenza SIL OFL) |
| `CNAME` | Dominio personalizzato per GitHub Pages |
| `.nojekyll` | Dice a GitHub Pages di pubblicare i file così come sono |

## Aggiungere una scheda

1. Copiare la cartella `r/0002` in `r/NNNN`, con il numero dell'etichetta applicata all'oggetto.
2. In `r/NNNN/index.html` sostituire il numero `0002` in tutti i punti (titolo, timbro, etichetta, record dei dati aperti) e compilare i contenuti. L'etichetta in fondo alla scheda si rigenera con `python strumenti/etichette.py --svg NNNN AAAA`.
3. Mettere le foto nella stessa cartella e collegarle con `<img src="nome.jpg" alt="descrizione">`.
4. In `index.html` aggiungere una riga al registro, la più recente in alto.

Regole: un numero non si riusa mai, nemmeno se la riparazione non riesce. Nelle schede non vanno dati personali dei proprietari.

## Stampare altre etichette

```
pip install segno reportlab fonttools
python strumenti/etichette.py 31 60
```

Stampare al 100%, senza adattare alla pagina.
