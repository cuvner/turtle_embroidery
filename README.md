# Embroidery Turtle Web App

A friendly, browser-based studio for sketching turtle commands and exporting ready-to-stitch PES files for a 150 cm hoop (10 mm per unit). Born from classroom turtle drawings, now aimed at fabric.

- Live demo: https://turtle-embroidery.onrender.com
- Built on [pyembroidery](https://github.com/EmbroidePy/pyembroidery); inspired by [Pembroider](https://github.com/CreativeInquiry/PEmbroider).

![Embroidery turtle example](images/turtle_embroider_readme.png)

Embroidery: the art of decorating fabric with a needle and thread. Visual reference: ![Embroidery machine](https://www.brothersewingshop.co.uk/image/cache/catalog/Brother/F540E-500x500.jpg)

---

## Contents

- [What’s inside](#whats-inside)
- [Setup](#setup)
- [Run the app](#run-the-app)
- [Writing scripts](#writing-scripts)
- [Data flow / pipeline](#data-flow--pipeline)
- [Stack at a glance](#stack-at-a-glance)
- [Notes](#notes)

---

## What’s inside

- Frontend: static HTML/CSS/JS (`static/index.html`) with a single-page script editor (tab + auto-indent), an octagon sample, and PES/PNG download links.
- Backend: FastAPI (`server.py`) with two endpoints:
  - `POST /export` takes a JSON array of commands.
  - `POST /export_script` takes a small Python-like turtle script (supports `forward`, `backward`, `left`, `right`, `goto`, `penup`, `pendown`, and `for i in range(n):` loops).
- Stitch logic: shared helpers (`api_backend.py`, `embroidery_turtle.py`, `embroidery_utils.py`) to densify points and write PES/PNG via `pyembroidery`.

---

## Setup

1. Install Python 3.9+.
2. (Recommended) Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # on Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Render / headless deploy note

The backend is headless and avoids Tkinter by using `embroidery_utils.py`. No GUI is needed on the server; deploy with:

```bash
uvicorn server:app --host 0.0.0.0 --port $PORT
```

---

## Run the app

```bash
uvicorn server:app --reload
```

Open `http://127.0.0.1:8000` in your browser. You’ll see a script box with a sample octagon, “Run script → PES/PNG”, download links, and a quick command reference.

---

## Writing scripts

- Each line is a command ending with parentheses.
- Movement: `forward(20)`, `backward(10)` (numbers are in turtle units; default 10 mm per unit).
- Turns: `left(90)`, `right(45)` (degrees).
- Pen control: `penup()`, `pendown()`.
- Jump to a coordinate: `goto(x, y)`.
- Loops: repeat steps with `for i in range(N):` followed by indented commands.

Example octagon (loaded by default in the UI):

```
penup()
goto(65, 85)
pendown()
for i in range(8):
    forward(20)
    right(45)
```

---

## Data flow / pipeline

1. Frontend collects your script and uses default sizing (10 mm per turtle unit for a 150 cm hoop) with max stitch 3 mm.
2. Backend parses the script into commands, densifies points to keep stitches under the max, scales to millimeters, and writes PES + PNG in memory.
3. Backend returns base64 PES/PNG; frontend turns them into download links and shows stitch count.

---

## Stack at a glance

- Python + FastAPI for the API.
- `pyembroidery` + `pillow` to generate PES and preview PNG.
- Vanilla HTML/CSS/JS for the UI (served from `/static`).

---

## Notes

- Hoop size is 150 cm (1500 mm); the UI defaults to 10 mm per turtle unit (150 units across the hoop).
- Keep commands inside the 150-unit grid to avoid oversized stitch counts.
- Server is headless (no Tkinter). Deploy with `uvicorn server:app --host 0.0.0.0 --port $PORT`.
