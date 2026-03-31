# Quantum Interference Demo

This repository contains a small Qiskit script that demonstrates how quantum phase becomes physically useful only after interference recombines amplitudes.

Run it with:

```bash
python quantum_interference_demo.py
```

## Install

Use a recent Python environment, then install:

```bash
pip install "qiskit>=1.0" "qiskit-aer>=0.14"
```

Optional plotting:

```bash
pip install matplotlib
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
   Creates a uniform 2-qubit superposition and uses a controlled-Z gate as a phase oracle that marks `|11>` by multiplying its amplitude by `-1`.

3. `grover_two_qubit_demo()`
   Performs one full 2-qubit Grover iteration:
   state preparation,
   phase oracle,
   diffusion operator,
   and then measurement.

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

## Implementation Notes

- The script uses modern state inspection via `Statevector.from_instruction(...)`.
- Measurement sampling uses `qiskit_aer.AerSimulator`.
- Circuits are intentionally hand-built for clarity rather than hidden behind helper frameworks.
- The 2-qubit oracle is implemented directly with `CZ`, which is the clearest way to mark `|11>`.

## Expected Highlights

When you run the script, you should see:

- equal amplitudes after the first Hadamard in the 1-qubit demo,
- a sign flip after `Z` with unchanged probabilities,
- `|1>` after `HZH`,
- a negative amplitude on `|11>` after the 2-qubit oracle,
- and strong amplification of `|11>` after the Grover diffusion step.
