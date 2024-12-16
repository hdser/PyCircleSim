![Header](img/header-pycirclesim.png)

__PyCircleSim__ is a Python framework for simulating and analyzing the Circles protocol through agent-based modeling. By simulating how different types of participants interact within the Circles ecosystem, researchers and developers can better understand the dynamics of this decentralized Universal Basic Income (UBI) system.

## Table of Contents

- [Introduction and Background](#introduction-and-background)
  - [Understanding Circles Protocol](#understanding-circles-protocol)
  - [Why Simulation Matters](#why-simulation-matters)
- [Key Features](#key-features)
- [Setup and Installation](#setup-and-installation)
  - [Prerequisites](#prerequisites)
  - [Installation Steps](#installation-steps)
  - [Plugin Configuration](#plugin-configuration)
- [Project Structure](#project-structure)
- [Configuration System](#configuration-system)
  - [Network Configuration](#network-configuration)
  - [Agent Configuration](#agent-configuration)
- [Agent System](#agent-system)
  - [Agent Profiles](#agent-profiles)
  - [Actions and Behaviors](#actions-and-behaviors)
  - [Trust Dynamics](#trust-dynamics)
- [Data Collection System](#data-collection-system)
  - [Database Schema](#database-schema)
  - [Using the Data Collector](#using-the-data-collector)
  - [Analysis Capabilities](#analysis-capabilities)
- [Running Simulations](#running-simulations)
  - [Basic Usage](#basic-usage)
  - [Advanced Options](#advanced-options)
  - [Monitoring Progress](#monitoring-progress)
- [Analyzing Results](#analyzing-results)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Introduction and Background

### Understanding Circles Protocol

Circles is a decentralized Universal Basic Income (UBI) protocol built on Gnosis Chain. Each participant in the Circles ecosystem can mint their own personal currency token. These personal tokens are made valuable through trust relationships – when participants trust each other's currencies, they effectively agree to accept each other's tokens as payment.

The system creates a web of trust where value flows through social connections. For example, if Alice trusts Bob's tokens and Bob trusts Carol's tokens, Alice can indirectly accept Carol's tokens through this trust path, even without directly trusting Carol.

### Why Simulation Matters

Understanding how such a complex system evolves requires sophisticated simulation tools. Key questions we can explore through simulation include:

- How does the trust network grow and evolve over time?
- What patterns emerge in token distribution and velocity?
- How do different types of participants affect system stability?
- What are the effects of different trust strategies?

PyCircleSim enables researchers and developers to explore these questions through:
- Creating test networks with multiple types of participants
- Modeling realistic trust relationship formation
- Simulating token minting and trading behaviors
- Collecting comprehensive data for analysis
- Testing different scenarios and configurations

## Key Features

- **Agent-Based Modeling**: A flexible system where different types of participants (agents) can be configured with distinct behaviors and strategies.

- **Trust Network Simulation**: Realistic modeling of trust relationship formation, including:
  - Directional trust connections
  - Trust limits and expiry
  - Trust path discovery
  - Network density evolution

- **Token Economics**: Complete implementation of Circles token mechanics:
  - Personal token minting
  - Token transfers along trust paths
  - Group token creation
  - Token velocity tracking

- **Data Collection**: Comprehensive event and state tracking:
  - Registration events
  - Trust relationship changes
  - Token movements
  - Network statistics

- **Analysis Tools**: Built-in capabilities for analyzing:
  - Network growth patterns
  - Trust network properties
  - Token distribution metrics
  - System stability indicators

## Setup and Installation

### Prerequisites

Before installation, ensure you have:
- Python 3.10 or higher
- Git
- pip package manager
- DuckDB for data storage
- Foundry for blockchain simulation

### Installation Steps

1. First, install Foundry for local blockchain simulation:
```bash
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

2. Install Ape and required plugins:
```bash
pip install eth-ape
ape plugins install solidity foundry etherscan
```

3. Clone and set up PyCircleSim:
```bash
git clone https://github.com/yourusername/pyCircleSim.git
cd pyCircleSim

python -m venv circles_ape
source circles_ape/bin/activate  # On Windows use: circles_ape\Scripts\activate

pip install -e .
```

### Plugin Configuration

Configure Ape by creating an `ape-config.yaml` file:
```yaml
name: Circles-Chain-Simulator
plugins:
  - name: solidity
  - name: foundry
  - name: etherscan

foundry:
  host: http://localhost:8545
  fork:
    gnosis:
      mainnet_fork:
        upstream_provider: http://192.168.2.186:8545

gnosis:
  default_network: mainnet-fork
  mainnet_fork:
    default_provider: foundry
```

## Project Structure

The project is organized to separate different concerns:
```
pyCircleSim/
├── rings_network/
│   ├── network_builder.py     # Network creation
│   ├── network_evolver.py     # Time evolution
│   ├── network_analyzer.py    # Analysis tools
│   ├── data_collector.py      # Data management
│   └── config/               
│       ├── rings_config.yaml  # Network settings
│       └── agent_config.yaml  # Agent behaviors
```

## Configuration System

### Network Configuration (rings_config.yaml)

The network configuration controls simulation-wide parameters:
```yaml
size: 20                # Network size
trust_density: 0.1      # Target trust density
batch_size: 10         # Processing batch size
iterations: 3          # Number of iterations
blocks_per_iteration: 100  # Blocks per iteration
block_time: 5          # Seconds per block

gas_limits:
  register_human: 500000
  trust: 300000
  mint: 300000
  transfer: 300000
```

### Agent Configuration (agent_config.yaml)

The agent configuration defines different participant behaviors:
```yaml
simulation_params:
  initial_balance: 100
  welcome_bonus: 200
  min_gas_price: 1000000000

agent_distribution:
  honest_user: 10
  group_creator: 1
  sybil_attacker: 2
  trust_hub: 5

profiles:
  honest_user:
    description: "Regular network participant"
    target_account_count: 1
    max_daily_actions: 20
    risk_tolerance: 0.3
```

## Running Simulations

Since PyCircleSim is built as an Ape plugin, use the following command to run simulations:

```bash
ape run rings simulate \
  --rings-config rings_network/config/rings_config.yaml \
  --agent-config rings_network/config/agent_config.yaml
```

### Advanced Options

You can override configuration parameters via command line:
```bash
ape run rings simulate \
  --rings-config rings_network/config/rings_config.yaml \
  --agent-config rings_network/config/agent_config.yaml \
  --network-size 1000 \
  --trust-density 0.2
```

Available options include:
- `--network-size`: Number of agents to create
- `--trust-density`: Target trust network density
- `--batch-size`: Number of operations per batch
- `--iterations`: Number of simulation cycles
- `--blocks-per-iteration`: Blockchain blocks per cycle

### Monitoring Progress

The simulation provides detailed progress information:
```
Starting simulation with configuration:
Network size: 1,000 agents
Trust density: 0.1
Iterations: 3

Building initial network...
Processing iteration 1/3...
[Statistics follow...]
```

## Analyzing Results

After simulation completion, analyze results using:
```bash
ape run rings analyze
```

Results are stored in timestamped directories:
```
simulation_results/
└── sim_20241216_143022/
    ├── agent_statistics.csv    # Agent behavior data
    ├── iteration_statistics.csv   # Per-iteration metrics
    ├── event_logs.csv         # Chronological events
    ├── network_snapshots.csv  # Network state captures
    └── simulation_metadata.json  # Configuration data
```

## Troubleshooting

Common issues and solutions:

1. **Foundry Connection Errors**:
   - Ensure Foundry is running: `anvil`
   - Verify network settings in ape-config.yaml
   - Check Foundry's sync status

2. **Configuration File Issues**:
   - Use absolute paths if relative paths fail
   - Validate YAML syntax
   - Check file permissions

3. **Out of Gas Errors**:
   - Increase gas limits in configuration
   - Reduce batch sizes
   - Check transaction complexity

4. **Database Errors**:
   - Verify DuckDB write permissions
   - Check available disk space
   - Validate database schema

For additional help:
- Check logs in `rings_simulation.log`
- Review error messages in console output
- Create an issue on GitHub with details

## Contributing

We welcome contributions! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.