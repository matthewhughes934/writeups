#!/usr/bin/env python3

import wave

FILENAME = "morse_chal.wav"
# from https://upload.wikimedia.org/wikipedia/commons/b/b5/International_Morse_Code.svg
MORSE_CODE_MAP= {
    "0": "E",
    "00": "I",
    "000": "S",
    "0000": "H",
    "00000": "5",
    "00001": "4",
    "0001": "V",
    "00011": "3",
    "001": "U",
    "0010": "F",
    "00111": "2",
    "01": "A",
    "010": "R",
    "011": "W",
    "0110": "P",
    "0111": "J",
    "01111": "1",
    "1": "T",
    "10": "N",
    "100": "D",
    "1000": "B",
    "10000": "6",
    "1001": "X",
    "101": "K",
    "1010": "C",
    "1011": "Y",
    "11": "M",
    "110": "G",
    "1100": "Z",
    "11000": "7",
    "1101": "Q",
    "111": "O",
    "11100": "8",
    "11110": "9",
    "11111": "0",
    "L":" 0100",
}


def main() -> int:
    w = wave.Wave_read(FILENAME)

    # Just read the whole thing into memory
    frames = w.readframes(w.getnframes())

    # Via manual inspection of the data
    block_size = 2000
    char_sep_length = 17
    word_sep_length = 35
    # there were only two lengths 13 and 4
    long_length = 13

    last_block_start = 0
    last_block_end = 0
    last_blank_start = 0

    zero_count = 0
    in_blank = False

    current_char = ""

    for i, frame in enumerate(frames):
        if frame == 0:
            if zero_count == block_size:
                in_blank = True
                last_block_end = i - zero_count
                last_blank_start = last_block_end
            zero_count += 1
        else:
            # End of a blank
            if in_blank:
                width = (last_block_end - last_block_start) // block_size
                blank_width = (i - last_blank_start) // block_size

                current_char += "1" if width == long_length else "0"
                if blank_width in (char_sep_length, word_sep_length):
                    end = "" if blank_width == char_sep_length else "_"
                    print(MORSE_CODE_MAP[current_char], end=end)
                    current_char = ""
                last_block_start = i
                in_blank = False
            zero_count = 0

    # Trailing character
    width = (last_block_end - last_block_start) // block_size - 1
    print(1 if width == long_length else 0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
