# student_main.py

import turtle
from embroidery_turtle import EmbroideryTurtle, export_to_embroidery

# ----- SETTINGS STUDENTS CAN CHANGE -----

HOOP_SIZE_MM = 1500          # actual hoop is 150 cm = 1500 mm
WORLD_SIZE_UNITS = 150       # keep drawing grid at 150 units
SCALE = HOOP_SIZE_MM / WORLD_SIZE_UNITS  # auto-scale turtle units to hoop mm
MAX_STITCH_MM = 3.0
PES_FILENAME = "student_design.pes"
PNG_FILENAME = "student_design.png"

# ----------------------------------------

screen = turtle.Screen()
screen.setup(800, 800)
screen.title("Embroidery Turtle – with Scaling")

# Map a 150-unit grid onto the 150 cm (1500 mm) hoop.
screen.setworldcoordinates(0, 0, WORLD_SIZE_UNITS, WORLD_SIZE_UNITS)

t = EmbroideryTurtle()
t.speed(1)
t.hideturtle()

# ---- DRAW SOMETHING ----
t.penup()
t.goto(65, 85)
t.pendown()

for i in range(8):
    t.forward(20)
    t.right(45)

# ---- EXPORT ----
export_to_embroidery(
    t,
    scale_mm=SCALE,           # << SCALE applied here
    max_stitch_mm=MAX_STITCH_MM,
    pes_filename=PES_FILENAME,
    png_filename=PNG_FILENAME,
    show_preview=True,
)

turtle.done()
