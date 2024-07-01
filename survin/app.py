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
def root_page(request: Request):
    return {
        "newfiles": sorted(
            database.get_videos_by_status(status=database.Status.NEW),
            key=lambda x: x.timestamp,
        ),
        "detectedfiles": sorted(
            (
                video
                for video in database.get_videos_by_status(
                    status=database.Status.COMPLETED
                )
                if video.classifications
            ),
            key=lambda x: x.timestamp,
        ),
        "notdetectedfiles": sorted(
            (
                video
                for video in database.get_videos_by_status(
                    status=database.Status.COMPLETED
                )
                if not video.classifications
            ),
            key=lambda x: x.timestamp,
        ),
    }


@app.get("/snapshot/{guid:str}")
def snapshot(request: Request, guid: str):
    path = database.get_video_path(guid)
    if path is None:
        return "File not found", 404
    snapshot_file_path = Path("snapshots").joinpath(path.with_suffix(".jpg").name)
    response = FileResponse(
        snapshot_file_path,
        media_type="image/jpeg",
        headers={"Cache-Control": "max-age=3600"},
    )
    return response


@app.get("/videoplayer/{guid:str}")
def videoplayer(request: Request, guid: str):
    return templates.TemplateResponse(
        "videoplayer.jinja2", {"request": request, "guid": guid}
    )


@app.get("/video/{guid:str}")
def video_stream(guid: str):
    path = database.get_video_path(guid)
    if path is None:
        return "File not found", 404

    def iterfile():
        with open(path, mode="rb") as file_like:
            yield from file_like

    return StreamingResponse(iterfile(), media_type="video/mp4")
