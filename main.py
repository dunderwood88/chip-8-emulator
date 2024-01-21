import numpy as np

from src.cpu import Chip8
from src.display.cli_display import CliDisplay
from src.display.tkinter_display import TkinterDisplay

if __name__ == "__main__":

    program =  np.fromfile("ibm-logo.ch8", dtype=np.uint8)

    display = CliDisplay()
    display = TkinterDisplay()
    chip_8 = Chip8(display)
    chip_8.run(program)