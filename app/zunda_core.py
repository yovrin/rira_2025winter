# app/voicevox_util.py

import json
import requests
import io
import wave

def generate_wav_bytes(text, speaker=1, speed = 1.0):
    host = 'localhost'
    port = 50021

    params = (
        ('text', text),
        ('speaker', speaker),
    )

    # 音声合成用クエリ
    response1 = requests.post(
        f'http://{host}:{port}/audio_query',
        params=params
    )
    response1.raise_for_status()

    headers = {'Content-Type': 'application/json'}

    # ② audio_query の JSON を取り出して speedScale を変更
    query = response1.json()
    query["speedScale"] = speed  # ← ★ここで速度設定（通常 0.5～2.0）

    # 音声合成
    response2 = requests.post(
        f'http://{host}:{port}/synthesis',
        headers=headers,
        params=params,
        data=json.dumps(query)
    )
    response2.raise_for_status()

    # そのまま WAV のバイナリを返す
    return response2.content


import simpleaudio as sa
import io
import wave

def play_wav_bytes(wav_bytes):
    """WAVバイトをPCのスピーカーで再生"""
    with io.BytesIO(wav_bytes) as audio_io:
        with wave.open(audio_io, 'rb') as wave_read:
            audio_data = wave_read.readframes(wave_read.getnframes())
            wave_obj = sa.WaveObject(
                audio_data,
                wave_read.getnchannels(),
                wave_read.getsampwidth(),
                wave_read.getframerate()
            )

    play_obj = wave_obj.play()
    play_obj.wait_done()


if __name__ == '__main__':
    text = 'かしこい、なのだ'

    wav_bytes = generate_wav_bytes(text)  # WAV を生成
    play_wav_bytes(wav_bytes)  # ← WAV を再生する

