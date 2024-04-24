import customtkinter


def start_gui(main_app, audio_stream_handler):
    use_volume_filter = False

    def volume_filter(data):
        return data * (10 ** (volume_slider.get() / 20))

    def update_label(*args):
        silder_vaule_label.configure(text=f'{(volume_slider.get()):.1f} dB')

    def change_state_volume(*args):
        nonlocal use_volume_filter
        use_volume_filter = not use_volume_filter

        if use_volume_filter:
            volume_filter_button.configure(fg_color='#126929')
            audio_stream_handler.data_loop.append(volume_filter)

        else:
            volume_filter_button.configure(fg_color='#1F6AA5')
            audio_stream_handler.data_loop.remove(volume_filter)

    volume_frame = customtkinter.CTkFrame(main_app, height=300, width=100)
    volume_frame.pack(anchor='s',  side='left')

    customtkinter.CTkLabel(volume_frame, text='Volume', fg_color='#171717').pack(anchor='n', fill='x')
    volume_filter_button = customtkinter.CTkButton(volume_frame, text='', width=30, height=30,
                                                   command=change_state_volume)
    volume_filter_button.pack(anchor='center', side='top', padx=20, pady=10)
    volume_slider = customtkinter.CTkSlider(volume_frame, from_=-60, to=15, number_of_steps=750, orientation='vertical', command=update_label)
    volume_slider.set(0)
    volume_slider.pack(anchor='center', padx=20, pady=5)
    silder_vaule_label = customtkinter.CTkLabel(volume_frame, text='0 dB')
    silder_vaule_label.pack(anchor='center', pady=(0, 5), side='bottom', fill='x')
