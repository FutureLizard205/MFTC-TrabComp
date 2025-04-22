# MF - Trabalho de Laboratório Computacional

Este repositório contém o código desenvolvido no âmbito do trabalho de laboratório computacional em Mecânica dos Fluidos, para a cadeira MFTC (Mecânica dos Fluídos e Transferência de Calor) da Universidade de Aveiro.

Ano Letivo: 2024/25

Licença: MIT

This repo contains the code developed for the within the scope of computational laboratory work in Fluid Mechanics, for the MFTC (Fluid Mechanics and Heat Transfer) class at the University of Aveiro.

Academic Year: 2024/25

License: MIT

## 🚀 Getting Started

### ↙️ Clone the Repo

To clone the repo, run:

```bash
git clone https://github.com/FutureLizard205/MFTC-TrabComp.git
```

Alternatively, you can [download the repo's files as a ZIP archive](https://github.com/FutureLizard205/MFTC-TrabComp/archive/refs/heads/main.zip) and extract them to an empty folder.

And open a terminal inside of the repo's folder.

### 🔧 Prerequisites

Make sure you have Python 3.11 - 3.13 installed on your system (other versions haven't been tested, but may work as well). To check the installed version, run:

```bash
python --version
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### ⚙️ Run the Simulation

In order to run the optimization of the first simulation (task 4.1), just run the 4.1.py file:

```bash
python 4.1.py
```

In order to run the optimization of the second simulation (task 4.2, where there is some additional tolerance in the water level, but with added cost), just run the 4.2.py file:

```bash
python 4.2.py
```

Both should output the results of the optimal decision variable found (for the given initial guess 'x0') and the resulting total cost and energy in the terminal, as well as graphs with the water level, costs, energy consumption, pump flow rate and power over time.

#### Custom Simulation

In order to run a singular simulation with a certain decision variable x, edit the x variable in the hydraulicSim.py file and run it:

```bash
python hydraulicSim.py
```