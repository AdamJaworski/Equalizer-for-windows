import queue
import sounddevice as sd
from scipy.signal import butter, sosfiltfilt
import time
import numpy as np


def measure_time(func):
    def wrapper(*args):
        start = time.time()
        output = func(*args)
        print(f"{(time.time() - start):.4f}s / {(2048/48000):.4f}s")
        return output

    return wrapper


class AudioStreamHandler:
    def __init__(self):
        self.output_vb = None
        self.output_headphones = None
        self.forward_vb = None
        self.data_loop = []
        self.open_streams = []
        self.sound_dtype = sd.default.dtype = 'float32'
        self.sampling_freq = None
        self.downsample = 10
        self.queue = queue.Queue(maxsize=20)
        self.initialize()

    def loop_back(self, indata, outdata, frames, time, status) -> None:
        indata[:] = outdata

    def play(self, indata, outdata, frames, time_, status):
        if status:
            print(status)
        processed_data = self.process_data(indata)  #.astype(self.sound_dtype)
        if not self.queue.full():
            if 'int' in self.sound_dtype:
                scaled_data = indata.astype(np.float32) / np.iinfo(indata.dtype).max
                self.queue.put(scaled_data[::self.downsample, :])
            else:
                self.queue.put(indata[::self.downsample, :])
        outdata[:] = processed_data

    def process_data(self, data):
        for func in self.data_loop:
            data = func(data)
        return data

    def on_exit(self):
        for stream in self.open_streams:
            stream.stop()

    def initialize(self):
        devices = sd.query_devices()
        for device in devices:
            if device['name'] == 'CABLE Input (VB-Audio Virtual Cable)':
                self.output_vb = device
            elif device['name'] == 'CABLE Output (VB-Audio Virtual Cable)':
                self.forward_vb = device
            elif device['name'] == 'Headphones (Arctis 5 Game)':
                self.output_headphones = device
            # elif device['name'] == 'Głośniki (JBL Pebbles)':
            #     self.output_headphones = device

        self.sampling_freq = self.output_headphones['default_samplerate']
        loop_back_stream = sd.Stream(device=(self.forward_vb['index'], self.output_vb['index']),
                                     callback=self.loop_back, blocksize=32, latency=0.02, clip_off=True)        #, never_drop_input=True, clip_off=False

        play_stream = sd.Stream(device=(self.forward_vb['index'], self.output_headphones['index']),
                                callback=self.play, clip_off=True, blocksize=2048, latency=0.02)

        self.open_streams = [loop_back_stream, play_stream]
        loop_back_stream.start()
        play_stream.start()

    def __del__(self):
        self.on_exit()



