import os

from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()
OUTPUT_DIR = "data"


@app.get("/discord")
async def read_items(channel_id: str | None = None):

    path_to_channel_json: str = os.path.join(OUTPUT_DIR, f"{channel_id}.json")

    return FileResponse(
        path=path_to_channel_json,
        media_type="application/json",
    )
