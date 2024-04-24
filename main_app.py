import sys
import customtkinter
import volume
import output_vol_graph
import equalizer
from audio_stream_handler import AudioStreamHandler


def __on_exit():
    app.destroy()
    sys.exit(1)


def __on_start():
    audio_stream_handler = AudioStreamHandler()
    output_vol_graph.start_gui(app, audio_stream_handler)
    volume.start_gui(app, audio_stream_handler)
    equalizer.start_gui(app, audio_stream_handler)


app = customtkinter.CTk()
app.title("*")
app.protocol("WM_DELETE_WINDOW", __on_exit)
app.resizable(False, False)

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")
customtkinter.set_appearance_mode("dark")

screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
center_x = int(screen_width / 2 - 918 / 2)
center_y = int(screen_height / 2 - 520 / 2)

app.geometry(f"918x520+{center_x}+{center_y}")
__on_start()
app.mainloop()