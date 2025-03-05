from models.minimax import generate_MinMax
from utils.read_file import read_docx, read_txt
from utils.save_audio import save_audio
import argparse
import time
import os
import json


class Generator:
    def __init__(self, text, file, argparsers):
        self.text = text
        self.args = argparsers
        self.file = file
        self.inform = {}
        self.stop_time = 0.8
        self.number_order = []

    def analyze_text(self):
        if self.text == '':
            if '.txt' in self.file:
                self.text = read_txt(self.file)
            elif '.docx' in self.file:
                self.text = read_docx(self.file)
            else:
                raise ValueError("不支持的文件类型，请联系管理员申请扩充文件类型或者修改格式")
        else:
            self.text = self.text.split('\n')
        return self.text
    
    def is_chinese(self, word):
        # 判断这一段话是否为中文，是就返回True
        ch_count = 0
        en_count = 0
        for ch in word:
            if '\u4e00' <= ch <= '\u9fff':
                ch_count += 1
            else:
                en_count += 1
        if ch_count > en_count:
            return True
        else:
            return False
    
    def save_json(self, audio_path, text, language, gender, number, long_text=False):
        temp_dict = {}
        if gender == 'female':
            speed = self.args.female_speed
            volume = self.args.female_volume
            tune = self.args.female_tune
            voice = self.args.female_voice
        else:
            speed = self.args.male_speed
            volume = self.args.male_volume
            tune = self.args.male_tune
            voice = self.args.male_voice

        if language == 'en':
            #需要记录两次回答的内容
            temp_dict['gender'] = gender
            temp_dict['audio_path'] = audio_path
            temp_dict['speed'] = speed
            temp_dict['volume'] = volume
            temp_dict['tune'] = tune
            temp_dict['voice'] = voice
            temp_dict['text'] = text
            temp_dict['stop_time'] = self.stop_time
            temp_dict['long_text'] = long_text
            self.inform['line_{}'.format(number)] = temp_dict
        else:
            #中文需要记录一次回答的内容
            temp_dict['speed'] = speed
            temp_dict['volume'] = volume
            temp_dict['tune'] = tune
            temp_dict['voice'] = voice
            temp_dict['gender'] = gender
            temp_dict['audio_path'] = audio_path
            temp_dict['text'] = text
            temp_dict['stop_time'] = self.stop_time
            self.inform['line_{}'.format(number)] = temp_dict
            
            #Todo:这边还要根据generate_minmax做修改

    def generate_chinese_tts(self, gen_text, i):
        gender = 'female'
        gen_audio = generate_MinMax(self.args, gen_text, gender)
        audio_path = save_audio(gen_audio, i, self.args)
        self.save_json(audio_path, self.text[i], 'zh', gender, i)
        self.number_order.append(i)#中文不存在生成两边的情况，因此直接保存就可以了

    def generate_english_tts(self, gen_text, i, gender, long_text=False):
        if long_text:
            gen_audio = generate_MinMax(self.args, gen_text, 'female')
            audio_path = save_audio(gen_audio, i, self.args)
            self.save_json(audio_path, self.text[i], 'en', 'female', i, long_text)
            gen_audio = generate_MinMax(self.args, gen_text, 'male')
            audio_path2 = save_audio(gen_audio, str(i)+'_1', self.args)
            self.save_json(audio_path2, self.text[i], 'en', 'male', str(i)+'_1', long_text)
        else:
            gen_audio = generate_MinMax(self.args, gen_text, gender)
            audio_path = save_audio(gen_audio, i, self.args)
            audio_path2 = save_audio(gen_audio, str(i)+'_1', self.args)
            paths = [audio_path, audio_path2]
            self.save_json(paths, self.text[i], 'en', gender, i)
        # Todo: 英文生成器

    def record_order_list(self, ordlist):
        for i in range(len(ordlist)):
            self.number_order.append(str(ordlist[i]))
        for i in range(len(ordlist)):
            self.number_order.append(str(ordlist[i]) + '_1')

    def generate_audio(self):
        self.text = self.analyze_text()

        # Generate audio file from text
        #创建一个存储英文信息的列表
        text_list = []
        for i in range(len(self.text)):
            print(i)
            if i == 0: #这一段一定是中文，所以不需要管，而且时间间隔也不用管
                self.language = 'zh'
                gen_text = self.text[i] + "<#{}#>".format(self.stop_time)#结束添加0.3s的停顿
                self.generate_chinese_tts(gen_text, i)
            elif self.is_chinese(self.text[i]):
                #ToDo:中文文本中需要添加如果前面是英文的时候，需要判断一个list中是否还保存了数值，如果保存了说明是在第二题中。
                #对所有文本执行结束之后，添加一个0.3s的停顿
                gen_text = self.text[i] + "<#{}#>".format(self.stop_time)#结束添加0.3s的停顿
                #如果是中文字符，需要考虑一下几种情况
                if i == len(self.text) - 1: #这一段是整个文章的最后一段，一定也是中文
                    self.generate_chinese_tts(gen_text, i)
                    #将文本的保存信息存储到这里
                else: #这一段是中间的中文，需要判断前后是否都是中文
                    if self.is_chinese(self.text[i-1]) and self.is_chinese(self.text[i+1]): #前后都是中文
                        self.generate_chinese_tts(gen_text, i)
                    elif self.is_chinese(self.text[i-1]) and not self.is_chinese(self.text[i+1]): #前是中文，后不是中文
                        self.generate_chinese_tts(gen_text+ "<#{}#>".format(self.stop_time*2), i)
                    elif not self.is_chinese(self.text[i-1]) and self.is_chinese(self.text[i+1]): #前不是中文，后是中文
                        #在这里添加一个判断，如果text_list中保存了数字，那么说明是第二题或第三题的情况，先考虑第二题
                        if len(text_list) > 0: 
                            if 'W:' in self.text[text_list[0]] or 'M:' in self.text[text_list[0]]:
                                #说明是第二题,这时就可以记录一下顺序了
                                self.record_order_list(text_list)
                                text_list = []
                            else:
                                self.record_order_list(text_list)
                                text_list = []
                                pass
                        self.generate_chinese_tts("<#{}#>".format(self.stop_time*2) + gen_text, i)
                    else: #前后都不是中文
                        #在这里添加一个判断，如果text_list中保存了数字，那么说明是第二题或第三题的情况，先考虑第二题
                        if len(text_list) > 0: 
                            if 'W:' in self.text[text_list[0]] or 'M:' in self.text[text_list[0]]:
                                #说明是第二题,这时就可以记录一下顺序了
                                self.record_order_list(text_list)
                                text_list = []
                            else:
                                #这是第三种情况
                                self.record_order_list(text_list)
                                text_list = []
                                pass
                        self.generate_chinese_tts("<#{}#>".format(self.stop_time*2) + gen_text + "<#{}#>".format(self.stop_time*2), i)
            else:
                #下面全部都是非英语的情况，这个时候就需要考虑很多问题了，首先三种题目类型
                #1. 第一个题目开始于number，包含W,M,Q三个元素。需要记录三行，然后保存每一行的内容，并且还要重新录制一遍
                #记录W和M的数量和内容，保存到list种，如果出现Q并且W和M的数量为1，那么就是第一题
                if "W:" in self.text[i]:
                    generate_long_text = False
                    #如果出现W，那么就记录W的内容，替换掉W:不能转音频
                    gen_text = self.text[i].replace("W:", "<#{}#>".format(self.stop_time)) + "<#{}#>".format(self.stop_time)
                    gender = 'female'
                    text_list.append(i) #将文本的保存信息存储到这里, 这个用来记录数量
                    self.generate_english_tts(gen_text, i, gender, generate_long_text)
                elif "M:" in self.text[i]:
                    generate_long_text = False
                    #如果出现W，那么就记录W的内容，替换掉W:不能转音频
                    gen_text = self.text[i].replace("M:", "<#{}#>".format(self.stop_time)) + "<#{}#>".format(self.stop_time)
                    gender = 'male'
                    text_list.append(i) #将文本的保存信息存储到这里, 这个用来记录数量
                    self.generate_english_tts(gen_text, i, gender, generate_long_text)            
                elif "Question:" in self.text[i]:
                    generate_long_text = False
                    #如果出现W，那么就记录W的内容，替换掉W:不能转音频
                    gen_text = self.text[i] + "<#{}#>".format(self.stop_time)
                    gender = 'female'
                    text_list.append(i) #将文本的保存信息存储到这里, 这个用来记录数量
                    self.generate_english_tts(gen_text, i, gender, generate_long_text)
                    self.record_order_list(text_list) #保存顺序结束之后要删除list中的内容
                    #保存顺序结束之后要删除list中的内容
                    text_list = []
                else:
                    #就是是英文，但是却并不是W，M，Q的情况，这个时候需要全部储存起来，并且判断一下文本是否会过长
                    generate_long_text = True
                    if len(self.text[i]) > 5000:
                        gen_text = self.text[i].split('.')
                        #以'.'作为分割
                        for j in range(len(gen_text)):
                            gender = 'female'
                            self.generate_english_tts(gen_text[j] + "<#{}#>".format(self.stop_time), '{}_{}'.format(i,j), gender, generate_long_text)
                            text_list.append(i+j)
                    else:
                        gen_text = self.text[i].replace('.', '.<#{}#>'.format(self.stop_time))
                        gender = 'female'
                        self.generate_english_tts(gen_text + "<#{}#>".format(self.stop_time), i, gender, generate_long_text)
                        text_list.append(i)
                    
        if text_list != []:
            self.record_order_list(text_list)
        print(self.number_order)

        self.inform['save_path'] = self.args.save_path
        self.inform['number_order'] = self.number_order
        with open('{}/data.json'.format(self.args.save_path), 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.inform, ensure_ascii=False, indent=4))
                #2. 第二种题目起始于中文，结束于中文，包含W，M，两个元素。全部结束之后还需要保存一次
                #3. 第三种题目是长文本，存在分段的可能，因此还是定义为起始于中文结束于中文。

        return self.args.save_path


