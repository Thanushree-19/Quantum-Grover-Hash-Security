import math
from collections import Counter

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from qiskit.quantum_info import Statevector

from src.hash_functions.toy_hash import create_toy_hash_system
from src.classical_attack.preimage_search import classical_preimage_search
from src.quantum_grover.grover_search import create_grover_circuit


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Quantum Hash Lab",
    layout="wide",
    initial_sidebar_state="expanded",
)

SHOTS = 4096

st.markdown(
    """
    <style>
    .stApp {
        background-color: #0d1119;
        color: #e6eaf2;
    }

    [data-testid="stSidebar"] {
        background-color: #111722;
        border-right: 1px solid #283142;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: #eef1f8;
    }

    div[data-testid="stMetric"] {
        background-color: #151c29;
        border: 1px solid #293448;
        padding: 14px;
        border-radius: 10px;
    }

    div.stButton > button {
        background-color: #7464b5;
        color: white;
        border: 1px solid #8b7bce;
        border-radius: 7px;
        min-height: 42px;
        font-weight: 600;
    }

    div.stButton > button:hover {
        background-color: #65549f;
        color: white;
        border-color: #a99be7;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #293448;
        border-radius: 8px;
    }

    hr {
        border-color: #293448;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SESSION STATE
# =========================================================

DEFAULTS = {
    "hash_map": None,
    "generated_config": None,
    "validated_target": None,
    "target_input_signature": None,
    "classical_result": None,
    "grover_result": None,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def to_binary(value, width):
    return format(int(value), f"0{width}b")


def calculate_hash_statistics(hash_map, n_bits, m_bits):
    frequencies = Counter(hash_map.values())

    total_inputs = len(hash_map)
    unique_hashes = len(frequencies)
    collision_hashes = {
        value: count
        for value, count in frequencies.items()
        if count > 1
    }

    collision_pairs = sum(
        count * (count - 1) // 2
        for count in collision_hashes.values()
    )

    return {
        "total_inputs": total_inputs,
        "unique_hashes": unique_hashes,
        "collision_hash_count": len(collision_hashes),
        "collision_pairs": collision_pairs,
        "missing_hashes": (2 ** m_bits) - unique_hashes,
        "frequencies": frequencies,
    }


def create_hash_dataframe(hash_map, n_bits, m_bits):
    rows = []

    for input_value, hash_value in sorted(hash_map.items()):
        rows.append({
            "Input (decimal)": input_value,
            "Input (binary)": to_binary(input_value, n_bits),
            "Hash (decimal)": hash_value,
            "Hash (binary)": to_binary(hash_value, m_bits),
        })

    return pd.DataFrame(rows)


def create_collision_dataframe(hash_map, n_bits, m_bits):
    groups = {}

    for input_value, hash_value in hash_map.items():
        groups.setdefault(hash_value, []).append(input_value)

    rows = []

    for hash_value, inputs in sorted(groups.items()):
        if len(inputs) > 1:
            rows.append({
                "Hash (binary)": to_binary(hash_value, m_bits),
                "Hash (decimal)": hash_value,
                "Matching inputs": ", ".join(
                    to_binary(value, n_bits)
                    for value in sorted(inputs)
                ),
                "Number of inputs": len(inputs),
                "Collision pairs": len(inputs) * (len(inputs) - 1) // 2,
            })

    return pd.DataFrame(
        rows,
        columns=[
            "Hash (binary)",
            "Hash (decimal)",
            "Matching inputs",
            "Number of inputs",
            "Collision pairs",
        ],
    )


def calculate_grover_probabilities(
    hash_map,
    target_hash,
    n_bits,
    iterations,
):
    circuit = create_grover_circuit(
        hash_map=hash_map,
        target_hash=target_hash,
        n_bits=n_bits,
        iterations=iterations,
    )

    # Remove measurements to obtain the quantum state.
    state_circuit = circuit.remove_final_measurements(inplace=False)

    state = Statevector.from_instruction(state_circuit)
    probabilities = np.asarray(state.probabilities(), dtype=float)

    matching_inputs = [
        input_value
        for input_value, hash_value in hash_map.items()
        if hash_value == target_hash
    ]

    success_probability = float(
        sum(probabilities[input_value] for input_value in matching_inputs)
    )

    return circuit, probabilities, success_probability, matching_inputs


def ideal_grover_probability(n_inputs, n_matches, iterations):
    if n_matches == 0:
        return 0.0

    if n_matches >= n_inputs:
        return 1.0

    theta = math.asin(math.sqrt(n_matches / n_inputs))

    return math.sin((2 * iterations + 1) * theta) ** 2


def parse_target_hash(target_text, notation, m_bits):
    target_text = target_text.strip()

    if not target_text:
        raise ValueError("Enter a target hash first.")

    if notation == "Binary":
        if any(character not in "01" for character in target_text):
            raise ValueError("A binary hash can contain only 0 and 1.")

        if len(target_text) > m_bits:
            raise ValueError(
                f"The hash must contain at most {m_bits} bits."
            )

        target_value = int(target_text, 2)

    else:
        if not target_text.isdigit():
            raise ValueError("Enter a valid non-negative decimal integer.")

        target_value = int(target_text)

    if not 0 <= target_value < 2 ** m_bits:
        raise ValueError(
            f"The target must be between 0 and {(2 ** m_bits) - 1}."
        )

    return target_value


# =========================================================
# HEADER
# =========================================================

st.title("Quantum Hash Lab")

st.caption(
    "Explore toy hash functions, collision patterns, classical preimage "
    "search, and Grover's quantum search."
)

st.divider()


# =========================================================
# SIDEBAR: USER SETTINGS
# =========================================================

with st.sidebar:
    st.subheader("Experiment Settings")

    st.caption("Enter the hash system configuration.")

    n_bits = st.number_input(
        "Input size (bits)",
        min_value=2,
        max_value=8,
        value=None,
        placeholder="Choose 2–8 bits",
        step=1,
        key="input_bits",
    )

    m_bits = st.number_input(
        "Hash output size (bits)",
        min_value=1,
        max_value=16,
        value=None,
        placeholder="Enter output bits",
        step=1,
        key="output_bits",
    )

    st.divider()

    st.caption(f"Measurement shots: **{SHOTS:,}**")
    st.caption("Shots are fixed and cannot be changed.")

    generate_clicked = st.button(
        "Generate Hashes",
        use_container_width=True,
    )

    if generate_clicked:
        if n_bits is None or m_bits is None:
            st.error("Enter both input size and hash output size.")
        else:
            try:
                with st.spinner("Generating hash values..."):
                    generated_map = create_toy_hash_system(
                        int(n_bits),
                        int(m_bits),
                    )

                st.session_state.hash_map = generated_map
                st.session_state.generated_config = (
                    int(n_bits),
                    int(m_bits),
                )

                st.session_state.validated_target = None
                st.session_state.target_input_signature = None
                st.session_state.classical_result = None
                st.session_state.grover_result = None

                st.success("Hash values generated.")

            except Exception as error:
                st.error(f"Could not generate hashes: {error}")


# =========================================================
# VERIFY GENERATED CONFIGURATION
# =========================================================

hash_map = st.session_state.hash_map
generated_config = st.session_state.generated_config

current_config = (
    (int(n_bits), int(m_bits))
    if n_bits is not None and m_bits is not None
    else None
)

config_is_current = (
    hash_map is not None
    and generated_config == current_config
)

if hash_map is not None and not config_is_current:
    st.warning(
        "Your settings differ from the generated hash system. "
        "Click **Generate Hashes** to create a new system using these settings."
    )


# =========================================================
# GENERATED HASHES AND AUTOMATIC ANALYSIS
# =========================================================

if config_is_current:
    n_bits = int(n_bits)
    m_bits = int(m_bits)

    stats = calculate_hash_statistics(hash_map, n_bits, m_bits)

    st.header("1. Generated Hash Values")

    st.caption(
        f"{n_bits}-bit inputs mapped to {m_bits}-bit hash outputs."
    )

    metric1, metric2, metric3, metric4 = st.columns(4)

    metric1.metric("Input combinations", stats["total_inputs"])
    metric2.metric("Unique hash outputs", stats["unique_hashes"])
    metric3.metric("Hashes with collisions", stats["collision_hash_count"])
    metric4.metric("Collision pairs", stats["collision_pairs"])

    hash_df = create_hash_dataframe(hash_map, n_bits, m_bits)

    st.dataframe(
        hash_df,
        use_container_width=True,
        hide_index=True,
    )

    csv_data = hash_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Hash Table (CSV)",
        data=csv_data,
        file_name="generated_hash_values.csv",
        mime="text/csv",
    )

    # -----------------------------------------------------
    # HASH DISTRIBUTION
    # -----------------------------------------------------

    st.divider()
    st.header("2. Hash Distribution")

    st.caption(
        "This graph shows how many inputs produce each observed hash value."
    )

    distribution_df = pd.DataFrame([
        {
            "Hash (binary)": to_binary(hash_value, m_bits),
            "Hash (decimal)": hash_value,
            "Number of inputs": count,
        }
        for hash_value, count in sorted(stats["frequencies"].items())
    ])

    if 2 ** m_bits > 512:
        st.info(
            "The hash output space is large. The graph displays observed "
            "hash values only, rather than every possible output."
        )

    distribution_fig = px.bar(
        distribution_df,
        x="Hash (binary)",
        y="Number of inputs",
        hover_data=["Hash (decimal)"],
        labels={
            "Hash (binary)": "Hash output",
            "Number of inputs": "Input count",
        },
        title="Frequency of Hash Outputs",
    )

    distribution_fig.update_layout(
        template="plotly_dark",
        height=420,
        showlegend=False,
        xaxis_title="Hash output (binary)",
        yaxis_title="Number of inputs",
    )

    st.plotly_chart(distribution_fig, use_container_width=True)

    # -----------------------------------------------------
    # COLLISION ANALYSIS
    # -----------------------------------------------------

    st.divider()
    st.header("3. Collision Analysis")

    st.caption(
        "A collision occurs when two or more different inputs produce the same hash."
    )

    collision_df = create_collision_dataframe(
        hash_map,
        n_bits,
        m_bits,
    )

    col_left, col_right = st.columns([1.1, 1])

    with col_left:
        st.subheader("Collision Details")

        if collision_df.empty:
            st.success("No collisions were found in this generated mapping.")
        else:
            st.dataframe(
                collision_df,
                use_container_width=True,
                hide_index=True,
            )

    with col_right:
        st.subheader("Collision Counts")

        if collision_df.empty:
            st.info("The collision graph will appear if collisions exist.")
        else:
            collision_fig = px.bar(
                collision_df,
                x="Hash (binary)",
                y="Number of inputs",
                hover_data=[
                    "Hash (decimal)",
                    "Collision pairs",
                    "Matching inputs",
                ],
                labels={
                    "Hash (binary)": "Colliding hash",
                    "Number of inputs": "Inputs producing this hash",
                },
                title="Inputs per Colliding Hash",
            )

            collision_fig.update_layout(
                template="plotly_dark",
                height=400,
                showlegend=False,
            )

            st.plotly_chart(
                collision_fig,
                use_container_width=True,
            )

    st.caption(
        f"Possible hash outputs: {2 ** m_bits:,} · "
        f"Outputs not produced by any input: {stats['missing_hashes']:,}"
    )

    # =====================================================
    # TARGET HASH SEARCH
    # =====================================================

    st.divider()
    st.header("4. Find a Target Hash")

    st.write(
        "Enter a hash value manually. The application will check which "
        "inputs produce that hash."
    )

    target_col, notation_col, check_col = st.columns([2, 1, 1])

    with target_col:
        target_text = st.text_input(
            "Target hash",
            placeholder=(
                f"Enter a {m_bits}-bit binary hash"
            ),
            key="target_hash_input",
        )

    with notation_col:
        notation = st.radio(
            "Input format",
            options=["Binary", "Decimal"],
            horizontal=True,
            key="target_hash_notation",
        )

    with check_col:
        st.write("")
        st.write("")
        check_clicked = st.button(
            "Check Target Hash",
            use_container_width=True,
        )

    target_signature = (
        target_text.strip(),
        notation,
        generated_config,
    )

    if (
        st.session_state.target_input_signature is not None
        and st.session_state.target_input_signature != target_signature
    ):
        st.session_state.validated_target = None
        st.session_state.classical_result = None
        st.session_state.grover_result = None

    if check_clicked:
        try:
            target_value = parse_target_hash(
                target_text,
                notation,
                m_bits,
            )

            matches = [
                input_value
                for input_value, hash_value in hash_map.items()
                if hash_value == target_value
            ]

            st.session_state.validated_target = {
                "target": target_value,
                "matches": matches,
            }

            st.session_state.target_input_signature = target_signature
            st.session_state.classical_result = None
            st.session_state.grover_result = None

        except ValueError as error:
            st.session_state.validated_target = None
            st.session_state.target_input_signature = target_signature
            st.session_state.classical_result = None
            st.session_state.grover_result = None
            st.error(str(error))

    validated = st.session_state.validated_target

    if (
        validated is not None
        and st.session_state.target_input_signature == target_signature
    ):
        target_value = validated["target"]
        matches = validated["matches"]

        st.markdown("#### Target Hash Result")

        target_metric, count_metric = st.columns(2)

        target_metric.metric(
            "Target hash (binary)",
            to_binary(target_value, m_bits),
        )

        count_metric.metric(
            "Matching inputs",
            len(matches),
        )

        if matches:
            st.success("Preimage found.")

            match_df = pd.DataFrame([
                {
                    "Matching input (decimal)": input_value,
                    "Matching input (binary)": to_binary(
                        input_value,
                        n_bits,
                    ),
                    "Hash (decimal)": target_value,
                    "Hash (binary)": to_binary(
                        target_value,
                        m_bits,
                    ),
                }
                for input_value in matches
            ])

            st.dataframe(
                match_df,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.warning(
                "No preimage found. No input in the generated mapping "
                "produces this target hash. Classical and Grover searches "
                "cannot find a preimage that does not exist in this mapping."
            )

        # =================================================
        # CLASSICAL SEARCH
        # =================================================

        st.divider()
        st.header("5. Classical Search")

        st.write(
            "Classical search checks the generated mapping for inputs "
            "matching the target hash."
        )

        if st.button(
            "Run Classical Search",
            use_container_width=True,
        ):
            try:
                classical_matches = classical_preimage_search(
                    hash_map,
                    target_value,
                )

                st.session_state.classical_result = {
                    "target": target_value,
                    "matches": classical_matches,
                    "queries": len(hash_map),
                }

            except Exception as error:
                st.error(f"Classical search failed: {error}")

        classical_result = st.session_state.classical_result

        if (
            classical_result is not None
            and classical_result["target"] == target_value
        ):
            classical_matches = classical_result["matches"]

            st.success("Classical search completed.")

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Inputs checked",
                f"{classical_result['queries']:,}",
            )

            c2.metric(
                "Matches found",
                len(classical_matches),
            )

            c3.metric(
                "Target hash",
                to_binary(target_value, m_bits),
            )

            if classical_matches:
                st.write(
                    "Matching inputs:",
                    ", ".join(
                        to_binary(value, n_bits)
                        for value in classical_matches
                    ),
                )
            else:
                st.info("Classical search found no matching input.")

        # =================================================
        # GROVER SEARCH
        # =================================================

        st.divider()
        st.header("6. Grover Quantum Search")

        st.write(
            "Run Grover's algorithm on the generated hash mapping. "
            "Choose the number of Grover iterations below."
        )

        iterations = st.number_input(
            "Grover iterations",
            min_value=0,
            max_value=100,
            value=None,
            placeholder="Enter iteration count",
            step=1,
            key="grover_iterations",
        )

        st.caption(
            f"Measurement shots are fixed at {SHOTS:,}. "
            "The displayed sampled counts are generated from the ideal "
            "statevector probabilities, not from quantum hardware."
        )

        if st.button(
            "Run Grover Search",
            use_container_width=True,
        ):
            if iterations is None:
                st.error("Enter the number of Grover iterations.")
            elif not matches:
                st.error(
                    "Grover search requires at least one matching input. "
                    "Choose a target hash that exists in the generated mapping."
                )
            else:
                try:
                    with st.spinner("Simulating Grover's algorithm..."):
                        (
                            circuit,
                            probabilities,
                            success_probability,
                            grover_matches,
                        ) = calculate_grover_probabilities(
                            hash_map=hash_map,
                            target_hash=target_value,
                            n_bits=n_bits,
                            iterations=int(iterations),
                        )

                        rng = np.random.default_rng()

                        sampled_indices = rng.choice(
                            len(probabilities),
                            size=SHOTS,
                            p=probabilities,
                        )

                        sampled_counts = Counter(
                            int(index)
                            for index in sampled_indices
                        )

                        sampled_successes = sum(
                            sampled_counts.get(input_value, 0)
                            for input_value in grover_matches
                        )

                        sampled_success_probability = (
                            sampled_successes / SHOTS
                        )

                        st.session_state.grover_result = {
                            "target": target_value,
                            "iterations": int(iterations),
                            "circuit": circuit,
                            "probabilities": probabilities,
                            "success_probability": success_probability,
                            "matches": grover_matches,
                            "sampled_counts": sampled_counts,
                            "sampled_success_probability": (
                                sampled_success_probability
                            ),
                        }

                except Exception as error:
                    st.error(f"Grover simulation failed: {error}")

        grover_result = st.session_state.grover_result

        if (
            grover_result is not None
            and grover_result["target"] == target_value
        ):
            iterations_used = grover_result["iterations"]
            probabilities = grover_result["probabilities"]
            success_probability = grover_result["success_probability"]
            grover_matches = grover_result["matches"]
            sampled_counts = grover_result["sampled_counts"]

            st.success("Grover simulation completed.")

            q1, q2, q3 = st.columns(3)

            q1.metric(
                "Grover iterations",
                iterations_used,
            )

            q2.metric(
                "Exact success probability",
                f"{success_probability * 100:.2f}%",
            )

            q3.metric(
                "Sampled success probability",
                f"{grover_result['sampled_success_probability'] * 100:.2f}%",
            )

            with st.expander("View Grover circuit"):
                st.code(str(grover_result["circuit"].draw(output="text")))

            # ---------------------------------------------
            # PROBABILITY DISTRIBUTION
            # ---------------------------------------------

            st.subheader("Quantum Measurement Probability")

            probability_df = pd.DataFrame({
                "Input (binary)": [
                    to_binary(index, n_bits)
                    for index in range(len(probabilities))
                ],
                "Input (decimal)": range(len(probabilities)),
                "Probability": probabilities,
                "Is target match": [
                    index in grover_matches
                    for index in range(len(probabilities))
                ],
            })

            probability_fig = px.bar(
                probability_df,
                x="Input (binary)",
                y="Probability",
                color="Is target match",
                hover_data=["Input (decimal)"],
                title="Probability of Measuring Each Input",
                labels={
                    "Input (binary)": "Measured input",
                    "Probability": "Measurement probability",
                    "Is target match": "Matches target",
                },
            )

            probability_fig.update_layout(
                template="plotly_dark",
                height=420,
            )

            st.plotly_chart(
                probability_fig,
                use_container_width=True,
            )

            # ---------------------------------------------
            # SAMPLED COUNTS
            # ---------------------------------------------

            st.subheader(
                f"Sampled Measurement Counts ({SHOTS:,} shots)"
            )

            sampled_df = pd.DataFrame([
                {
                    "Input (binary)": to_binary(index, n_bits),
                    "Input (decimal)": index,
                    "Measurements": sampled_counts.get(index, 0),
                    "Is target match": index in grover_matches,
                }
                for index in range(len(probabilities))
            ])

            sampled_fig = px.bar(
                sampled_df,
                x="Input (binary)",
                y="Measurements",
                color="Is target match",
                hover_data=["Input (decimal)"],
                title="Simulated Measurement Counts",
                labels={
                    "Input (binary)": "Measured input",
                    "Measurements": "Number of measurements",
                    "Is target match": "Matches target",
                },
            )

            sampled_fig.update_layout(
                template="plotly_dark",
                height=420,
            )

            st.plotly_chart(
                sampled_fig,
                use_container_width=True,
            )

            # ---------------------------------------------
            # CLASSICAL VS QUANTUM QUERY COMPARISON
            # ---------------------------------------------

            st.divider()
            st.subheader("Classical vs Quantum Search")

            n_inputs = len(hash_map)
            n_matches = len(grover_matches)

            # Classical exhaustive search checks the whole mapping
            # in the worst case.
            classical_queries = n_inputs

            # Grover's iteration count is reported separately from
            # the total number of oracle evaluations.
            grover_oracle_queries = iterations_used

            comparison_df = pd.DataFrame([
                {
                    "Method": "Classical exhaustive search",
                    "Count": classical_queries,
                },
                {
                    "Method": "Grover oracle iterations",
                    "Count": grover_oracle_queries,
                },
            ])

            comparison_fig = px.bar(
                comparison_df,
                x="Method",
                y="Count",
                title="Search Work Comparison",
                text="Count",
                labels={
                    "Method": "Search method",
                    "Count": "Count",
                },
            )

            comparison_fig.update_traces(textposition="outside")

            comparison_fig.update_layout(
                template="plotly_dark",
                height=400,
                showlegend=False,
            )

            st.plotly_chart(
                comparison_fig,
                use_container_width=True,
            )

            st.caption(
                "Classical count is the worst-case number of input checks. "
                "Grover count is the number of oracle iterations used; "
                "each Grover iteration also includes a diffusion operation. "
                "These counts are not identical measures of total computation."
            )

            # ---------------------------------------------
            # SUCCESS PROBABILITY VS ITERATIONS
            # ---------------------------------------------

            st.subheader("Success Probability vs Grover Iterations")

            max_plot_iterations = min(
                30,
                max(10, iterations_used + 5),
            )

            iteration_values = list(
                range(max_plot_iterations + 1)
            )

            success_values = [
                ideal_grover_probability(
                    n_inputs=n_inputs,
                    n_matches=n_matches,
                    iterations=iteration,
                )
                for iteration in iteration_values
            ]

            iteration_df = pd.DataFrame({
                "Iterations": iteration_values,
                "Success probability": success_values,
            })

            iteration_fig = px.line(
                iteration_df,
                x="Iterations",
                y="Success probability",
                markers=True,
                title="Theoretical Grover Success Probability",
            )

            iteration_fig.add_scatter(
                x=[iterations_used],
                y=[success_probability],
                mode="markers",
                name="Selected iteration",
                marker={"size": 12},
            )

            iteration_fig.update_layout(
                template="plotly_dark",
                height=420,
                yaxis_range=[0, 1],
                xaxis_title="Grover iterations",
                yaxis_title="Success probability",
            )

            st.plotly_chart(
                iteration_fig,
                use_container_width=True,
            )

            st.caption(
                "The curve uses the ideal Grover success-probability formula. "
                "The selected point is calculated from the simulated statevector."
            )

else:
    st.info(
        "Enter the input size and hash output size in the sidebar, "
        "then click **Generate Hashes** to begin."
    )