# Quantum-Grover-Hash-Security

A Qiskit-based simulation and analysis of Grover's algorithm for evaluating cryptographic hash security through classical vs. quantum search experiments and interactive visualizations.

## 📌 About the Project

This project explores how Grover's quantum search algorithm can be used to search for inputs that produce a selected hash value. It combines classical hash searching with quantum circuit simulation to study search behavior and measurement results.

The project uses a toy hash function and a limited search space for educational experimentation.

## 🎯 Objectives

- Understand the basic working of Grover's search algorithm.
- Implement a toy hash function for experimental analysis.
- Search for inputs matching a selected target hash.
- Simulate quantum search circuits using Qiskit.
- Study how Grover iterations affect the probability of finding matching inputs.
- Compare classical and quantum search behavior using graphs.

## ✨ Key Features

- Classical hash computation and search.
- Hash preimage search experiments.
- Grover's algorithm simulation using quantum circuits.
- Target hash matching and multiple matching-input experiments.
- Measurement probability and result analysis.
- Interactive Streamlit interface.
- Graphs and visualizations for experimental results.

## 🛠️ Technologies Used

- **Python** — Core implementation
- **Qiskit** — Quantum circuit simulation
- **Streamlit** — Interactive frontend
- **Pandas** — Data handling
- **Plotly and Matplotlib** — Visualization
- **Jupyter Notebook** — Experiments and testing

## 📂 Project Structure

```text
Quantum-Grover-Hash-Security/
├── notebooks/
│   ├── 1_intro_circuit.ipynb
│   ├── 2_test_oracle.ipynb
│   ├── 3_test_diffusion.ipynb
│   ├── 4_test_grover_simulation.ipynb
│   ├── 5_classical_vs_quantum.ipynb
│   ├── 6_matching_inputs_experiment.ipynb
│   └── 7_final_project_testing.ipynb
├── results/
├── src/
│   ├── classical_attack/
│   ├── hash_functions/
│   └── quantum_grover/
├── app.py
├── main.py
├── .gitignore
└── README.md
```

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Thanushree-19/Quantum-Grover-Hash-Security.git
cd Quantum-Grover-Hash-Security
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install the dependencies

Install the packages required by the project:

```bash
pip install qiskit streamlit pandas plotly matplotlib jupyter
```

### 4. Run the Streamlit application

```bash
streamlit run app.py
```

If your project uses additional dependencies, install those too before running the application.

## 📊 Experiments and Analysis

The project investigates:

- Classical search for inputs matching a target hash.
- Construction and simulation of Grover search circuits.
- Experiments involving multiple matching inputs.
- Changes in measurement probabilities across Grover iterations.
- Graph-based comparison of classical and quantum search behavior.

## 🔬 Scope and Limitations

This is an educational simulation using a toy hash function and a limited search space. The results demonstrate quantum search concepts; they do not establish that modern cryptographic hash functions can be practically broken using current quantum computers.

## 🔮 Future Enhancements

- Test additional search-space sizes.
- Compare different numbers of Grover iterations.
- Improve the interactive experiment controls.
- Extend the analysis of matching inputs and search probabilities.
- Explore the impact of oracle design on simulation results.

## 👩‍💻 Authors

-**Thanushree M N**
-**Sai Varsha K S**
-**Sana Mariyam**
-**Raina Zohreen**

##🤝 Contributions

Developed collaboratively as a Computer Science Engineering project.

## 📄 License

No license has currently been specified for this repository. Please contact the author for permission to reuse or distribute the code.
