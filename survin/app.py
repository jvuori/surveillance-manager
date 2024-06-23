from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_htmx import htmx, htmx_init

from survin import database
from fastapi.responses import FileResponse

app = FastAPI()
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
app.mount(
    "/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static"
)
htmx_init(templates=templates)


@app.get("/", response_class=HTMLResponse)
@htmx("index", "index")
async def root_page(request: Request):
    return {
        "detectedfiles": sorted(
            (file_path, classifications)
            for file_path in database.get_files(status=database.Status.COMPLETED)
            if (classifications := database.get_classifications(file_path))
        ),
        "notdetectedfiles": sorted(
            (file_path, classifications)
            for file_path in database.get_files(status=database.Status.COMPLETED)
            if not (classifications := database.get_classifications(file_path))
        ),
    }


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
