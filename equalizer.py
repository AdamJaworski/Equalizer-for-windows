from numba import jit, prange
import customtkinter
import global_variables
from scipy.signal import butter, sosfilt
import numpy as np


def start_gui(main_app):
    equalizer_bool = False

    freqs = [63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
    sliders, freq_labels, gain_labels = [], [], []
    sos_cache = [butter(4, [11 * (2 ** (i + 2)), 11 * (2 ** (i + 3))], fs=global_variables.sampling_freq, btype='band', output='sos') for i in range(len(freqs))]

    def bandpass_filter(data, sos):
        return np.array([sosfilt(sos, data[:, channel]) for channel in range(data.shape[1])]).T

    def dB_to_linear(gain_dB):
        return 10 ** (gain_dB / 20)

    @jit(nopython=True)
    def apply_gain_and_sum(filters, gains):
        result = np.zeros_like(filters[0])
        for i in prange(len(filters)):
            result += filters[i] * gains[i]
        return result

    def equalizer(data):
        filters = [bandpass_filter(data, sos) for sos in sos_cache]
        gains = [dB_to_linear(sliders[index].get() + 1) for index in range(len(sliders))]
        return apply_gain_and_sum(filters, gains)

    @global_variables.on_stream_operation
    def change_state(*args):
        nonlocal equalizer_bool
        equalizer_bool = not equalizer_bool
        button.configure(fg_color='#126929' if equalizer_bool else '#1F6AA5')
        (global_variables.data_loop.append if equalizer_bool else global_variables.data_loop.remove)(equalizer)

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

    button_frame = customtkinter.CTkFrame(equalizer_frame)
    button_frame.pack(side='left', fill='y', padx=(4, 0))
    button = customtkinter.CTkButton(button_frame, text='', width=30, height=30, command=change_state)
    button.pack(anchor='center', side='top', padx=20, pady=10)