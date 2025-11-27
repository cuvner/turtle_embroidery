# server.py

from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, validator

from api_backend import generate_from_commands, script_to_commands


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
IMAGES_DIR = BASE_DIR / "images"


class CommandModel(BaseModel):
    op: str
    value: Optional[float] = Field(default=0.0)
    x: Optional[float] = None
    y: Optional[float] = None

    @validator("op")
    def normalize_op(cls, v: str) -> str:
        return v.lower()


class ExportRequest(BaseModel):
    commands: List[CommandModel]
    scale_mm: float = Field(default=1500 / 150, description="mm per turtle unit")
    max_stitch_mm: float = Field(default=3.0, description="max stitch length in mm")

    @validator("scale_mm", "max_stitch_mm")
    def must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("must be positive")
        return v


app = FastAPI(title="Embroidery Turtle", version="0.1.0")


@app.get("/")
def serve_index():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Embroidery Turtle API. POST /export with commands."}


@app.post("/export")
def export_design(req: ExportRequest):
    if not req.commands:
        raise HTTPException(status_code=400, detail="commands cannot be empty")

    try:
        outputs = generate_from_commands(
            [cmd.dict() for cmd in req.commands],
            scale_mm=req.scale_mm,
            max_stitch_mm=req.max_stitch_mm,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # pragma: no cover - guard rail
        raise HTTPException(status_code=500, detail=str(exc))

    return outputs


class ScriptRequest(BaseModel):
    script: str
    scale_mm: float = Field(default=1500 / 150)
    max_stitch_mm: float = Field(default=3.0)

    @validator("scale_mm", "max_stitch_mm")
    def must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("must be positive")
        return v


@app.post("/export_script")
def export_script(req: ScriptRequest):
    try:
        commands = script_to_commands(req.script)
        outputs = generate_from_commands(
            commands,
            scale_mm=req.scale_mm,
            max_stitch_mm=req.max_stitch_mm,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))

    return {
        "commands": commands,
        **outputs,
    }


if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

if IMAGES_DIR.exists():
    app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")
