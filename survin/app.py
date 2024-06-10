from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi_htmx import htmx, htmx_init

from survin import database
from fastapi.responses import FileResponse

app = FastAPI()
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
htmx_init(templates=templates)


@app.get("/", response_class=HTMLResponse)
@htmx("index", "index")
async def root_page(request: Request):
    return {"files": sorted(database.get_files(status=database.Status.COMPLETED))}


@app.get("/hello")
def read_root():
    return "<h1>Hello World</h1>"


@app.get("/snapshot/{path:path}")
async def snapshot(path: Path):
    snapshot_file_path = Path("snapshots").joinpath(path.with_suffix(".jpg").name)
    return FileResponse(snapshot_file_path, media_type="image/jpeg")


@app.get("/videoplayer/{path:path}")
async def videoplayer(request: Request, path: Path):
    return templates.TemplateResponse(
        "videoplayer.jinja2", {"request": request, "file": path}
    )


@app.get("/video/{path:path}")
async def video_stream(path: Path):
    def iterfile():
        with open(path, mode="rb") as file_like:
            yield from file_like

    return StreamingResponse(iterfile(), media_type="video/mp4")
