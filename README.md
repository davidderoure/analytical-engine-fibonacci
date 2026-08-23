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

Install the one dependency, then run the script with a modulus `--n`:

```bash
pip install -r requirements.txt
python3 analytical_engine_fibonacci.py --n 12
```

This does three things:

1. Runs the Fibonacci-mod-*n* algorithm on the simulated Engine and prints
   the Mill's operation-card trace (capped at `--trace-limit` rows).
2. Prints the resulting sequence and the Pisano period π(*n*).
3. Writes a MIDI file — by default `fib_pisano_n<n>.mid` in the current
   directory — containing `--repeats` loops of the period.

Open the output file in any DAW or MIDI player (see
[Listening tips](#listening-tips) below).

### Options

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

### Examples

```bash
# default: n=12, minor pentatonic, one octave centred on middle C
python3 analytical_engine_fibonacci.py --n 12

# a bigger modulus — longer period, wider melodic range
python3 analytical_engine_fibonacci.py --n 30 --out fib30.mid

# major scale, slower tempo, longer notes, four loops
python3 analytical_engine_fibonacci.py --n 12 --scale major --tempo 90 --note-len 1 --repeats 4

# start an octave lower, and print the full operation trace
python3 analytical_engine_fibonacci.py --n 12 --base-note 48 --trace-limit all
```

An example output is in [`examples/fib_pisano_n12.mid`](examples/fib_pisano_n12.mid)
(π(12) = 24).

## Listening tips

The MIDI file is deliberately plain (one instrument, fixed velocity) so it
sounds different depending on what plays it back:

- **Instrument choice matters a lot.** A harp patch (e.g. in Logic Pro)
  suits the plucked, arpeggio-like character of the sequence particularly
  well.
- **Restricting the register introduces rhythm.** Because `value_to_note`
  spreads values across several octaves (see the mapping table in the repo
  discussion), narrowing the instrument's audible range — or transposing /
  filtering to a "vertical slice" of the output in your DAW — drops out
  every note that falls outside it. What's left is no longer a continuous
  melodic line but a sparser, syncopated pattern: the numeric structure of
  the Pisano sequence starts to read as rhythm rather than pitch.

## Background

Ada Lovelace's 1843 notes on Babbage's proposed Analytical Engine include
"Note G", which contains what is widely regarded as the first published
computer program — an algorithm for computing Bernoulli numbers, laid out
as a table of operations acting on variables. This demo borrows that
structure (Store, Mill, Operation Cards) for a much simpler algorithm, and
adds a sonification step that Lovelace herself anticipated when she wrote
that the Engine "might act upon other things besides number", including
composing music.
