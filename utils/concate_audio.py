import json
import os
from scipy.io.wavfile import read, WavFileWarning
import soundfile as sf
import numpy as np
import time

def concate_audio(save_path):
    info = json_path.split('_')
    json_path = os.join(save_path, 'data.json')
# 打开并读取JSON文件
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

# 获取order_number列表
    order_numbers = data.get('order_number', [])
    signal = []

    for i in order_numbers:
        # 拼接音频文件路径
        audio_path = os.path.join(save_path, f'output_{i}.wav')

        try:
            sr, data = read(audio_path)
        except WavFileWarning:
            number += 1
            continue
        signal.append(data)
        number += 1
    new_data = np.concatenate(signal, axis = 0)
    dates = int(time.time())
    file_names = "./output_english_{}_{}.wav".format(info[1], info[2])

    sf.write(file_names, new_data, sr)
    return file_names


