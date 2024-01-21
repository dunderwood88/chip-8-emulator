from cpu import Chip8
from renderer import Renderer
import numpy as np

if __name__ == "__main__":

    program =  np.fromfile("ibm-logo.ch8", dtype=np.uint8)

    renderer = Renderer()
    chip_8 = Chip8(renderer)
    chip_8.run(program)