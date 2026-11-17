# quantum interference demo

a small Qiskit demo of phase, interference and a two-qubit Grover search.

the search predicate is `x + 1 = 4` over two-bit values. the code identifies `x = 3` classically and constructs an oracle that marks `|11>`. this illustrates amplitude amplification; it is not a quantum speedup for solving the predicate.

run it with:

```bash
python quantum_interference_demo.py
```

optional chart:

```bash
python quantum_interference_demo.py --plot
```

save the visualizations and circuit diagrams to a folder:

```bash
python quantum_interference_demo.py --save-plots outputs
```

## install

use a recent Python environment, then install:

```bash
pip install "qiskit>=1.0"
```

optional plotting:

```bash
pip install matplotlib
```

optional aer backend:

```bash
pip install "qiskit-aer>=0.14"
```

## circuits

the script is split into three parts:

1. `one_qubit_phase_demo()`
   starts in `|0>`, applies `H`, then `Z`, then `H` again.
   this shows:
   `H|0> = (|0> + |1>) / sqrt(2)`,
   `Z` changes the relative phase of `|1>`,
   and `HZH|0> = |1>`.

2. `two_qubit_oracle_demo()`
   creates a uniform 2-qubit superposition and uses a controlled-z-based phase oracle to mark the unique basis state that solves a tiny classical predicate.

3. `grover_two_qubit_demo()`
   performs one full 2-qubit Grover iteration:
   state preparation,
   phase oracle,
   diffusion operator, using the state selected by the predicate,
   and then measurement.

## visualizations

with `matplotlib` installed, the script shows:

- stage-by-stage probability bar charts for the 1-qubit demo,
- a 3-stage probability comparison for the 2-qubit oracle demo,
- a multi-stage Grover amplification chart,
- a direct before/after Grover probability comparison.

if you use `--save-plots outputs`, the script also writes text circuit diagrams into that folder so you can inspect the gate sequence without rerunning the demo.

## phase and interference

### what phase means operationally

a quantum amplitude is a complex number. measurement probabilities depend on the magnitude squared of that number, not directly on its sign or complex angle.

that means these two states have the same measurement probabilities:

- `( |0> + |1> ) / sqrt(2)`
- `( |0> - |1> ) / sqrt(2)`

the only difference is the relative phase between the basis states.

### why phase alone does not change probabilities

if you flip the sign of one amplitude with a phase oracle, the probability of that basis state does not immediately change. for example, changing an amplitude from `+1/2` to `-1/2` keeps the probability at `(1/2)^2 = 1/4`.

so a phase oracle does not by itself make the marked answer more likely to appear in a measurement.

### how interference changes probabilities

the key step is recombination. when another unitary mixes basis states together, amplitudes add or cancel.

that is where the relative phase matters:

- amplitudes with the same sign can reinforce each other,
- amplitudes with opposite sign can cancel.

in the 1-qubit demo, the second Hadamard converts an invisible phase difference into a visible outcome. the state
`( |0> - |1> ) / sqrt(2)` becomes `|1>`.

### how this connects to grover's algorithm

Grover uses exactly this pattern:

1. prepare a uniform superposition over all candidate answers,
2. apply a phase oracle that marks the good answer by flipping its sign,
3. apply the diffusion operator to recombine amplitudes so the marked answer is amplified.

for the special 2-qubit, one-solution case, one Grover iteration is enough to drive the ideal state entirely onto the marked basis state.

in this demo, the "good answer" is defined by a simple check:
which 2-bit number satisfies `x + 1 = 4`?
the code first determines that the unique valid candidate is `x = 3`, then builds the phase-marking step for `|11>`.

## implementation notes

- the script uses modern state inspection via `Statevector.from_instruction(...)`.
- measurement sampling uses ideal `Statevector.sample_counts(...)` by default for a simple zero-noise demo.
- if `qiskit-aer` is installed, the helper can optionally use `qiskit_aer.AerSimulator`.
- circuits are intentionally hand-built for clarity rather than hidden behind helper frameworks.
- the 2-qubit oracle is implemented directly with `CZ` plus optional `X` gates, to mark the two-qubit basis state that solves the toy predicate.

## expected output

when you run the script, you should see:

- equal amplitudes after the first Hadamard in the 1-qubit demo,
- a sign flip after `Z` with unchanged probabilities,
- `|1>` after `HZH`,
- a negative amplitude on the uniquely valid search answer after the 2-qubit oracle,
- and strong amplification of that answer after the Grover diffusion step.
