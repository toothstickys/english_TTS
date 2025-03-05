import argparse
from utils.start_web import VoicePreviewApp

def arg():
    args = argparse.ArgumentParser("对话控制台")

    args.add_argument('--generator', default='MinMax', type=str,
                      help='语音生成大模型选择')
    # args.add_argument('--txt_path', default="D:\\code\\listen8.txt", type=str,
    #                   help='语音生成大模型选择')
    
    args.add_argument('--text', type=str, default='Hi, I\'m Lihua, I\'m a student in XJTLU, it\'s really nice to see you. Why not have a dinner together?')
    args.add_argument('--file', type=str, default="D:\\code\\listen2.docx")

    args.add_argument('--music_path', default="D:\\pythonpro\\dataset\\Listening_Cindy_24_10_23.mp3", type=str, help='背景音乐路径') #最新10.26
    args.add_argument('--temp_dir', default='./temp', type=str, help='临时保存的位置')
    args.add_argument('--audio_save_path', default='./output.mp3', type=str, help="最终音频保存位置")
    args.add_argument('--MM_model', default='speech-01-turbo', type=str, help='修改minmax的模型')

    args.add_argument('--gender', type=str, default='male')
    args.add_argument('--language', type=str, default='en')
    args.add_argument('--number', type=int, default=1)
    args.add_argument('--female_speed', type=int, default=1)
    args.add_argument('--male_speed', type=int, default=1)
    args.add_argument('--male_tune', type=int, default=1)
    args.add_argument('--female_tune', type=int, default=1)
    args.add_argument('--male_voice', type=str, default='audiobook_male_1')
    args.add_argument('--female_voice', type=str, default='presenter_female')
    args = args.parse_args()
    return args

def main():
    # 调用arg()函数获取命令行参数，并将其赋值给变量args
    args = arg()
    app = VoicePreviewApp(args)
    app.run_server()

if __name__ == '__main__':
    main()