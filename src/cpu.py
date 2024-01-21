from collections import deque

import numpy as np

from src.display.abstract_display import AbstractDisplay

class Chip8:
    """Class that implements a CHIP-8 emulator.
    """

    def __init__(self, display: AbstractDisplay) -> None:
        """Constructor to initialise the CHIP-8 CPU.

        Parameters
        ----------
        display : AbstractDisplay
            a display object to handle the display of graphics
        """
        # 4KB (4096 bytes) of memory
        self._memory = np.zeros(4096, dtype=np.uint8)

        # 1 16-bit index register to point at memory locations
        self._index = np.uint16(0)

        # 1 stack for 16-bit addresses to call/return subroutines
        self._stack = deque()

        # 16 8-bit general purpose variable registers
        self._variables = np.zeros(16, dtype=np.uint8)

        # 1 program counter to point at the current instruction in memory
        self._program_counter = 0x200  # point to first program address

        # 1 8-bit delay timer decremented at a rate of 60 Hz until it reaches 0
        self._delay_timer = np.uint8(0)

        # 1 8-bit sound timer which functions like the delay timer
        self._sound_timer = np.uint8(0)

        # establish the rendering object
        self._display = display


        # load the font data into memory
        font_data = np.array(
            [
                0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
                0x20, 0x60, 0x20, 0x20, 0x70, # 1
                0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
                0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
                0x90, 0x90, 0xF0, 0x10, 0x10, # 4
                0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
                0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
                0xF0, 0x10, 0x20, 0x40, 0x40, # 7
                0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
                0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
                0xF0, 0x90, 0xF0, 0x90, 0x90, # A
                0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
                0xF0, 0x80, 0x80, 0x80, 0xF0, # C
                0xE0, 0x90, 0x90, 0x90, 0xE0, # D
                0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
                0xF0, 0x80, 0xF0, 0x80, 0x80  # F
            ],
            dtype=np.uint8
        )
        self._load_into_memory(font_data)

    def _load_into_memory(
            self,
            payload: np.ndarray,
            memory_offset: int=0
        ) -> None:
        """Loads a byte payload into the CHIP-8 memory.

        Parameters
        ----------
        payload : np.ndarray
            the byte payload represented as an np.ndarray of type np.uint8
        memory_offset : int, optional
            specifies the memory location to start loading into, by default 0
        """
        for i, p in enumerate(payload):
            self._memory[memory_offset + i] = p

    def _fetch(self) -> None:
        """Reads the instruction that the program counter is currently pointing
        to in memory.
        Instructions are 2 bytes long, so 2 successive reads are performed,
        combining each 2-byte element into a single 16-bit instruction.
        The program counter is incremented by 2.
        """
        instruction = self._memory[self._program_counter].astype(np.uint16)
        instruction <<= 0x8
        self._program_counter += 1
        instruction |= self._memory[self._program_counter].astype(np.uint16)
        self._program_counter += 1

        return instruction.astype(np.uint16)

    def _decode_and_execute(self, instruction: np.uint16):
        """
        Decodes the 36 different CHIP-8 instructions according to section 3 of
        the CHIP-8 Technical Reference:
        http://devernay.free.fr/hacks/chip8/C8TECH10.HTM#3.0

        All instructions are 2 bytes long and are stored most-significant-byte
        first.

        The following variables are used:

        nnn or addr = a 12-bit value, the lowest 12 bits of the instruction
        n or nibble = a 4-bit value, the lowest 4 bits of the instruction
        x = a 4-bit value, the lower 4 bits of the high byte of the instruction
        y = a 4-bit value, the upper 4 bits of the low byte of the instruction
        kk or byte = an 8-bit value, the lowest 8 bits of the instruction

        After instructions are decoded they are executed accordingly.

        Parameters
        ----------
        instruction : np.uint16
            The 2-byte instruction to be decoded and subsequently executed
        """
        # first nibble specifies instruction type
        first_nibble = instruction & 0xF000

        # x and y used in many instructions so calculate here
        x = ((instruction & 0x0F00) >> 8).astype(np.uint8)
        y = ((instruction & 0x00F0) >> 4).astype(np.uint8)

        if first_nibble == 0x0000:
            if instruction == 0x00E0:
                self._display.clear()
            # TODO: more
        elif first_nibble == 0x1000:
            self._program_counter = instruction & 0x0FFF
        # TODO: 2 through 5
        elif first_nibble == 0x6000:
            self._variables[x] = instruction & 0x00FF
        elif first_nibble == 0x7000:
            self._variables[x] += instruction & 0x00FF
        # TODO: 8 through 9
        elif first_nibble == 0xA000:
            self._index = instruction & 0x0FFF
        # TODO: B through C
        elif first_nibble == 0xD000:
            num_bytes = (instruction & 0x000F).astype(np.uint8)
            self._display_draw(x, y, num_bytes)
        # TODO: E through F
        else:
            raise RuntimeError(f"Unknown instruction: {instruction}")
        
    def _display_draw(self, x: np.uint8, y: np.uint8, num_bytes: np.uint8):
        """Display n-byte sprite starting at memory location I at (Vx, Vy),
        set VF = collision.

        The interpreter reads n bytes from memory, starting at the address
        stored in I. These bytes are then displayed as sprites on screen at
        coordinates (Vx, Vy).
        Sprites are XORed onto the existing screen. If this causes any pixels
        to be erased, VF is set to 1, otherwise it is set to 0. If the sprite
        is positioned so part of it is outside the coordinates of the display,
        it wraps around to the opposite side of the screen.

        Parameters
        ----------
        x : np.uint8
            4-bit variable used to locate x-position stored in
            self._variables[x]
        y : np.uint8
            4-bit variable used to locate y-position stored in
            self._variables[y]
        num_bytes : np.uint8
            the number of bytes to read from memory, starting at the address
            stored at memory location I (self._index)
        """
        for r in range(num_bytes):

            # grab 1 byte (8-bit) sprite from memory location
            sprite =  self._memory[self._index + r]

            for c in range(0x0008):  # iterate over each bit in sprite
                if sprite & 0x0080:  # if current bit not zero
                    pixel_erased = self._display.set_pixel(
                        (self._variables[x] + c).astype(np.uint16),
                        (self._variables[y] + r).astype(np.uint16)
                    )
                    self._variables[0x000F] = pixel_erased  # VF = collision
                sprite <<= 1

        self._display.render()

    def run(self, program: np.ndarray):
        """Loads in a chip-8 program and runs it.

        Parameters
        ----------
        program : np.ndarray
            the CHIP-8 program represented as an np.ndarray of type np.uint8
        """
        # load into the standard memory location (0x200)
        self._load_into_memory(program, memory_offset=0x200)

        while True:  # initiate fetch/decode/execute cycle
            instruction = self._fetch()
            self._decode_and_execute(instruction)
