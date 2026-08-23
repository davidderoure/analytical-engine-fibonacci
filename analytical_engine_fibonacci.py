#!/usr/bin/env python3
"""
A minimal simulator of Babbage's Analytical Engine, used to compute
Fibonacci numbers modulo n (the "Pisano period"), sonified as MIDI.

Demo for a talk on Ada Lovelace, the Analytical Engine, and algorithmic
composition.

The engine model follows the spirit of Lovelace's 1843 "Note G": a Store
of numbered variable columns, a Mill that performs one arithmetic
operation at a time, and a sequence of Operation Cards that are logged
as they run -- just as Note G tabulates the operations needed to
compute the Bernoulli numbers. The engine only knows ADD and SUBTRACT;
modulo is built from repeated subtraction, in the same spirit that
Note G builds a whole computation out of the four base operations.

Usage:
    python3 analytical_engine_fibonacci.py --n 12
    python3 analytical_engine_fibonacci.py --n 12 --scale major --out fib12.mid
"""

import argparse
import mido


class AnalyticalEngine:
    """A tiny simulation of the Store + Mill, logging each operation."""

    def __init__(self):
        self.store = {}   # variable columns, e.g. "V1" -> value
        self.trace = []   # log of operations, Note-G style
        self.op_count = 0

    def set_variable(self, name, value):
        self.store[name] = value

    def _operate(self, symbol, op, a_name, b_name, result_name):
        self.op_count += 1
        a, b = self.store[a_name], self.store[b_name]
        result = op(a, b)
        self.store[result_name] = result
        self.trace.append((self.op_count, symbol, a_name, b_name, result_name, result))
        return result

    def add(self, a, b, result):
        return self._operate("+", lambda x, y: x + y, a, b, result)

    def subtract(self, a, b, result):
        return self._operate("-", lambda x, y: x - y, a, b, result)

    def print_trace(self, limit=20):
        rows = self.trace if limit is None else self.trace[:limit]
        print(f"{'No.':>4}  {'Op':^3}  {'Variables acted on':<12} {'Result in':<10} Value")
        print("-" * 50)
        for no, sym, a, b, result, value in rows:
            print(f"{no:>4}   {sym:^3}  {a + ',' + b:<12} {result:<10} {value}")
        if limit is not None and len(self.trace) > limit:
            print(f"... ({len(self.trace) - limit} further operations omitted)")


def fibonacci_mod_n(n, max_terms=100000):
    """
    Run the Fibonacci-mod-n algorithm on the Analytical Engine.

    Returns (engine, sequence, period) where `period` is the Pisano
    period pi(n): the sequence of Fibonacci numbers mod n is periodic,
    and the pair (F(k) mod n, F(k+1) mod n) returns to its starting
    value (0, 1 mod n) exactly every pi(n) terms.
    """
    engine = AnalyticalEngine()
    v2_init = 1 % n
    engine.set_variable("V1", 0)        # F(k-1) mod n
    engine.set_variable("V2", v2_init)  # F(k)   mod n
    engine.set_variable("Vn", n)        # the modulus, held constant

    sequence = [0, v2_init]
    target = (0, v2_init)
    period = None

    for k in range(2, max_terms):
        engine.add("V1", "V2", "V3")
        while engine.store["V3"] >= n:            # modulo by repeated subtraction
            engine.subtract("V3", "Vn", "V3")
        value = engine.store["V3"]
        sequence.append(value)

        engine.set_variable("V1", engine.store["V2"])
        engine.set_variable("V2", value)

        if (engine.store["V1"], engine.store["V2"]) == target:
            period = k - 1
            break

    return engine, sequence, period


SCALES = {
    "chromatic": list(range(12)),
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "pentatonic": [0, 3, 5, 7, 10],  # minor pentatonic
}


def value_to_note(value, base_note, scale):
    intervals = SCALES[scale]
    octave, degree = divmod(value, len(intervals))
    return base_note + octave * 12 + intervals[degree]


