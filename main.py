from flask import Flask
from flask import render_template, request
import logging
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)   #解决跨域问题

@app.route('/') #主页地址,“装饰器”
def web():
    return render_template('index.html') #把index.html文件读进来，再交给浏览器

@app.route('/static/<path:path>')
def static_files(path):
    return app.send_static_file(path)

def runWeb():
    app.logger.setLevel(logging.DEBUG)
    app.run(host='0.0.0.0',debug=False,port=8000) #127.0.0.1 回路 自己返回自己

# 上传文件到服务器指定到文件夹中（一定要放在自己起服务到那个文件夹，不要放在本地的其他文件夹中，不然服务器访问不了你的文件）
UPLOAD_FOLDER = ''
# 上传文件格式
ALLOWED_EXTENSIONS = set(['tar'])

app.config['UPLOAD_POLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods = ['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        print('request======>',request.files.get('tar_file').filename) #get('photo')是input标签 name的名称，切忌写错！
        file = request.files['tar_file']
        if file and allowed_file(file.filename):
            filename = "seis.tar"#str(time.time()) + "_" + secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_POLDER'],filename))
            # url = UPLOAD_FOLDER+filename

            log = ""
            with open(r"static\log.json","w",encoding="utf-8") as f:
                json = "{\"LOG\":\"" + log + "\"}"
                f.write(json)

            os.system('python simulation_Web.py')

            return render_template('index.html')
        else:
            log = "输入文件不合规"
            with open(r"static\log.json","w",encoding="utf-8") as f:
                json = "{\"LOG\":\"" + log + "\"}"
                f.write(json)
            return render_template('index.html')

with open(r"static\sc_eew.json","w",encoding="utf-8") as f:
    json = "{\"ID\": 111,\"EventID\": \"202401010704184\",\"ReportTime\": \"2024-05-25 09:54:28\",\"ReportNum\": 4,\"OriginTime\": \"2000-05-25 09:54:28\",\"HypoCenter\": \"架空模拟\",\"Latitude\": 31.517,\"Longitude\": 132.250,\"Magunitude\": 5.0, \"Depth\": 22.0, \"Delta\": 11.970983002819295}"
    f.write(json)
with open(r"static\switch.json","w",encoding="utf-8") as f:
    json = "{\"o\":1}"
    f.write(json)

runWeb()
