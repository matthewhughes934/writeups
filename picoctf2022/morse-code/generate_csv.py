#!/usr/bin/env python3

import csv
import wave

FILENAME = "morse_chal.wav"
OUTFILE = "morse_chal.csv"


def main() -> int:
    w = wave.Wave_read(FILENAME)

    # Just read the whole thing into memory
    frames = w.readframes(w.getnframes())
    sampwidth = w.getsampwidth()

    with open(OUTFILE, "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(
            (i, int.from_bytes(frame, byteorder="little"))
            for i, frame in enumerate(
                frames[j : j + sampwidth] for j in range(0, len(frames), sampwidth)
            )
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
