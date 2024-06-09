from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_htmx import htmx, htmx_init

app = FastAPI()
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
htmx_init(templates=templates)

@app.get("/", response_class=HTMLResponse)
@htmx("index", "index")
async def root_page(request: Request):
    return {}

@app.get("/hello")
def read_root():
    return "<h1>Hello World</h1>"
