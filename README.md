# Quantum Interference Demo

This repository contains a small Qiskit script that demonstrates how quantum phase becomes physically useful only after interference recombines amplitudes.

The Grover section now frames the oracle as a tiny search problem instead of simply saying "mark `|11>`":
find the 2-bit value `x` such that `x + 1 = 4`.
The unique solution is `x = 3`, so the oracle marks `|11>`.

Run it with:

```bash
python quantum_interference_demo.py
```

Optional chart:

```bash
python quantum_interference_demo.py --plot
```

Save the visualizations and circuit diagrams to a folder:

```bash
python quantum_interference_demo.py --save-plots outputs
```

## Install

Use a recent Python environment, then install:

```bash
pip install "qiskit>=1.0"
```

Optional plotting:

```bash
pip install matplotlib
```

Optional Aer backend:

```bash
pip install "qiskit-aer>=0.14"
```

## What The Demo Shows

The script is split into three parts:

1. `one_qubit_phase_demo()`
   Starts in `|0>`, applies `H`, then `Z`, then `H` again.
   This shows:
   `H|0> = (|0> + |1>) / sqrt(2)`,
   `Z` changes the relative phase of `|1>`,
   and `HZH|0> = |1>`.

2. `two_qubit_oracle_demo()`
   Creates a uniform 2-qubit superposition and uses a controlled-Z-based phase oracle to mark the unique basis state that solves a tiny classical predicate.

3. `grover_two_qubit_demo()`
   Performs one full 2-qubit Grover iteration:
   state preparation,
   phase oracle,
   diffusion operator, using the state selected by the predicate,
   and then measurement.

## Visualizations

If `matplotlib` is installed, the script can now show:

- stage-by-stage probability bar charts for the 1-qubit demo,
- a 3-stage probability comparison for the 2-qubit oracle demo,
- a multi-stage Grover amplification chart,
- a direct before/after Grover probability comparison.

If you use `--save-plots outputs`, the script also writes text circuit diagrams into that folder so you can inspect the gate sequence without rerunning the demo.

## Physical Intuition

### What phase means operationally

A quantum amplitude is a complex number. Measurement probabilities depend on the magnitude squared of that number, not directly on its sign or complex angle.

That means these two states have the same measurement probabilities:

- `( |0> + |1> ) / sqrt(2)`
- `( |0> - |1> ) / sqrt(2)`

The only difference is the relative phase between the basis states.

### Why phase alone does not change probabilities

If you flip the sign of one amplitude with a phase oracle, the probability of that basis state does not immediately change. For example, changing an amplitude from `+1/2` to `-1/2` keeps the probability at `(1/2)^2 = 1/4`.

So a phase oracle does not by itself make the marked answer more likely to appear in a measurement.

### How interference changes probabilities

The key step is recombination. When another unitary mixes basis states together, amplitudes add or cancel.

That is where the relative phase matters:

- amplitudes with the same sign can reinforce each other,
- amplitudes with opposite sign can cancel.

In the 1-qubit demo, the second Hadamard converts an invisible phase difference into a visible outcome. The state
`( |0> - |1> ) / sqrt(2)` becomes `|1>`.

### How this connects to Grover's algorithm

Grover uses exactly this pattern:

1. prepare a uniform superposition over all candidate answers,
2. apply a phase oracle that marks the good answer by flipping its sign,
3. apply the diffusion operator to recombine amplitudes so the marked answer is amplified.

For the special 2-qubit, one-solution case, one Grover iteration is enough to drive the ideal state entirely onto the marked basis state.

In this demo, the "good answer" is defined by a simple check:
which 2-bit number satisfies `x + 1 = 4`?
The code first determines that the unique valid candidate is `x = 3`, then builds the phase-marking step for `|11>`.

## Implementation Notes

- The script uses modern state inspection via `Statevector.from_instruction(...)`.
- Measurement sampling uses ideal `Statevector.sample_counts(...)` by default for a simple zero-noise demo.
- If `qiskit-aer` is installed, the helper can optionally use `qiskit_aer.AerSimulator`.
- Circuits are intentionally hand-built for clarity rather than hidden behind helper frameworks.
- The 2-qubit oracle is implemented directly with `CZ` plus optional `X` gates, which is the clearest way to mark whichever 2-qubit basis state solves the toy predicate.

## Expected Highlights

When you run the script, you should see:

- equal amplitudes after the first Hadamard in the 1-qubit demo,
- a sign flip after `Z` with unchanged probabilities,
- `|1>` after `HZH`,
- a negative amplitude on the uniquely valid search answer after the 2-qubit oracle,
- and strong amplification of that answer after the Grover diffusion step.
