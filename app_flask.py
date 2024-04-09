from util import root_dir
from flask import Flask, send_file
import os

app = Flask(__name__)

@app.route('/')
def index():
    files = os.listdir(root_dir)
    return f"""
    <h1>파일 목록</h1>
    <ul>
        {''.join([f'<li><a href="/download/{file}">{file}</a></li>' for file in files])}
    </ul>
    """

@app.route('/download/<path:filename>')
def download(filename):
    return send_file(f"{root_dir}/{filename}", as_attachment=True)

if __name__ == '__main__':
    app.run(port=8000, host='0.0.0.0', debug=False)
    