def sonify(sequence, period, out_path, base_note=60, scale="pentatonic",
           note_len_beats=0.5, tempo_bpm=132, repeats=2, mark_loops=False):
    """
    Write `sequence` to a MIDI file, repeated `repeats` times so the
    listener can hear the Pisano period loop back on itself.

    Notes are written in the register value_to_note() produces, with no
    modification -- so the file can be split by register (e.g. a
    vertical slice around middle C onto two instruments) without a loop
    marker distorting it.

    If `mark_loops` is True, a GM percussion "open triangle" hit on
    channel 10 marks the start of each pass. This relies on the
    playback instrument honouring the GM percussion channel, so it is
    opt-in rather than the default.
    """
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)

    track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(tempo_bpm), time=0))
    track.append(mido.Message("program_change", program=8, channel=0, time=0))  # celesta

    ticks = mid.ticks_per_beat
    note_ticks = int(ticks * note_len_beats)
    ding_ticks = note_ticks // 4

    period_seq = sequence[1:period + 1] if period else sequence[1:]

    for r in range(repeats):
        for i, value in enumerate(period_seq):
            note = value_to_note(value, base_note, scale)
            if mark_loops and i == 0:
                # ding sounds together with the downbeat note, not before
                # it -- delaying the downbeat would push every subsequent
                # note off the tempo grid, a little more with each repeat
                track.append(mido.Message("note_on", note=81, velocity=90, channel=9, time=0))
                track.append(mido.Message("note_on", note=note, velocity=80, channel=0, time=0))
                track.append(mido.Message("note_off", note=81, velocity=0, channel=9, time=ding_ticks))
                track.append(mido.Message("note_off", note=note, velocity=0, channel=0, time=note_ticks - ding_ticks))
            else:
                track.append(mido.Message("note_on", note=note, velocity=80, channel=0, time=0))
                track.append(mido.Message("note_off", note=note, velocity=0, channel=0, time=note_ticks))

    mid.save(out_path)
    return out_path


def trace_limit_type(value):
    if value.lower() == "all":
        return None
    return int(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=12, help="modulus n (default 12)")
    parser.add_argument("--out", default=None, help="output MIDI path")
    parser.add_argument("--scale", choices=SCALES.keys(), default="pentatonic")
    parser.add_argument("--base-note", type=int, default=60, help="MIDI note for value 0")
    parser.add_argument("--tempo", type=int, default=132, help="tempo in BPM")
    parser.add_argument("--note-len", type=float, default=0.5, help="note length in beats")
    parser.add_argument("--repeats", type=int, default=2, help="times to loop the period")
    parser.add_argument("--trace-limit", type=trace_limit_type, default=20,
                         help="max operation-card rows to print ('all' for no limit)")
    parser.add_argument("--mark-loops", action="store_true",
                         help="add a channel-10 GM percussion hit at the start of each loop "
                              "(requires a GM-aware drum kit on channel 10 to sound right; "
                              "off by default so note registers stay untouched)")
    args = parser.parse_args()

    out_path = args.out or f"fib_pisano_n{args.n}.mid"

    print(f"Fibonacci mod {args.n} on a simulated Analytical Engine")
    print("=" * 60)
    engine, sequence, period = fibonacci_mod_n(args.n)

    print("\nOperation Cards run by the Mill (Note-G style):")
    engine.print_trace(limit=args.trace_limit)

    print(f"\nSequence (F(k) mod {args.n}):")
    print(sequence[1:period + 1] if period else sequence)
    print(f"\nPisano period pi({args.n}) = {period}")
    print(f"Total engine operations: {engine.op_count}")

    sonify(sequence, period, out_path, base_note=args.base_note, scale=args.scale,
           note_len_beats=args.note_len, tempo_bpm=args.tempo, repeats=args.repeats,
           mark_loops=args.mark_loops)
    print(f"\nWrote {args.repeats} repeats of the period to: {out_path}")


if __name__ == "__main__":
    main()
