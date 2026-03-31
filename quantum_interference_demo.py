"""Small educational demos of phase, interference, and Grover search in Qiskit.

Run with:
    python quantum_interference_demo.py

Required packages:
    pip install "qiskit>=1.0" "qiskit-aer>=0.14"

Optional plotting:
    pip install matplotlib
"""

from __future__ import annotations

from typing import Dict, Sequence

try:
    from qiskit import QuantumCircuit, transpile
    from qiskit.quantum_info import Statevector
    from qiskit_aer import AerSimulator
except ImportError as exc:  # pragma: no cover - this is a user-facing import guard.
    raise SystemExit(
        "This demo requires Qiskit and Qiskit Aer.\n"
        'Install them with: pip install "qiskit>=1.0" "qiskit-aer>=0.14"\n'
        "Optional plotting: pip install matplotlib"
    ) from exc

try:
    import matplotlib.pyplot as plt
except ImportError:  # pragma: no cover - plotting is optional.
    plt = None


def format_complex(value: complex, digits: int = 3) -> str:
    """Format a complex number in a compact beginner-friendly way."""
    real = 0.0 if abs(value.real) < 1e-12 else value.real
    imag = 0.0 if abs(value.imag) < 1e-12 else value.imag

    if imag == 0.0:
        return f"{real:.{digits}f}"
    if real == 0.0:
        return f"{imag:.{digits}f}j"
    sign = "+" if imag >= 0 else "-"
    return f"{real:.{digits}f} {sign} {abs(imag):.{digits}f}j"


def basis_label(index: int, num_qubits: int) -> str:
    """Return a computational basis label such as |01>."""
    return f"|{index:0{num_qubits}b}>"


def print_statevector(
    statevector: Statevector,
    title: str,
    *,
    digits: int = 3,
    hide_zero_amplitudes: bool = False,
) -> None:
    """Pretty-print amplitudes and probabilities for each basis state."""
    num_qubits = statevector.num_qubits
    print(f"\n{title}")
    print("-" * len(title))
    print(f"{'Basis':<8} {'Amplitude':<20} {'Probability':>12}")

    for index, amplitude in enumerate(statevector.data):
        probability = abs(amplitude) ** 2
        if hide_zero_amplitudes and probability < 1e-12:
            continue
        print(
            f"{basis_label(index, num_qubits):<8} "
            f"{format_complex(amplitude, digits):<20} "
            f"{probability:>11.3f}"
        )


def print_counts(counts: Dict[str, int], shots: int, title: str) -> None:
    """Print histogram counts in a compact text form."""
    print(f"\n{title}")
    print("-" * len(title))
    for bitstring, count in sorted(counts.items()):
        print(f"{bitstring}: {count:>5}  ({count / shots:.3f})")


def maybe_plot_probabilities(
    labels: Sequence[str],
    before: Sequence[float],
    after: Sequence[float],
    title: str,
) -> None:
    """Show a simple before/after probability bar chart if matplotlib is installed."""
    if plt is None:
        print("\nmatplotlib not installed, skipping probability plot.")
        return

    x_positions = range(len(labels))
    width = 0.35

    fig, axis = plt.subplots(figsize=(8, 4.5))
    axis.bar([x - width / 2 for x in x_positions], before, width=width, label="Before")
    axis.bar([x + width / 2 for x in x_positions], after, width=width, label="After")
    axis.set_xticks(list(x_positions))
    axis.set_xticklabels(labels)
    axis.set_ylim(0, 1.0)
    axis.set_ylabel("Probability")
    axis.set_title(title)
    axis.legend()
    fig.tight_layout()
    plt.show()


def run_measurement_counts(circuit: QuantumCircuit, shots: int = 2048) -> Dict[str, int]:
    """Sample measurement outcomes using the modern Aer simulator backend."""
    simulator = AerSimulator()
    compiled = transpile(circuit, simulator)
    result = simulator.run(compiled, shots=shots).result()
    return result.get_counts()


def uniform_superposition_circuit(num_qubits: int) -> QuantumCircuit:
    """Prepare the equal superposition over all computational basis states."""
    circuit = QuantumCircuit(num_qubits)
    circuit.h(range(num_qubits))
    return circuit


def mark_11_with_cz(circuit: QuantumCircuit) -> None:
    """Phase oracle for |11>: multiply only the |11> amplitude by -1."""
    circuit.cz(0, 1)


def mark_basis_state_with_phase_flip(circuit: QuantumCircuit, target: str) -> None:
    """Mark an arbitrary 2-qubit computational basis state with a phase flip.

    This is still an explicit hand-built oracle: move the target to |11> with X gates,
    apply CZ, then undo the X gates.
    """
    if len(target) != 2 or any(bit not in "01" for bit in target):
        raise ValueError("target must be a 2-bit string such as '11' or '01'")

    for qubit, bit in enumerate(reversed(target)):
        if bit == "0":
            circuit.x(qubit)
    circuit.cz(0, 1)
    for qubit, bit in enumerate(reversed(target)):
        if bit == "0":
            circuit.x(qubit)


def diffusion_operator_2q() -> QuantumCircuit:
    """2-qubit Grover diffusion operator: H^⊗2 X^⊗2 CZ X^⊗2 H^⊗2."""
    circuit = QuantumCircuit(2, name="Diffusion")
    circuit.h([0, 1])
    circuit.x([0, 1])
    circuit.cz(0, 1)
    circuit.x([0, 1])
    circuit.h([0, 1])
    return circuit


