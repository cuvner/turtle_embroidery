# student_main.py

import turtle
from embroidery_turtle import EmbroideryTurtle, export_to_embroidery

# ----- SETTINGS STUDENTS CAN CHANGE -----

SCALE = 10               # ← try 3, 5, 8, 10 to make it bigger/smaller
MAX_STITCH_MM = 3.0
PES_FILENAME = "student_design.pes"
PNG_FILENAME = "student_design.png"

# ----------------------------------------

screen = turtle.Screen()
screen.setup(800, 800)
screen.title("Embroidery Turtle – with Scaling")

# Hoop is still 150×150 mm, but turtle units are scaled later:
screen.setworldcoordinates(0, 0, 150, 150)

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
