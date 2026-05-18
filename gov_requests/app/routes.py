from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, Form, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from utils import process_documents

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"request": request}
    )


@router.post("/generate")
async def generate_documents(
    start_date: str = Form(...),
    end_date: str = Form(...)
):
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()

    file_path = process_documents(start, end)

    return FileResponse(
        path=file_path,
        filename=Path(file_path).name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )