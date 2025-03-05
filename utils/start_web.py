from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from utils.generate_audio import generate_MinMax
import os
from audio_generator import Generator
# import argparse
import json
from utils.concate_audio import concate_audio
from flask_restx import Api, Resource

app = Flask(__name__, template_folder='../templates')
app.secret_key = '123'
app.config['UPLOAD_FOLDER'] = '../uploads'
app.config['MAX_CONTENT_PATH'] = 1000000

api = Api(app, version='1.0', title='Voice Preview API',
          description='A simple API to preview voice')

ns = api.namespace('voice', description='Operations related to voice preview')

class VoicePreviewApp:
    def __init__(self, args):
        self.app = app
        self.register_routes()
        self.args = args
        self.json_path = ''

    def register_routes(self):
        @self.app.route('/', methods=['GET', 'POST'])
        def index():
            return redirect(url_for('preview_voice'))
        
        @self.app.route('/generate', methods=['GET', 'POST'])
        def generate():
                # 读取本地JSON文件
            with open('data.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
            return render_template('generate.html', data=data)

        @self.app.route('/preview_voice', methods=['GET', 'POST'])
        def preview_voice():
            print(1)
            if request.method == 'POST':
                # 获取AJAX请求中的数据
                self.args.gender = request.json['gender']
                self.args.female_voice = request.json['female_voice']
                self.args.male_voice = request.json['male_voice']
                self.args.female_speed = request.json['female_speed']
                self.args.male_speed = request.json['male_speed']
                self.args.female_tune = request.json['female_tune']
                self.args.male_tune = request.json['male_tune']
                self.args.female_volume = request.json['fevolume']
                self.args.male_volume = request.json['mavolume']
                # 在这里处理接收到的性别数据
                # 例如，可以播放对应性别的试听音频
                if self.args.gender == 'male':
                    voice = self.args.male_voice
                    speed = self.args.male_speed
                    tune = self.args.male_tune
                    volume = self.args.male_volume
                elif self.args.gender == 'female':
                    voice = self.args.female_voice
                    speed = self.args.female_speed
                    tune = self.args.female_tune
                    volume = self.args.female_volume

                text_test = "Hi, I'm Lihua, I'm a student in XJTLU, it's really nice to see you. Why not have a dinner together?"
                audio_file = generate_MinMax(voice, tune, speed, text_test.encode('utf-8'), volume)

                return send_file(audio_file, mimetype='audio/mpeg')
            # 返回响应
            return render_template('home.html')
        
        @self.app.route('/preview_voice', methods=['POST','GET'])
        def upload_file():
            if request.method == 'POST':
                try:
                    file = request.files.get('file')
                    text = request.form.get('text')

                    # 优先级：如果存在有效文件，则忽略文本
                    if file and file.filename != '':
                        # 处理文件上传
                        if not os.path.exists(app.config['UPLOAD_FOLDER']):
                            os.makedirs(app.config['UPLOAD_FOLDER'])
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                        file.save(file_path)
                        # 调用生成逻辑（仅文件）
                        self.json_path = Generator('', file_path, self.args).generate_audio()  # 传递None作为text
                        return jsonify({
                            'status': 'success',
                            'message': 'File processed',
                            'json_path': json_path
                        })
                        return redirect(url_for('generate'))
                    elif text:
                        # 处理文本
                        self.json_path = Generator(text, '', self.args).generate_audio()  # 传递None作为file_path
                        return jsonify({
                            'status': 'success',
                            'message': 'Text processed',
                            'json_path': json_path
                        })
                        return redirect(url_for('generate'))

                    else:
                        # 两者都不存在
                        return jsonify({'error': 'No file or text provided'}), 400

                except Exception as e:
                    return jsonify({'error': str(e)}), 500
                
        @self.app.route('/generate', methods=['POST'])
        def generate_one_row():
            if request.method == 'POST':
                # 获取AJAX请求中的数据
                gender = request.json['gender']
                voice = request.json['voice']
                speed = request.json['speed']
                tune = request.json['tune']
                volume = request.json['volume']
                text = request.json['text']

                audio_file = generate_MinMax(voice, tune, speed, text.encode('utf-8'), volume)
                return send_file(audio_file, mimetype='audio/mpeg')
            return render_template('generate.html')
                # 在这里处理接收到的数据

        @self.app.route('/generate', methods=['POST'])
        def concate_audio():
            if request.method == 'POST':
                if request.json['concate_audio']:
                    audio_path = concate_audio(self.json_path)
                    return send_file(audio_path, mimetype='audio/mpeg')
            
            return render_template('generate.html')



                    
    def run_server(self):
        self.app.run(debug=True, port=887)

if __name__ == '__main__':

    app = VoicePreviewApp()
    app.run_server()
