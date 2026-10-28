
def create_toy_hash_system(n_bits: int, m_bits: int):
    """
    Evaluates the toy hash function for all possible inputs
    using user-defined input bit size (n) and hash size (m).

    Returns:
        hash_map: Dictionary containing input -> hash mappings.
    """

    if not (2 <= n_bits <= 8):
        raise ValueError("Input bit size (n) must be between 2 and 8.")

    if m_bits < 1:
        raise ValueError("Hash size (m) must be at least 1 bit.")

    print("\n--- Toy Hash System Configuration ---")
    print(f"Input Bit Size (n): {n_bits} (Total inputs: {2**n_bits})")
    print(f"Hash Output Size (m): {m_bits} bits")
    print("-" * 55)

    print(
        f"{'Input (Binary)':<16} | "
        f"{'Input (Dec)':<12} | "
        f"{'Hash Output (Binary)':<20}"
    )
    print("-" * 55)

    # Store each input and its hash in a dictionary
    hash_map = {}

    # Evaluate all possible inputs
    for x_val in range(2**n_bits):

        # Convert the input integer into individual bits
        bits = [(x_val >> i) & 1 for i in range(n_bits)]

        hash_bits = []

        for k in range(m_bits):

            # 1. Linear mixing (XOR)
            h_k = 0

            for i in range(n_bits):
                if i % m_bits == k:
                    h_k ^= bits[i]

            # 2. Non-linear mixing (AND)
            if n_bits >= 2:
                non_linear_term = bits[0] & bits[n_bits - 1]

                if k % 2 == 1:
                    h_k ^= non_linear_term

            hash_bits.append(h_k)

        # Reassemble hash bits into an integer
        hash_val = 0

        for idx, bit in enumerate(hash_bits):
            hash_val |= (bit << idx)

        # NEW: Save the input and its hash
        hash_map[x_val] = hash_val

        # Convert input and hash to binary for display
        bin_x = bin(x_val)[2:].zfill(n_bits)
        bin_h = bin(hash_val)[2:].zfill(m_bits)

        print(f"|{bin_x}>           | {x_val:<12} | |{bin_h}>")

    print("-" * 55)

    # NEW: Return all stored mappings
    return hash_map


if __name__ == "__main__":
    try:
        n = int(input("Enter input bit size (n, between 2 and 8): "))
        m = int(input("Enter hash output size (m bits): "))

        hash_map = create_toy_hash_system(n, m)

        print(f"\nTotal stored mappings: {len(hash_map)}")

    except ValueError as e:
        print(f"Invalid input: {e}")
