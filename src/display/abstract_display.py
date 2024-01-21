from abc import ABC, abstractmethod

import numpy as np


class AbstractDisplay(ABC):
    """Class that implements a renderer to display the output of a CHIP-8
    emulator.

    The display for CHIP-8 is 64 x 32 pixels, and each pixel is represented by
    0 or 1.
    """

    def __init__(self) -> None:
        """Constructor.
        """
        self._columns = 64
        self._rows = 32

    @abstractmethod
    def clear(self) -> None:
        """Clears the display by re-initialising the 32 x 64 np.ndarray to be
         all 0s.
        """
        pass

    @abstractmethod
    def render(self) -> None:
        """Renders the current state of the display to the console.
        """
        pass

    @abstractmethod
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
        pass