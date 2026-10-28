
from qiskit import QuantumCircuit
from qiskit.circuit.library import DiagonalGate


def find_marked_inputs(hash_map, target_hash):
    """
    Find all inputs whose hash matches the target hash.
    """
    marked_inputs = []

    for input_value, hash_value in hash_map.items():
        if hash_value == target_hash:
            marked_inputs.append(input_value)

    return marked_inputs


def create_grover_oracle(hash_map, target_hash, n_bits):
    """
    Create a quantum phase oracle.

    Matching inputs receive phase -1.
    Other inputs receive phase +1.
    """

    if not 1 <= n_bits <= 8:
        raise ValueError("n_bits must be between 1 and 8.")

    expected_inputs = set(range(2**n_bits))

    if set(hash_map.keys()) != expected_inputs:
        raise ValueError(
            "hash_map must contain every input from "
            "0 to 2**n_bits - 1."
        )

    marked_inputs = find_marked_inputs(hash_map, target_hash)

    if not marked_inputs:
        raise ValueError(
            "No input produces the target hash."
        )

    # Start with phase +1 for every possible input.
    diagonal_values = [1] * (2**n_bits)

    # Mark every matching input with phase -1.
    for input_value in marked_inputs:
        diagonal_values[input_value] = -1

    # Create the quantum circuit.
    oracle = QuantumCircuit(n_bits, name="Grover Oracle")

    # Create a diagonal quantum gate and add it to the circuit.
    phase_gate = DiagonalGate(diagonal_values)
    oracle.append(phase_gate, list(range(n_bits)))

    return oracle
