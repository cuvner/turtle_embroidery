# Embroidery Turtle Web App

Friendly web app for drawing simple turtle commands and exporting PES/PNG for a 150 cm hoop (10 mm per turtle unit).

![Embroidery turtle example](images/turtle_embroider.png)

Embroidery: the art of decorating fabric with a needle and thread. Visual reference: ![Embroidery machine](https://www.brothersewingshop.co.uk/image/cache/catalog/Brother/F540E-500x500.jpg)

## What’s inside

- Frontend: static HTML/CSS/JS (`static/index.html`). Edit commands or a simple turtle-style script and export PES/PNG.
- Backend: FastAPI (`server.py`) with two endpoints:
  - `POST /export` takes a JSON array of commands.
  - `POST /export_script` takes a small Python-like turtle script (supports `forward`, `backward`, `left`, `right`, `goto`, `penup`, `pendown`, and `for i in range(n):` loops).
- Stitch logic: shared helpers (`api_backend.py`, `embroidery_turtle.py`) to densify points and write PES/PNG via `pyembroidery`.

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

## Run the app

```bash
uvicorn server:app --reload
```

Open `http://127.0.0.1:8000` in your browser. The UI includes:

- Scale (mm per turtle unit) and max stitch length controls.
- JSON commands editor and a “Load sample star” button.
- Script editor and a “Run script → PES/PNG” button.
- Download links for PES/PNG and a stitch count after export.

## Writing scripts

- Each line is a command ending with parentheses.
- Movement: `forward(20)`, `backward(10)` (numbers are in turtle units; default 10 mm per unit).
- Turns: `left(90)`, `right(45)` (degrees).
- Pen control: `penup()`, `pendown()`.
- Jump to a coordinate: `goto(x, y)`.
- Loops: repeat steps with `for i in range(N):` followed by indented commands.

Example star script (already in the UI):

```
penup()
goto(65, 85)
pendown()
for i in range(8):
    forward(20)
    right(45)
```

## Data flow / pipeline

1. Frontend collects your commands or script and your scale/stitch settings.
2. Backend parses commands (or converts the script to commands), densifies points so stitches stay under `max_stitch_mm`, scales to millimeters (default 10 mm per turtle unit for the 150 cm hoop), and writes PES + PNG in memory.
3. Backend returns base64 PES/PNG; frontend turns them into download links.

## Stack at a glance

- Python + FastAPI for the API.
- `pyembroidery` + `pillow` to generate PES and preview PNG.
- Vanilla HTML/CSS/JS for the UI (served from `/static`).

## Notes

- Hoop size is 150 cm (1500 mm); the UI defaults to 10 mm per turtle unit (150 units across the hoop).
- Keep commands small and inside the 150-unit grid to avoid oversized stitch counts.
