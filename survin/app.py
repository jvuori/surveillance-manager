import datetime
import mimetypes
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_htmx import htmx, htmx_init

from survin import database

app = FastAPI()
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
app.mount(
    "/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static"
)
htmx_init(templates=templates)


@app.get("/", response_class=HTMLResponse)
@htmx("index", "index")
def root_page(
    request: Request,
    date: datetime.date | None = None,
    source: str | None = None,
    detected: bool | None = None,
):
    dates = database.get_dates()
    selected_date = date or dates[-1]

    sources = sorted(database.get_sources(selected_date))
    if source in sources:
        selected_source = source
    else:
        selected_source = sources[0] if sources else ""

    def get_detected(prefix: str = "&"):
        if detected is None:
            return ""
        return f"{prefix}detected={detected}"

    return {
        "dates": dates,
        "selected_date": selected_date,
        "sources": sources,
        "selected_source": selected_source,
        "detected": detected,
        "get_detected": get_detected,
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


@app.get("/videocontainer/{date:str}/{source:str}")
def video_container(
    request: Request, date: str, source: str, detected: bool | None = None
):
    print("detected", detected)
    return templates.TemplateResponse(
        "video_container.jinja2",
        {
            "request": request,
            "date": datetime.date.fromisoformat(date),
            "videos": sorted(
                (
                    [
                        video
                        for video in database.get_videos_by_date_and_source(
                            datetime.date.fromisoformat(date), source
                        )
                        if detected is None or bool(video.classifications) == detected
                    ]
                ),
                key=lambda x: x.timestamp,
            ),
        },
    )


@app.get("/videoplayer/{guid:str}")
def videoplayer(request: Request, guid: str):
    return templates.TemplateResponse(
        "videoplayer.jinja2", {"request": request, "guid": guid}
    )


@app.get("/video/{guid:str}")
async def video_stream(guid: str):
    path = database.get_video_path(guid)
    if path is None:
        return "File not found", 404

    # Use mimetypes to automatically detect the correct media type
    media_type, _ = mimetypes.guess_type(str(path))

    # Fallback to video/mp4 if detection fails or returns non-video type
    if not media_type or not media_type.startswith("video/"):
        media_type = "video/mp4"

    async def iterfile():
        with open(path, mode="rb") as file_like:
            yield file_like.read()

    return StreamingResponse(iterfile(), media_type=media_type)
