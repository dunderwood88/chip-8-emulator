from multiprocessing import Process, Queue
from queue import Empty
import tkinter as tk

import numpy as np

from src.display.abstract_display import AbstractDisplay


class TkinterDisplay(AbstractDisplay):
    """Class that implements a renderer to display the output of a CHIP-8
    emulator using the Tkinter module.

    The display for CHIP-8 is 64 x 32 pixels, and each pixel is represented by
    0 or 1.
    """

    def __init__(self, pixel_size: int=20) -> None:
        """Constructor to initialise a Tkinter-based GUI renderer that outputs
        the state of the np.ndarray display object.
        """
        super().__init__()

        self._pixel_size = pixel_size
        self._display = np.zeros((self._rows, self._columns), dtype=np.uint8)
        self._display_state_queue: Queue[np.ndarray] = Queue()

        # spin out separate process to define/update the tkinter canvas
        self.tkinter_process = Process(target=self._tkinter_root)
        self.tkinter_process.start()

    def _tkinter_root(self):
        """Function defining the Tkinter process that runs asynchronously.
        Defines the display canvas and continuously checks for updates to the
        display state by listening on updates from a queue.
        """

        # define the window canvas
        root = tk.Tk()
        canvas = tk.Canvas(
            root, bg="black",
            width=self._columns * self._pixel_size,
            height=self._rows * self._pixel_size
        )
        canvas.pack()

        # set up loop to continuously check the queue for state updates
        def check_queue() -> None:
            """Function to get display updates from the asynchronous queue and
            render them on the canvas.
            """

            try:
                grid = self._display_state_queue.get_nowait()
                for i in range(self._rows):
                    for j in range(self._columns):
                        x0, y0 = j * self._pixel_size, i * self._pixel_size
                        x1, y1 = x0 + self._pixel_size, y0 + self._pixel_size
                        color = "white" if grid[i, j] == 1 else "black"
                        canvas.create_rectangle(
                            x0, y0, x1, y1, outline="grey8", fill=color
                        )
            except Empty:
                pass  # no updates

            root.after(1, check_queue)  # set up a recurring loop

        root.after(1, check_queue)
        root.mainloop()  # start the main Tkinter loop
        

    def clear(self) -> None:
        """Clears the display by re-initialising the 32 x 64 np.ndarray to be
         all 0s.
        """
        self._display = np.zeros((self._rows, self._columns), dtype=np.uint8)

    def render(self) -> None:
        """Renders the current state of the display to the console. The state
        of the np.ndarray display object is asynchronously broadcast to a
        separate GUI process that handles the rendering.
        """
        self._display_state_queue.put(self._display)

    def set_pixel(self, x: np.uint16, y: np.uint16) -> bool:
        """Toggles the pixel value at the location x, y on the display grid.
        Returns true if the pixel ahs been erased (set from 1 to 0).

        Parameters
        ----------
        x : np.uint16
            x-value of the pixel to be toggled
        y : np.uint16
            y-value of the pixel to be toggled

        Returns
        -------
        bool
            returns true if the pixel has been erased, else false
        """
        # toggle pixel value (0 to 1 or 1 to 0)
        self._display[y][x] ^= 1

        return not self._display[y][x]  # returns true if pixel erased