import os

import numpy as np

from src.display.abstract_display import AbstractDisplay

# allows visualising entire np.ndarray
np.set_printoptions(threshold=np.inf, linewidth=1000)

class CliDisplay(AbstractDisplay):
    """Class that implements a renderer to display the output of a CHIP-8
    emulator using np.ndarray outputs to the console.

    The display for CHIP-8 is 64 x 32 pixels, and each pixel is represented by
    0 or 1.
    """

    def __init__(self) -> None:
        """Constructor to initialise an np.ndarray-based renderer to output
        a primitive display to the console.
        """
        super().__init__()

        # initialise the display as a 32 x 64 np.ndarray of 0s
        self._display = np.zeros((self._rows, self._columns), dtype=np.uint8)

    def clear(self) -> None:
        """Clears the display by re-initialising the 32 x 64 np.ndarray to be
         all 0s.
        """
        self._display = np.zeros((self._rows, self._columns), dtype=np.uint8)

    def render(self) -> None:
        """Renders the current state of the display to the console.
        """
        os.system("clear")
        print(self._display)

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