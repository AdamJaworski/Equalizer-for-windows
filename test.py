import time
from numpy.fft import fft, rfft, irfft
import numpy as np
import cmath
import sounddevice as sd

devices = sd.query_devices()
for device in devices:
    if device['name'] == 'CABLE Input (VB-Audio Virtual Cable)':
        output_vb = device
    elif device['name'] == 'CABLE Output (VB-Audio Virtual Cable)':
        forward_vb = device
    elif device['name'] == 'Headphones (Arctis 5 Game)':
        output_headphones = device


def loop_back(indata, outdata, frames, time, status) -> None:
    indata[:] = outdata


def play(indata, outdata, frames, time_, status):
    fft_ = rfft(indata)
    sig_phase = np.angle(fft_, deg=True)
    new_fft = fft_ * cmath.rect(1., np.pi/4)
    new_phase = np.angle(new_fft, deg=True)
    new_real = irfft(new_fft)
    print(f"1:{sig_phase}  , \n 2:{new_phase}")
    outdata[:] = new_real


sampling_freq = output_headphones['default_samplerate']
loop_back_stream = sd.Stream(device=(forward_vb['index'], output_vb['index']),
                             callback=loop_back, blocksize=32, latency=0.01,
                             clip_off=True)  # , never_drop_input=True, clip_off=False

play_stream = sd.Stream(callback=play, clip_off=True, blocksize=24000, latency=0.05)

loop_back_stream.start()
play_stream.start()
while True:
    time.sleep(0.01)