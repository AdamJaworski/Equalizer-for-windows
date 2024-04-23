import customtkinter as ctk
import numpy as np
import queue
from matplotlib.animation import FuncAnimation
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import global_variables


plotdata = None


def start_gui(main_app):
    global plotdata
    window = 300  # time in ms
    downsample = 10
    channels = [*range(global_variables.forward_vb['max_input_channels'])]
    sample_rate = global_variables.forward_vb['default_samplerate']
    length = int(window * sample_rate / (1000 * downsample))
    mapping = [c - 1 for c in channels]
    plotdata = np.zeros((length, len(channels)))

    def update_plot(frame):
        global plotdata
        while not global_variables.q.empty():
            try:
                data = global_variables.q.get_nowait()
            except queue.Empty:
                break
            shift = len(data)
            plotdata = np.roll(plotdata, -shift, axis=0)
            plotdata[-shift:, :] = data
        for column, line in enumerate(lines):
            # Make sure to scale the data to the plot's y-axis range if necessary
            line.set_ydata(plotdata[:, column])
        return lines

    fig = Figure(figsize=(6, 2), dpi=100)  # Adjust the size as needed
    ax = fig.add_subplot()
    lines = ax.plot(plotdata)
    ax.legend(['channel {}'.format(c) for c in channels], loc='lower left', ncol=len(channels))
    ax.axis((0, len(plotdata), -1, 1))
    ax.set_yticks([0])
    ax.yaxis.grid(True)
    ax.get_legend().remove()
    ax.tick_params(bottom=False, top=False, labelbottom=False,
                   right=False, left=False, labelleft=False)
    fig.tight_layout(pad=0)
    ax.set_facecolor('#343434')  # Set plot area color


    # Embedding plot in customtkinter frame
    frame = ctk.CTkFrame(main_app, width=400, height=100)  # Adjust the size as needed
    frame.pack(anchor='center', side='top', fill='x')  # Add some padding to place it above the volume slider
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill='both', expand=True)

    main_app.ani = FuncAnimation(fig, update_plot, interval=window/10, blit=False, cache_frame_data=False)