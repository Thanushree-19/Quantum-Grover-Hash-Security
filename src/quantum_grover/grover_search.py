
import math

from qiskit import QuantumCircuit

from .oracle import create_grover_oracle, find_marked_inputs


def create_diffusion_operator(n_qubits: int) -> QuantumCircuit:
    """
    Create Grover's diffusion operator.
    """

    if not 1 <= n_qubits <= 8:
        raise ValueError("n_qubits must be between 1 and 8.")

    diffusion = QuantumCircuit(n_qubits, name="Diffusion")

    # Step 1: Apply Hadamard gates.
    diffusion.h(range(n_qubits))

    # Step 2: Apply X gates.
    diffusion.x(range(n_qubits))

    # Step 3: Apply a phase operation to the all-ones state.
    if n_qubits == 1:
        diffusion.z(0)
    else:
        diffusion.h(n_qubits - 1)
        diffusion.mcx(list(range(n_qubits - 1)), n_qubits - 1)
        diffusion.h(n_qubits - 1)

    # Step 4: Reverse the X and Hadamard gates.
    diffusion.x(range(n_qubits))
    diffusion.h(range(n_qubits))

    # Set the global phase for the standard diffusion operator.
    diffusion.global_phase = math.pi

    return diffusion


def create_grover_circuit(
    hash_map: dict,
    target_hash,
    n_bits: int,
    iterations: int | None = None,
) -> QuantumCircuit:
    """
    Build Grover's search circuit using the existing oracle
    and the diffusion operator.
    """

    if not 1 <= n_bits <= 8:
        raise ValueError("n_bits must be between 1 and 8.")

    # Find the inputs whose hashes match the target.
    marked_inputs = find_marked_inputs(hash_map, target_hash)

    if not marked_inputs:
        raise ValueError("No input produces the target hash.")

    total_inputs = 2**n_bits
    number_marked = len(marked_inputs)

    if number_marked > total_inputs:
        raise ValueError("Invalid number of matching inputs.")

    # Choose a reasonable iteration count automatically.
    if iterations is None:
        if number_marked == total_inputs:
            iterations = 0
        else:
            angle = math.asin(math.sqrt(number_marked / total_inputs))
            iterations = max(
                0,
                round(math.pi / (4 * angle) - 0.5),
            )

    if not isinstance(iterations, int) or iterations < 0:
        raise ValueError("iterations must be a non-negative integer.")

    # Create the oracle and diffusion circuits.
    oracle = create_grover_oracle(hash_map, target_hash, n_bits)
    diffusion = create_diffusion_operator(n_bits)

    # Build the complete Grover circuit.
    grover = QuantumCircuit(n_bits, n_bits, name="Grover Search")

    # Step 1: Give every input an equal starting amplitude.
    grover.h(range(n_bits))

    # Step 2: Repeat oracle + diffusion.
    for _ in range(iterations):
        grover.compose(oracle, inplace=True)
        grover.compose(diffusion, inplace=True)

    # Step 3: Measure the input qubits.
    grover.measure(range(n_bits), range(n_bits))

    return grover
