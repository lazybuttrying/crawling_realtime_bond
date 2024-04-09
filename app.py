from fastapi import FastAPI, File, Response
from fastapi.responses import HTMLResponse, FileResponse
from os import listdir
from realtime.util import root_dir

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def index():
    files = listdir(root_dir)
    file_links = ''.join([f'<li><a href="/download/{file}">{file}</a></li>' for file in files])
    return f"""
    <h1>파일 목록</h1>
    <ul>
        {file_links}
    </ul>
    """

@app.get("/download/{filename:path}")
async def download(filename: str, response: Response):
    file_path = f"{root_dir}/{filename}"
    return FileResponse(path=file_path, filename=filename, headers={"Content-Disposition": "attachment"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

