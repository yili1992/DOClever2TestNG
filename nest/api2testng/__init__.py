#encoding = utf-8
__author__ = 'zhaoli'


import os
from os.path import join, exists
import arrow
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import *
from .Api2Testng.TACodeGenerator import transfer2code
import zipfile

UPLOAD_FOLDER = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'uploads')
CODE_FOLDER = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'codes')
ALLOWED_EXTENSIONS = ['json']
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app, supports_credentials=True)
app.config.from_object(__name__)
app.secret_key = 'api2testng'


def init():
    if not exists(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)
    if not exists(CODE_FOLDER):
        os.mkdir(CODE_FOLDER)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def save_file(file):
    filename = ""
    if file and allowed_file(file.filename):
        filename = os.path.basename(file.filename)
        upload_to = join(app.config['UPLOAD_FOLDER'], filename)

        if exists(upload_to):
            filename = '{}_{}.json'.format(filename[:-5], arrow.now().strftime('%Y%m%d_%H%M%S'))
            upload_to = join(app.config['UPLOAD_FOLDER'], filename)

        file.save(upload_to)
    return filename


def write_zip(z, target_path, target_folder):
    for d in os.listdir(target_path):
        if os.path.isdir(join(target_path, d)):
            write_zip(z, join(target_path, d), join(target_folder, d))
        else:
            z.write(target_path+os.sep+d, target_folder+os.sep+d)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST', 'GET'])
def uploaded_file():
    if request.method == 'POST':
        file = request.files['file']
        filename = save_file(file)
        result = {"code": "0",
                  "msg": "上传成功",
                  "imgURL": filename
        }

        return jsonify(result)

@app.route('/transfer', methods=['POST', 'GET'])
def transfer_code():
    if request.method == 'POST':
        data = request.json
        author = data.get('author', '')
        group = data.get('group', '')
        filename = data.get('filename', '')
        base_url = data.get('url', '')
        data_provider = data.get('dataProvider', False)
        target_folder = filename.split('.')[0]
        target_path = join(CODE_FOLDER, target_folder)
        if os.path.exists(target_path):
            import shutil
            shutil.rmtree(target_path)
            os.remove(target_path+'.zip')
        os.mkdir(target_path)
        try:
            fail_dict = transfer2code(group, join(app.config['UPLOAD_FOLDER'], filename),  target_path, author, base_url, data_provider)
            print(fail_dict)
            zip_file = join(CODE_FOLDER, target_folder+'.zip')
            z = zipfile.ZipFile(zip_file, 'w')
            write_zip(z, target_path, target_folder)
            z.close()
            if len(fail_dict) == 0:
                result = {"code": "00000",
                          "msg": "转换成功",
                          'filename': target_folder+'.zip'}
            else:
                result = {"code": "00000",
                          "msg": "转换完成: 失败列表:"+str(fail_dict),
                          'filename': target_folder+'.zip'}
        except Exception as e:
            result = {"code": "99999",
                      "msg": "转换失败:"+str(e)}

        return jsonify({"result": result})

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['CODE_FOLDER'], filename)

init()