def arg():
    args = argparse.ArgumentParser("对话控制台")

    args.add_argument('--generator', default='MinMax', type=str,
                      help='语音生成大模型选择')
    args.add_argument('--stop_time', default=0.5, type=float)
    args.add_argument('--user_id', default='1', type=str)
    args.add_argument('--times', default=0, type=int)
    # args.add_argument('--txt_path', default="D:\\code\\listen8.txt", type=str,
    #                   help='语音生成大模型选择')
    
    args.add_argument('--text', type=str, default='Hi, I\'m Lihua, I\'m a student in XJTLU, it\'s really nice to see you. Why not have a dinner together?')
    args.add_argument('--file', type=str, default="./test.txt")
    args.add_argument("--save_path", type=str, default="")

    args.add_argument('--music_path', default="D:\\pythonpro\\dataset\\Listening_Cindy_24_10_23.mp3", type=str, help='背景音乐路径') #最新10.26
    args.add_argument('--temp_dir', default='./temp', type=str, help='临时保存的位置')
    args.add_argument('--audio_save_path', default='./output.mp3', type=str, help="最终音频保存位置")
    args.add_argument('--MM_model', default='speech-01-turbo', type=str, help='修改minmax的模型')

    args.add_argument('--gender', type=str, default='female')
    args.add_argument('--language', type=str, default='en')
    args.add_argument('--number', type=int, default=1)
    args.add_argument('--female_speed', type=int, default=1)
    args.add_argument('--male_speed', type=int, default=1)
    args.add_argument('--male_tune', type=int, default=1)
    args.add_argument('--female_tune', type=int, default=1)
    args.add_argument('--male_voice', type=str, default='audiobook_male_1')
    args.add_argument('--female_voice', type=str, default='presenter_female')
    args.add_argument('--male_volume', type=int, default=1)
    args.add_argument('--female_volume', type=int, default=1)
    args = args.parse_args()
    return args

if __name__ == '__main__':
    args = arg()
    print('start mission')
    times = int(time.time())
    args.times = times
    args.save_path = './temp_{}_{}'.format(args.user_id, times)
    audio_generator = Generator('', args.file, args).generate_audio()