# Analytical Engine — Fibonacci & Pisano Periods

A small Python demo built for a talk on Ada Lovelace, the Analytical Engine,
and algorithmic composition.

It contains:

- **A minimal simulator of Babbage's Analytical Engine**, in the spirit of
  Lovelace's 1843 "Note G": a *Store* of numbered variable columns, a *Mill*
  that performs one arithmetic operation at a time, and a sequence of
  *Operation Cards* that are logged as they run, echoing Note G's table of
  operations. The engine only knows ADD and SUBTRACT — modulo is built from
  repeated subtraction, the same way Note G composes a whole computation
  from the four base arithmetic operations.
- **A Fibonacci-mod-*n* algorithm** run on that engine, which finds the
  [Pisano period](https://en.wikipedia.org/wiki/Pisano_period) π(*n*): the
  point at which the sequence of Fibonacci numbers mod *n* starts repeating.
- **Sonification**: the sequence is mapped onto a musical scale and written
  out as a MIDI file (via [`mido`](https://mido.readthedocs.io/)), looped
  twice so you can *hear* the period repeat, with a short percussive "ding"
  marking each loop boundary.

## Usage

```bash
pip install -r requirements.txt
python3 analytical_engine_fibonacci.py --n 12
```

This prints the Mill's operation-card trace, the sequence, and π(*n*), and
writes a MIDI file (default `fib_pisano_n12.mid`).

Options:

| Flag | Meaning | Default |
|---|---|---|
| `--n` | modulus *n* | `12` |
| `--out` | output MIDI path | `fib_pisano_n<n>.mid` |
| `--scale` | `chromatic`, `major`, `minor`, `pentatonic` | `pentatonic` |
| `--base-note` | MIDI note number for value 0 | `60` |
| `--tempo` | tempo in BPM | `132` |
| `--note-len` | note length in beats | `0.5` |
| `--repeats` | number of times to loop the period | `2` |
| `--trace-limit` | max operation-card rows printed | `20` |

An example output is in [`examples/fib_pisano_n12.mid`](examples/fib_pisano_n12.mid)
(π(12) = 24).

## Background

Ada Lovelace's 1843 notes on Babbage's proposed Analytical Engine include
"Note G", which contains what is widely regarded as the first published
computer program — an algorithm for computing Bernoulli numbers, laid out
as a table of operations acting on variables. This demo borrows that
structure (Store, Mill, Operation Cards) for a much simpler algorithm, and
adds a sonification step that Lovelace herself anticipated when she wrote
that the Engine "might act upon other things besides number", including
composing music.
