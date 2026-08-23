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
  twice so you can *hear* the period repeat. Notes are written exactly in
  the register `value_to_note()` produces, with nothing added — so the
  file can be split by register (e.g. a vertical slice around middle C
  onto two instruments) without any extra note distorting it.

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
| `--mark-loops` | add a channel-10 GM percussion hit at the start of each loop | off |

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

# mark each loop boundary with a channel-10 percussion hit (needs a
# GM-aware drum kit on channel 10 to actually sound like percussion —
# see Listening tips)
python3 analytical_engine_fibonacci.py --n 12 --mark-loops
```

### Example outputs

| File | `--n` | π(*n*) | Scale | Base note | Tempo | Notes |
|---|---|---|---|---|---|---|
| [`fib_pisano_n12.mid`](examples/fib_pisano_n12.mid) | 12 | 24 | pentatonic | C4 (60) | 132 | the default settings |
| [`fib_pisano_n7_minor.mid`](examples/fib_pisano_n7_minor.mid) | 7 | 16 | minor | C4 (60) | 120 | short loop, narrow range |
| [`fib_pisano_n17_major.mid`](examples/fib_pisano_n17_major.mid) | 17 | 36 | major | A3 (57) | 110 | longer period, brighter |
| [`fib_pisano_n25_chromatic.mid`](examples/fib_pisano_n25_chromatic.mid) | 25 | 100 | chromatic | C3 (48), sixteenth notes | 140 | long, dense, twelve-tone-ish |
| [`fib_pisano_n11_pentatonic_hi.mid`](examples/fib_pisano_n11_pentatonic_hi.mid) | 11 | 10 | pentatonic | C5 (72), 4 repeats | 160 | very short loop, high register |

Regenerate any of them, e.g.:

```bash
python3 analytical_engine_fibonacci.py --n 25 --scale chromatic --base-note 48 \
    --note-len 0.25 --tempo 140 --out examples/fib_pisano_n25_chromatic.mid
```

## Listening tips

The MIDI file is deliberately plain (one instrument, fixed velocity) so it
sounds different depending on what plays it back:

- **Instrument choice matters a lot.** A harp patch (e.g. in Logic Pro)
  suits the plucked, arpeggio-like character of the sequence particularly
  well.
- **Restricting the register introduces rhythm.** Because `value_to_note`
  spreads values across several octaves, narrowing the instrument's
  audible range — or splitting the output onto two instruments around a
  fixed pitch (e.g. everything below middle C to harp, everything above
  to piano) — drops out or reroutes notes outside each range. What's left
  reads as a sparser, syncopated pattern: the numeric structure of the
  Pisano sequence starts to sound like rhythm rather than pitch. Notes
  are never nudged out of their generated register to make room for
  anything else (see `--mark-loops` below), so a register split behaves
  predictably.
- **Marking loop boundaries.** By default nothing is added to mark where
  the period repeats — mark loop points manually in your DAW instead, or
  pass `--mark-loops` to add a channel-10 GM percussion hit at each
  boundary. That flag depends on the receiving instrument actually
  mapping channel 10 to a drum kit; on a plain single-instrument track it
  will just play as an ordinary (and out-of-register) note on that
  instrument, which is exactly what register-slicing wants to avoid.

## Background

Ada Lovelace's 1843 notes on Babbage's proposed Analytical Engine include
"Note G", which contains what is widely regarded as the first published
computer program — an algorithm for computing Bernoulli numbers, laid out
as a table of operations acting on variables. This demo borrows that
structure (Store, Mill, Operation Cards) for a much simpler algorithm, and
adds a sonification step that Lovelace herself anticipated when she wrote
that the Engine "might act upon other things besides number", including
composing music.
