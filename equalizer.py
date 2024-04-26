from numba import jit, prange
import customtkinter
from scipy.signal import butter, sosfilt_zi, sosfilt
import numpy as np
import json
from tkinter import filedialog


def start_gui(main_app, audio_stream_handler):
    equalizer_bool = False

    freqs     = [16, 31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
    low_band  = [11, 22, 44, 88, 177, 355, 710, 1420, 2840, 5680, 11360]
    high_band = [22, 44, 88, 177, 355, 710, 1420, 2840, 5680, 11360, 20000]
    sliders, freq_labels, gain_labels = [], [], []
    sos_cache = [butter(8, np.array([low_band[i], high_band[i]]) / (audio_stream_handler.sampling_freq / 2), btype='band', output='sos') for i in range(len(freqs))]
    zi_left  = [sosfilt_zi(sos) * 0 for sos in sos_cache]
    zi_right = [sosfilt_zi(sos) * 0 for sos in sos_cache]

    def bandpass_filter(data, index):
        nonlocal zi_right, zi_left
        left, zi_left[index]   = sosfilt(sos_cache[index], data[:, 0], zi=zi_left[index])
        right, zi_right[index] = sosfilt(sos_cache[index], data[:, 1], zi=zi_right[index])
        return np.column_stack((left, right))

    def dB_to_linear(gain_dB):
        return 10 ** (gain_dB / 20)

    @jit(nopython=True)
    def apply_gain_and_sum(filters, gains):
        result = np.zeros_like(filters[0])
        for i in prange(len(filters)):
            result += filters[i] * gains[i]
        return result

    def equalizer(data):
        filters = [bandpass_filter(data, index) for index in range(len(sos_cache))]
        gains = [dB_to_linear(sliders[index].get() + 1) for index in range(len(sliders))]
        data = apply_gain_and_sum(filters, gains)
        return data

    def change_state(*args):
        nonlocal equalizer_bool
        equalizer_bool = not equalizer_bool
        button.configure(fg_color='#126929' if equalizer_bool else '#1F6AA5')
        (audio_stream_handler.data_loop.append if equalizer_bool else audio_stream_handler.data_loop.remove)(equalizer)

    def load():
        try:
            open_ = open(filedialog.askopenfilename())
        except Exception:
            return

        settings = json.load(open_)
        for index, value in enumerate(settings["equalizer"]):
            sliders[index].set(value)
        update_label()

    def save():
        values = [slider.get() for slider in sliders]
        preset = {"equalizer": values}
        file = filedialog.asksaveasfile(defaultextension=".json", filetypes=(("JSON file", "*.json"), ("All Files", "*.*")))
        if file is None:
            return
        json.dump(preset, file)

    def update_label(*args):
        for index, label in enumerate(gain_labels):
            label.configure(text=f'{(sliders[index].get()):.1f} dB')

    equalizer_frame = customtkinter.CTkFrame(main_app, height=300, width=400)
    equalizer_frame.pack(anchor='s',  side='left', fill='y', padx=5)

    customtkinter.CTkLabel(equalizer_frame, text='Equalizer', fg_color='#171717').pack(anchor='n', fill='x')

    sliders      = []
    freq_labels  = []
    gain_labels  = []

    for i in range(len(freqs)):
        value_frame = customtkinter.CTkFrame(equalizer_frame)
        if i == 0:
            value_frame.pack(side='left', fill='y')
        else:
            value_frame.pack(side='left', fill='y', padx=(4, 0))
        text = f'{freqs[i]} Hz' if freqs[i] < 1000 else f'{(freqs[i] / 1000):.0f}k Hz'
        freq_label = customtkinter.CTkLabel(value_frame, text=text)
        freq_labels.append(freq_label)
        freq_label.pack(side='top')

        slider = customtkinter.CTkSlider(value_frame, from_=-10, to=10, number_of_steps=200, orientation='vertical', command=update_label)
        sliders.append(slider)
        slider.pack(anchor='center', padx=25, pady=(20, 0))
        slider.set(0)

        gain_label = customtkinter.CTkLabel(value_frame, text='0.0 dB')
        gain_labels.append(gain_label)
        gain_label.pack(side='bottom')

    example_config = [3.7, -0.5, -2.9, 3.2, -4.4, 0.6, 0.8, 1.8, -1, 2.3, 0]
    example_config = [3.7, -0.5, -2.9, 3.2, -4.4, 0.1, 0.5, -1.1, -1.7, 4.4, 4.6]
    button_frame = customtkinter.CTkFrame(equalizer_frame)
    button_frame.pack(side='left', fill='y', padx=(4, 0))

    button = customtkinter.CTkButton(button_frame, text='', width=30, height=30, command=change_state)
    button.pack(anchor='center', side='top', padx=20, pady=10)
    customtkinter.CTkButton(button_frame, text='S', width=30, height=30, command=save).pack(anchor='center', padx=20, pady=(70, 10))
    customtkinter.CTkButton(button_frame, text='L', width=30, height=30, command=load).pack(anchor='center', side='bottom', padx=20, pady=10)

    apply_gain_and_sum([0], [0])