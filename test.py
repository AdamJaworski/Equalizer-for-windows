import time

import sounddevice as sd

devices = sd.query_devices()
for device in devices:
    if device['name'] == 'Headphones (Arctis 5 Game)':
        output_headphones = device


def audio_callback(outdata, frames, time, status):
    outdata[:] = outdata  * (10 ** (-50 / 20))


stream = sd.OutputStream(
    device=output_headphones['index'], channels=2,
    samplerate=48000, callback=audio_callback, blocksize=256)

with stream:
    while True:
        time.sleep(0.01)