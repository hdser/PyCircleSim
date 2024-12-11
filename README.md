# PyCircleSim: Circles Network Simulation Framework

<img src="img/pycirclesim.jpg" alt="pyCircleSim" style="height:400px;width:900px;">

PyCircleSim is a Python framework for simulating and analyzing the Circles protocol. It provides tools for building test networks, evolving system state, and collecting data about token distributions and trust relationships within the Circles ecosystem.

## Introduction

Circles is a decentralized fair form of money built on Gnosis Chain. Each user can mint their own personal currency, which is trusted and traded within their social network. Understanding how such a system evolves over time requires sophisticated simulation tools.

This framework allows researchers and developers to:
- Create test networks with multiple accounts
- Establish trust relationships between accounts
- Simulate the passage of time and token minting
- Track and analyze the evolution of balances and trust relationships
- Export detailed data for further analysis

## System Requirements

- Python 3.10 or higher
- Foundry for local blockchain simulation
- Git
- pip package manager

## Installation

First, ensure you have Foundry installed. If not, install it following the instructions at [getfoundry.sh](https://getfoundry.sh/).

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pyCircleSim.git
cd pyCircleSim
```

2. Create and activate a virtual environment:
```bash
python -m venv circles_ape
source circles_ape/bin/activate  # On Windows use: circles_ape\Scripts\activate
```

3. Install the package in development mode:
```bash
pip install -e .
```

This will automatically install all required dependencies, including:
- eth-ape with recommended plugins
- pandas for data analysis
- other required packages

## Project Structure

```
pyCircleSim/
├── README.md
├── setup.py
├── rings_network/
│   ├── __init__.py
│   ├── network_builder.py    # Network creation and trust setup
│   ├── network_evolver.py    # Time evolution and minting
│   ├── network_analyzer.py   # Analysis tools
│   └── data_collector.py     # Data collection and storage
└── scripts/
    ├── rings.py             # Main simulation script
    └── abi/                 # Contract ABIs
```

## Usage

The framework provides several components that can be used independently or together:

1. Network Building:
```python
from rings_network import NetworkBuilder

builder = NetworkBuilder(RINGS_ADDRESS, ABI_PATH)
builder.build_complete_network()  # Creates a fully connected test network
```

2. Network Evolution:
```python
from rings_network import NetworkEvolver

evolver = NetworkEvolver(RINGS_ADDRESS, ABI_PATH)
evolver.advance_time(100)        # Advance blockchain by 100 blocks
evolver.personal_mint(account)   # Mint tokens for an account
```

3. Data Collection:
```python
from rings_network import DataCollector, NetworkAnalyzer

analyzer = NetworkAnalyzer(RINGS_ADDRESS, ABI_PATH)
collector = DataCollector(analyzer)
collector.collect_state(accounts)     # Record current network state
collector.export_data("results.json") # Save collected data
```

For a complete simulation, use the provided script:
```bash
ape run rings
```

## Data Format

The simulation generates JSON files containing:
- Balance histories for all accounts
- Trust relationship matrices
- Temporal evolution data
- Network statistics

Example data structure:
```json
{
    "timestamps": [...],
    "balance_history": [...],
    "trust_history": [...]
}
```


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

