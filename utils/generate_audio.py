import json
import requests
import os
def generate_MinMax(Voice, pitch, speed, text, volume):
    #调用minmax接口
    group_id = '1862062097068724524'  # 请输入您的group_id
    api_key = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiIxMTEiLCJVc2VyTmFtZSI6IjExMSIsIkFjY291bnQiOiIiLCJTdWJqZWN0SUQiOiIxODYyMDYyMDk3MDc3MTEzMTMyIiwiUGhvbmUiOiIxMzkxNDAwNjk3NCIsIkdyb3VwSUQiOiIxODYyMDYyMDk3MDY4NzI0NTI0IiwiUGFnZU5hbWUiOiIiLCJNYWlsIjoiIiwiQ3JlYXRlVGltZSI6IjIwMjQtMTItMTAgMTc6MzM6MDAiLCJUb2tlblR5cGUiOjEsImlzcyI6Im1pbmltYXgifQ.GTY7YaODs0a9JwYWZz3TSGtBLvJcgfK-IWzgCe_RoFFqOcd2NUXQjm93Sy7IJIhpYD_kgBrXFrmE6yzOYJvexI6KbURk_KtKhWiaGL_8kDju0s5W7UuNCMOSj_mEChENeprHpHM6nMD8iZLhxM1vazQ2Utmwv899K6heAoCoIrWy1C0CSx4eoVi_tOIatcCQ1E550f-vzyWRnKkT8tbOreBebgIiaWxTSbGRCn3WsPqCykAUrLsmNj0B6dBTG5NjoZlYoj4aCfIBRr17S2MuEhx4qk25m1tp7iIm-OGp9gsstFQeHECxTIkRoRE2rlKt3YTsDnBauoxuuJMFPKYQzQ'
    url = f"https://api.minimax.chat/v1/t2a_v2?GroupId={group_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    print(type(str(text)))
    print(type(str(Voice)))
    print(type(float(pitch)))
    print(type(float(speed)))
    data = json.dumps({
        # 如同时传入voice_id和timber_weights时，则会自动忽略voice_id，以timber_weights传递的参数为准
        "text": str(text),
        "model": 'speech-01-turbo',
        "stream": False,

        "timber_weights": [
            {
                "voice_id": str(Voice),
                "weight": 100
            },
            {
                "voice_id": 'audiobook_female_1',
                "weight": 1
            }
        ],        "voice_setting": {
            "voice_id": '',
            "speed": float(speed),
            "vol": volume,
            "pitch": int(pitch),
            "emotion": 'neutral'
        },
        "audio_setting": {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "wav"
        }
    })

    while True:
        #有时会限制访问，需要进行循环操作来处理
        response = requests.request("POST", url, stream=True, headers=headers, data=data)
        resp_json = json.loads(response.text)
        print(resp_json['base_resp']['status_msg'])
        print(text)
        if resp_json['base_resp']['status_msg'] == "invalid params, empty field":
            print(text)
            #判断如果不再输入文本则直接退出
            return "0"
        try:
            audio_value = bytes.fromhex(resp_json['data']['audio'])
            break
        except KeyError:
            continue

    with open("./utils/output_temp.wav", "wb") as f:
    #保存每一段的音频（这个可以作为第二个思路）
        f.write(audio_value)
        f.close()

    return "output_temp.wav"


