import sys
import customtkinter
import global_variables
import volume
import output_vol_graph
import equalizer

def __on_exit():
    global_variables.__on_exit()
    app.destroy()
    sys.exit(1)


def __on_start():
    global_variables.initialize()
    output_vol_graph.start_gui(app)
    volume.start_gui(app)
    equalizer.start_gui(app)


app = customtkinter.CTk()
app.title("*")
app.protocol("WM_DELETE_WINDOW", __on_exit)

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")
customtkinter.set_appearance_mode("dark")

screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
center_x = int(screen_width / 2 - 780 / 2)
center_y = int(screen_height / 2 - 520 / 2)

app.geometry(f"780x520+{center_x}+{center_y}")
__on_start()
app.mainloop()