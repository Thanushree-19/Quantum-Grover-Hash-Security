
from src.hash_functions.toy_hash import create_toy_hash_system


def classical_preimage_search(hash_map, target_hash):
    """
    Find every input that produces the target hash.

    hash_map: Dictionary containing input -> hash mappings.
    target_hash: Integer representation of the target hash.

    Returns a list of matching inputs.
    """

    matching_inputs = []

    for input_value, hash_value in hash_map.items():
        if hash_value == target_hash:
            matching_inputs.append(input_value)

    return matching_inputs


def main():
    try:
        # Get input and hash sizes
        n_bits = int(input("Enter input bit size (2-8): "))
        m_bits = int(input("Enter hash output size (at least 1): "))

        if not 2 <= n_bits <= 8:
            print("Error: Input bit size must be between 2 and 8.")
            return

        if m_bits < 1:
            print("Error: Hash output size must be at least 1.")
            return

        # Generate and store all hash mappings
        hash_map = create_toy_hash_system(n_bits, m_bits)

        # Accept the target hash
        target_input = input(
            "\nEnter target hash (binary or decimal): "
        ).strip()

        # Convert target into an integer
        if (
            len(target_input) == m_bits
            and all(bit in "01" for bit in target_input)
        ):
            target_hash = int(target_input, 2)
        else:
            target_hash = int(target_input, 10)

        # Check that the target fits in the selected hash size
        if not 0 <= target_hash < 2**m_bits:
            print(
                f"Error: Target hash must be between 0 and "
                f"{2**m_bits - 1}."
            )
            return

        # Search for matching inputs
        results = classical_preimage_search(hash_map, target_hash)

        # Display results
        target_binary = format(target_hash, f"0{m_bits}b")

        print("\n--- Classical Preimage Search Results ---")
        print(f"Target hash (binary): {target_binary}")
        print(f"Target hash (decimal): {target_hash}")

        if results:
            print(f"Matching inputs (decimal): {results}")

            matching_binary = [
                format(value, f"0{n_bits}b")
                for value in results
            ]

            print(f"Matching inputs (binary): {matching_binary}")
            print(f"Number of matching inputs: {len(results)}")
        else:
            print("No input produces this hash.")

    except ValueError:
        print("Invalid input. Please enter valid numbers or a binary hash.")


if __name__ == "__main__":
    main()
