import customtkinter
import numpy as np
from numpy.fft import rfft, irfft


def start_gui(main_app, audio_stream_handler):
    phase_enable = False

    # def phase_change(data):
    #     data += 1
    #     fft_ = rfft(data)
    #     fft_ = np.abs(fft_) * np.exp(1j * (np.angle(fft_) + np.deg2rad(phase_slider.get())))
    #     data = irfft(fft_) - 1
    #     return data

    def phase_change(data):
        fft_ = rfft(data)
        magnitude = np.abs(fft_)
        phase = np.angle(fft_)
        phase_shift_rad = np.deg2rad(phase_slider.get())
        new_phase = phase + phase_shift_rad
        new_fft = magnitude * np.exp(1j * new_phase)
        new_data = irfft(new_fft)
        original_power = np.mean(data ** 2)
        new_power = np.mean(new_data ** 2)
        new_data *= np.sqrt(original_power / new_power)

        return new_data

    def update_label(*args):
        silder_vaule_label.configure(text=f'{(phase_slider.get()):.1f} deg')

    def change_state_phase(*args):
        nonlocal phase_enable
        phase_enable = not phase_enable

        if phase_enable:
            phase_angle_button.configure(fg_color='#126929')
            audio_stream_handler.data_loop.append(phase_change)

        else:
            phase_angle_button.configure(fg_color='#1F6AA5')
            audio_stream_handler.data_loop.remove(phase_change)

    phase_frame = customtkinter.CTkFrame(main_app, height=300, width=100)
    phase_frame.pack(anchor='s',  side='left')

    customtkinter.CTkLabel(phase_frame, text='Phase', fg_color='#171717').pack(anchor='n', fill='x')
    phase_angle_button = customtkinter.CTkButton(phase_frame, text='', width=30, height=30,
                                                 command=change_state_phase)
    phase_angle_button.pack(anchor='center', side='top', padx=20, pady=10)
    phase_slider = customtkinter.CTkSlider(phase_frame, from_=0, to=180, number_of_steps=1800, orientation='vertical', command=update_label)
    phase_slider.set(0)
    phase_slider.pack(anchor='center', padx=20, pady=5)
    silder_vaule_label = customtkinter.CTkLabel(phase_frame, text='0 deg')
    silder_vaule_label.pack(anchor='center', pady=(0, 5), side='bottom', fill='x')
