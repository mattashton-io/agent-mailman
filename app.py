from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import datetime
import main
import uvicorn
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "year": datetime.datetime.now().year})

@app.post("/run", response_class=HTMLResponse)
async def run_agent(request: Request):
    # Call the logic in main.py
    logs = main.run_agent()
    return templates.TemplateResponse("index.html", {"request": request, "logs": logs, "year": datetime.datetime.now().year})

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    uvicorn.run(app, host='0.0.0.0', port=port)
