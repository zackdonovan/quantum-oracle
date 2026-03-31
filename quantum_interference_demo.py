"""Small educational demos of phase, interference, and Grover search in Qiskit.

Run with:
    python quantum_interference_demo.py
    python quantum_interference_demo.py --plot

Required packages:
    pip install "qiskit>=1.0"

Optional plotting:
    pip install matplotlib

Optional Aer backend:
    pip install "qiskit-aer>=0.14"
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable, Dict, Sequence

try:
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector
except ImportError as exc:  # pragma: no cover - this is a user-facing import guard.
    raise SystemExit(
        "This demo requires Qiskit.\n"
        'Install it with: pip install "qiskit>=1.0"\n'
        'Optional Aer backend: pip install "qiskit-aer>=0.14"\n'
        "Optional plotting: pip install matplotlib"
    ) from exc

try:
    from qiskit_aer import AerSimulator
except ImportError:  # pragma: no cover - Aer is optional.
    AerSimulator = None

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
    *,
    save_path: str | None = None,
) -> None:
    """Show a simple before/after probability bar chart if matplotlib is installed."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:  # pragma: no cover - plotting is optional.
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
    if save_path is not None:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=160)
        print(f"Saved plot to {save_path}")
    plt.show()


def maybe_plot_stage_probabilities(
    labels: Sequence[str],
    stage_titles: Sequence[str],
    probability_sets: Sequence[Sequence[float]],
    title: str,
    *,
    save_path: str | None = None,
) -> None:
    """Plot probabilities across several stages to make interference visually explicit."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:  # pragma: no cover - plotting is optional.
        print("\nmatplotlib not installed, skipping stage probability plot.")
        return

    fig, axes = plt.subplots(
        1,
        len(stage_titles),
        figsize=(4.8 * len(stage_titles), 4.5),
        sharey=True,
    )
    if len(stage_titles) == 1:
        axes = [axes]

    for axis, stage_title, probabilities in zip(axes, stage_titles, probability_sets):
        axis.bar(labels, probabilities, color="#2a6f97")
        axis.set_title(stage_title)
        axis.set_ylim(0, 1.0)
        axis.set_xlabel("Basis state")
        axis.grid(axis="y", alpha=0.25)

    axes[0].set_ylabel("Probability")
    fig.suptitle(title)
    fig.tight_layout()
    if save_path is not None:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=160)
        print(f"Saved plot to {save_path}")
    plt.show()


def maybe_save_circuit_diagram(circuit: QuantumCircuit, title: str, output_dir: str | None) -> None:
    """Save a text diagram of a circuit when an output directory is requested."""
    if output_dir is None:
        return

    safe_name = title.lower().replace(" ", "_").replace(":", "").replace("-", "_")
    output_path = Path(output_dir) / f"{safe_name}.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(str(circuit.draw(output="text")), encoding="utf-8")
    print(f"Saved circuit diagram to {output_path}")


def run_measurement_counts(
    circuit: QuantumCircuit,
    shots: int = 2048,
    *,
    prefer_aer: bool = False,
) -> Dict[str, int]:
    """Sample measurement outcomes from the final state.

    For a small educational demo, ideal statevector sampling is the most robust choice.
    If qiskit-aer is installed and prefer_aer=True, the function will try Aer first.
    """
    if prefer_aer and AerSimulator is not None:
        try:
            simulator = AerSimulator()
            result = simulator.run(circuit, shots=shots).result()
            return result.get_counts()
        except Exception as exc:  # pragma: no cover - fallback is environment-dependent.
            print("\nAerSimulator could not complete the measurement run.")
            print(f"Falling back to ideal statevector sampling instead. Reason: {exc}")

    unmeasured = circuit.remove_final_measurements(inplace=False)
    return Statevector.from_instruction(unmeasured).sample_counts(shots=shots)


def uniform_superposition_circuit(num_qubits: int) -> QuantumCircuit:
    """Prepare the equal superposition over all computational basis states."""
    circuit = QuantumCircuit(num_qubits)
    circuit.h(range(num_qubits))
    return circuit


def bitstring_for_index(index: int, num_qubits: int) -> str:
    """Return a bitstring such as '11' for a computational basis index."""
    return f"{index:0{num_qubits}b}"


def find_unique_solution_bitstring(
    num_qubits: int,
    predicate: Callable[[int], bool],
) -> str:
    """Classically define a tiny search problem and extract its unique solution.

    Grover needs an oracle that can recognize "good" states. For this educational
    demo, we keep the oracle hand-built and derive which basis state should be marked
    from a simple classical rule.
    """
    solutions = [
        bitstring_for_index(index, num_qubits)
        for index in range(2**num_qubits)
        if predicate(index)
    ]

    if len(solutions) != 1:
        raise ValueError(
            f"Expected exactly one marked state, but found {len(solutions)}: {solutions}"
        )

    return solutions[0]


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


def one_qubit_phase_demo(*, plot: bool = False, output_dir: str | None = None) -> None:
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

    if plot:
        labels = [basis_label(index, 1) for index in range(2)]
        maybe_plot_stage_probabilities(
            labels,
            ["Initial", "After H", "After HZ", "After HZH"],
            [
                [abs(amplitude) ** 2 for amplitude in sv_initial.data],
                [abs(amplitude) ** 2 for amplitude in sv_after_h.data],
                [abs(amplitude) ** 2 for amplitude in sv_after_hz.data],
                [abs(amplitude) ** 2 for amplitude in sv_after_hzh.data],
            ],
            "1-Qubit Interference: Probabilities at Each Stage",
            save_path=(
                str(Path(output_dir) / "one_qubit_probabilities.png")
                if output_dir is not None
                else None
            ),
        )
        maybe_save_circuit_diagram(after_hzh, "one_qubit_hzh_circuit", output_dir)


def example_search_predicate(candidate: int) -> bool:
    """Tiny search problem: find the 2-bit x such that x + 1 = 4."""
    return candidate + 1 == 4


def explain_search_problem(marked_state: str) -> None:
    """Print the small classical search problem that defines the marked state."""
    candidate_value = int(marked_state, 2)
    print("Search problem: find the 2-bit value x such that x + 1 = 4.")
    print(
        f"Among x in {{0, 1, 2, 3}}, the only solution is x = {candidate_value}, "
        f"which is |{marked_state}> in binary."
    )


def two_qubit_oracle_demo(
    marked_state: str,
    *,
    plot: bool = False,
    output_dir: str | None = None,
) -> None:
    """Part B: mark the unique solution state with a phase flip and inspect it."""
    print("\n=== Part B: 2-Qubit Phase Oracle Demo ===")
    explain_search_problem(marked_state)
    print("Create a uniform superposition, mark the solution with a phase flip, then recombine with the Grover-style diffusion map.")

    prepare = uniform_superposition_circuit(2)
    sv_before = Statevector.from_instruction(prepare)
    print_statevector(sv_before, "Before oracle: equal superposition over |00>, |01>, |10>, |11>")

    oracle_circuit = prepare.copy()
    mark_basis_state_with_phase_flip(oracle_circuit, marked_state)
    sv_after_oracle = Statevector.from_instruction(oracle_circuit)
    print_statevector(sv_after_oracle, f"After oracle: |{marked_state}> has a negative amplitude")
    print("The oracle changed only phase, not the measurement probabilities: all four states are still at 1/4.")

    recombined = oracle_circuit.copy()
    recombined.compose(diffusion_operator_2q(), inplace=True)
    sv_after_recombine = Statevector.from_instruction(recombined)
    print_statevector(
        sv_after_recombine,
        "After diffusion-style recombination",
    )
    print("Now the relative phase matters: amplitudes interfere so the marked answer is amplified while the others cancel.")

    if plot:
        labels = [basis_label(index, 2) for index in range(4)]
        maybe_plot_stage_probabilities(
            labels,
            ["Before Oracle", "After Oracle", "After Recombination"],
            [
                [abs(amplitude) ** 2 for amplitude in sv_before.data],
                [abs(amplitude) ** 2 for amplitude in sv_after_oracle.data],
                [abs(amplitude) ** 2 for amplitude in sv_after_recombine.data],
            ],
            "2-Qubit Oracle Demo: Phase Becomes Visible Through Interference",
            save_path=(
                str(Path(output_dir) / "two_qubit_oracle_probabilities.png")
                if output_dir is not None
                else None
            ),
        )
        maybe_save_circuit_diagram(oracle_circuit, "two_qubit_oracle_circuit", output_dir)


def grover_two_qubit_demo(
    marked_state: str,
    shots: int = 2048,
    *,
    plot: bool = False,
    output_dir: str | None = None,
) -> None:
    """Part C: one Grover iteration for a single marked 2-qubit basis state."""
    print("\n=== Part C: 2-Qubit Grover Demo ===")
    explain_search_problem(marked_state)
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
        maybe_plot_stage_probabilities(
            labels,
            ["Prepared", "After Oracle", "After Diffusion"],
            [
                [abs(amplitude) ** 2 for amplitude in sv_prepared.data],
                before_probs,
                after_probs,
            ],
            "Grover Search: Amplitude Amplification Across Stages",
            save_path=(
                str(Path(output_dir) / "grover_stage_probabilities.png")
                if output_dir is not None
                else None
            ),
        )
        maybe_plot_probabilities(
            labels,
            before_probs,
            after_probs,
            "Grover Probabilities: After Oracle vs After Diffusion",
            save_path=(
                str(Path(output_dir) / "grover_before_after.png")
                if output_dir is not None
                else None
            ),
        )
        maybe_save_circuit_diagram(full_grover, "grover_two_qubit_circuit", output_dir)


def parse_args() -> argparse.Namespace:
    """Parse command-line options for the demo script."""
    parser = argparse.ArgumentParser(
        description="Educational Qiskit demos for phase, interference, and Grover search."
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Show optional matplotlib visualizations for all demo stages.",
    )
    parser.add_argument(
        "--save-plots",
        metavar="DIR",
        help="Save plots and circuit text diagrams into DIR.",
    )
    return parser.parse_args()


def main() -> None:
    """Run all demos in order of increasing sophistication."""
    args = parse_args()
    print("Quantum interference demo using modern Qiskit APIs")
    print("This script emphasizes phase, interference, and Grover amplitude amplification.")

    marked_state = find_unique_solution_bitstring(2, example_search_predicate)
    print(
        "The script first solves a tiny classical predicate to decide which basis state "
        "the oracle should mark."
    )
    print(f"For this run, the unique solution is |{marked_state}>.\n")

    plot_enabled = args.plot or args.save_plots is not None
    one_qubit_phase_demo(plot=plot_enabled, output_dir=args.save_plots)
    two_qubit_oracle_demo(marked_state, plot=plot_enabled, output_dir=args.save_plots)
    grover_two_qubit_demo(marked_state, plot=plot_enabled, output_dir=args.save_plots)


if __name__ == "__main__":
    main()