def one_qubit_phase_demo() -> None:
    """Part A: show how a relative phase turns into a bit flip after recombination."""
    print("\n=== Part A: 1-Qubit Interference Demo ===")
    print("Start in |0>, create superposition, add a Z phase, then recombine with H.")

    initial = QuantumCircuit(1)
    sv_initial = Statevector.from_instruction(initial)
    print_statevector(sv_initial, "Initial state: |0>")

    after_h = QuantumCircuit(1)
    after_h.h(0)
    sv_after_h = Statevector.from_instruction(after_h)
    print_statevector(sv_after_h, "After H: (|0> + |1>) / sqrt(2)")
    print("Check: H|0> creates equal amplitudes, so both measurement probabilities are 1/2.")

    after_hz = QuantumCircuit(1)
    after_hz.h(0)
    after_hz.z(0)
    sv_after_hz = Statevector.from_instruction(after_hz)
    print_statevector(sv_after_hz, "After H then Z: (|0> - |1>) / sqrt(2)")
    print("Z changes the relative phase of |1> by pi, but probabilities are still 1/2 and 1/2.")

    after_hzh = QuantumCircuit(1)
    after_hzh.h(0)
    after_hzh.z(0)
    after_hzh.h(0)
    sv_after_hzh = Statevector.from_instruction(after_hzh)
    print_statevector(sv_after_hzh, "After HZH: final state")
    assert abs(sv_after_hzh.data[0]) < 1e-12
    assert abs(sv_after_hzh.data[1] - 1) < 1e-12
    print("This verifies HZH|0> = |1>: the phase difference becomes a measurable outcome after recombination.")

    measured = after_hzh.copy()
    measured.measure_all()
    counts = run_measurement_counts(measured)
    print_counts(counts, 2048, "Measurement counts for HZH|0>")


def two_qubit_oracle_demo() -> None:
    """Part B: mark |11> with a phase flip and inspect the statevector."""
    print("\n=== Part B: 2-Qubit Phase Oracle Demo ===")
    print("Create a uniform superposition, mark |11> with a CZ phase flip, then optionally recombine.")

    prepare = uniform_superposition_circuit(2)
    sv_before = Statevector.from_instruction(prepare)
    print_statevector(sv_before, "Before oracle: equal superposition over |00>, |01>, |10>, |11>")

    oracle_circuit = prepare.copy()
    mark_basis_state_with_phase_flip(oracle_circuit, "11")
    sv_after_oracle = Statevector.from_instruction(oracle_circuit)
    print_statevector(sv_after_oracle, "After oracle: |11> has a negative amplitude")
    print("The oracle changed only phase, not the measurement probabilities: all four states are still at 1/4.")

    recombined = oracle_circuit.copy()
    recombined.h([0, 1])
    sv_after_recombine = Statevector.from_instruction(recombined)
    print_statevector(
        sv_after_recombine,
        "After recombination with H on both qubits",
        hide_zero_amplitudes=True,
    )
    print("The relative phase now affects amplitudes after recombination, so interference becomes visible.")


def grover_two_qubit_demo(marked_state: str = "11", shots: int = 2048, plot: bool = True) -> None:
    """Part C: one Grover iteration for a single marked 2-qubit basis state."""
    print("\n=== Part C: 2-Qubit Grover Demo ===")
    print("One Grover iteration = prepare superposition -> phase oracle -> diffusion.")

    prepare = uniform_superposition_circuit(2)
    sv_prepared = Statevector.from_instruction(prepare)
    print_statevector(sv_prepared, "Prepared state: uniform superposition")

    oracle_step = prepare.copy()
    mark_basis_state_with_phase_flip(oracle_step, marked_state)
    sv_after_oracle = Statevector.from_instruction(oracle_step)
    print_statevector(sv_after_oracle, f"After oracle: |{marked_state}> is phase-marked")

    full_grover = oracle_step.copy()
    full_grover.compose(diffusion_operator_2q(), inplace=True)
    sv_after_diffusion = Statevector.from_instruction(full_grover)
    print_statevector(sv_after_diffusion, "After diffusion: amplitude amplification")
    amplified_index = int(marked_state, 2)
    amplified_probability = abs(sv_after_diffusion.data[amplified_index]) ** 2
    assert amplified_probability > 0.999999
    print(f"For the 2-qubit single-solution case, one Grover iteration ideally rotates all amplitude onto |{marked_state}>.")

    measured = full_grover.copy()
    measured.measure_all()
    counts = run_measurement_counts(measured, shots=shots)
    print_counts(counts, shots, "Measurement counts after one Grover iteration")

    labels = [basis_label(index, 2) for index in range(4)]
    before_probs = [abs(amplitude) ** 2 for amplitude in sv_after_oracle.data]
    after_probs = [abs(amplitude) ** 2 for amplitude in sv_after_diffusion.data]

    if plot:
        maybe_plot_probabilities(
            labels,
            before_probs,
            after_probs,
            "Grover Probabilities: After Oracle vs After Diffusion",
        )


def main() -> None:
    """Run all demos in order of increasing sophistication."""
    print("Quantum interference demo using modern Qiskit APIs")
    print("This script emphasizes phase, interference, and Grover amplitude amplification.")

    one_qubit_phase_demo()
    two_qubit_oracle_demo()
    grover_two_qubit_demo()


if __name__ == "__main__":
    main()
