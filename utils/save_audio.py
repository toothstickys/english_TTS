import os 
def save_audio(audio_value, number, args):
    dir_name = './temp_{}_{}'.format(args.user_id, args.times)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    # audio_value = np.frombuffer(audio_value, dtype=np.int16)
    # sf.write("./temp/output_{}.wav".format(number), audio_value, 32000)
    with open("{}/output_{}.wav".format(dir_name, number), "wb") as f:
    #保存每一段的音频（这个可以作为第二个思路）
        f.write(audio_value)
        f.close()
    return "{}/output_{}.wav".format(dir_name, number)