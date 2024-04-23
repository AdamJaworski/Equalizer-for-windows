import queue
import sounddevice as sd
import numpy as np
import time

output_vb         = None
output_headphones = None
forward_vb        = None
data_loop         = []
open_streams      = []
sound_dtype       = 'int16'
sampling_freq     = None
downsample        = 10
q                 = queue.Queue(maxsize=20)


def measure_time(func):
    def wrapper(*args):
        start = time.time()
        output = func(*args)
        print(f"{(time.time() - start):.4f}s")
        return output
    return wrapper


def loop_back(indata, outdata, frames, time, status) -> None:
    indata[:] = outdata


def play(indata, outdata, frames, time_, status):
    indata = process_data(indata).astype(sound_dtype)
    if not q.full():
        if sound_dtype.__contains__('int'):
            scaled_data = indata.astype(np.float32) / np.iinfo(indata.dtype).max
            q.put(scaled_data[::downsample, :])
        else:
            q.put(indata[::downsample, :])
    outdata[:] = indata


def process_data(data):
    for func in data_loop:
        data = func(data)
    return data


def __on_exit():
    for stream in open_streams:
        stream.stop()


def on_stream_operation(func):
    if any([output_vb, output_headphones, forward_vb]) is None:
        return

    def wrapper():
        func()
    return wrapper


def initialize():
    devices = sd.query_devices()
    global output_vb, forward_vb, output_headphones, open_streams, sampling_freq
    for device in devices:
        if device['name'] == 'CABLE Input (VB-Audio Virtual Cable)':
            output_vb = device
        if device['name'] == 'CABLE Output (VB-Audio Virtual Cable)':
            forward_vb = device
        if device['name'] == 'Headphones (Arctis 5 Game)':
            output_headphones = device

    loop_back_stream = sd.Stream(device=(forward_vb['index'], output_vb['index']), callback=loop_back,
                                 blocksize=16, latency='low', dtype=sound_dtype)
    play_stream      = sd.Stream(device=(forward_vb['index'], output_headphones['index']), callback=play,
                                 blocksize=1024, latency=0.1, dtype=sound_dtype)
    sampling_freq = output_headphones['default_samplerate']
    open_streams = [loop_back_stream, play_stream]
    loop_back_stream.start()
    play_stream.start()




