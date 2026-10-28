# main.py

import time
from src.hash_functions.toy_hash import toy_hash
from src.classical_attack.birthday_attack import birthday_attack
from src.quantum_grover.grover_search import run_grover_search

def main():
    print("==================================================")
    print("     QUANTUM HASH COLLISION & SEARCH ANALYZER     ")
    print("==================================================")
    
    # Step 1: Prompt the user for the bit-width (2 to 8 bits)
    try:
        user_input = input("Enter bit-width for the hash space (2 to 8): ").strip()
        n_bits = int(user_input)
        if not (2 <= n_bits <= 8):
            raise ValueError("Bit-width out of range.")
    except ValueError:
        print("Invalid input or out of range! Defaulting to 4 bits.")
        n_bits = 4

    space_size = 1 << n_bits
    print(f"\n[+] Initialized system with {n_bits} bits (Total search space: {space_size} items).")

    # Step 2: Execute and benchmark the Classical Birthday Attack
    print("\n--- [1] Running Classical Birthday Attack ---")
    start_time = time.time()
    classical_res = birthday_attack(n_bits)
    classical_duration = time.time() - start_time
    
    print(f"  -> Queries required : {classical_res['queries']}")
    print(f"  -> Execution Time   : {classical_duration:.6f} seconds")
    print(f"  -> Collision Found  : hash({classical_res['input1']}) == hash({classical_res['input2']}) == {classical_res['hash']}")
    print(f"     (Binaries: {format(classical_res['input1'], f'0{n_bits}b')} and {format(classical_res['input2'], f'0{n_bits}b')})")

    # Step 3: Execute and benchmark Quantum Grover Search
    # We pick a sample input to find its corresponding target hash
    sample_input = 2 if space_size > 2 else 0
    target_hash = toy_hash(sample_input, n_bits)
    
    print(f"\n--- [2] Running Quantum Grover Search ---")
    print(f"  -> Target Preimage  : {sample_input} (Binary: {format(sample_input, f'0{n_bits}b')})")
    print(f"  -> Target Hash      : {target_hash} (Binary: {format(target_hash, f'0{n_bits}b')})")
    
    start_time = time.time()
    quantum_res = run_grover_search(n_bits, target_hash)
    quantum_duration = time.time() - start_time

    print(f"  -> Optimal Iterations: {quantum_res['optimal_iters']}")
    print(f"  -> Execution Time    : {quantum_duration:.6f} seconds")
    
    # Identify the most frequent measurement outcome from the simulation
    best_state = max(quantum_res['counts'], key=quantum_res['counts'].get)
    best_count = quantum_res['counts'][best_state]
    print(f"  -> Top Measured State: |{best_state}> with {best_count}/1024 simulation shots")

    # Step 4: Final Comparison Matrix
    print("\n==================================================")
    print("               PERFORMANCE SUMMARY                ")
    print("==================================================")
    print(f"Bit-width (n)         : {n_bits}")
    print(f"Search Space Size (N) : {space_size}")
    print(f"Classical Queries     : {classical_res['queries']} (Expected ~O(sqrt(N)))")
    print(f"Quantum Iterations    : {quantum_res['optimal_iters']} (Expected ~O(sqrt(N)))")
    print("==================================================")


if __name__ == "__main__":
    main()