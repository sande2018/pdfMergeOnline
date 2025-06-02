from flask import Flask, render_template, request, send_file
import os
from PyPDF2 import PdfMerger, PdfReader
import uuid
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
MERGED_FILE_NAME = 'merged_file.pdf'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 设置最大文件上传大小为16MB

def generate_unique_filename():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    unique_id = uuid.uuid4().hex[:6]
    return f'merged_file_{timestamp}_{unique_id}.pdf'

def merge_pdfs(files):
    merger = PdfMerger()
    for file in files:
        pdf = PdfReader(file)
        merger.append(pdf)
    merged_file_name = generate_unique_filename()
    merged_file_path = os.path.join(app.config['UPLOAD_FOLDER'], merged_file_name)
    print("合并后文件路径:", merged_file_path)  # 打印合并后的文件路径
    with open(merged_file_path, 'wb') as output:
        try:
            merger.write(output)
            print("合并文件成功写入")
        except Exception as e:
            print("写入合并文件时出错:", e)
            return None, None
    return merged_file_name, merged_file_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/merge', methods=['POST'])
def merge():
    if 'files[]' not in request.files:
        return '没有文件部分'
    files = request.files.getlist('files[]')
    if not files:
        return '没有选择文件'
    merged_file_name, merged_file_path = merge_pdfs(files)
    print("合并后文件路径:", merged_file_path)  # 打印合并后的文件路径
    if os.path.exists(merged_file_path):  # 检查文件是否存在
        # os.remove(merged_file_path)  # 删除服务器上保存的合并后的文件
        download_link = f'/download/{merged_file_name}'
        return download_link
    else:
        return '找不到合并后的文件'

@app.route('/download/<filename>')
def download(filename):
    merged_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(merged_file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
