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

- **Data Collection**: Enhanced event tracking system with:
  - Unified event logging
  - Full transaction decoding
  - Comprehensive state tracking
  - Efficient DuckDB storage

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
- GnosisScan API key for contract ABIs

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

4. Create environment configuration:
```bash
cp .env.example .env
# Edit .env to add your GNOSISSCAN_API_KEY
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

The project uses a modular architecture organized as follows:

```
pyCircleSim/
├── scripts/
│   └── rings.py               # Main simulation script
└── src/
    ├── framework/
    │   ├── config/
    │   │   ├── rings_config.yaml      # Network configuration
    │   │   └── agent_config.yaml      # Agent configuration
    │   ├── agents/             # Agent system components
    │   │   ├── __init__.py
    │   │   ├── agent_manager.py
    │   │   ├── base_agent.py
    │   │   └── types.py
    │   ├── core/              # Core simulation components
    │   │   ├── handlers/
    │   │   ├── network_actions.py
    │   │   ├── network_builder.py
    │   │   ├── network_component.py
    │   │   └── network_evolver.py
    │   ├── data/              # Data collection system
    │   │   ├── duckdb/
    │   │   ├── event_logging/
    │   │   ├── base_collector.py
    │   │   └── circles_collector.py
    │   └── logging/           # Logging configuration
    └── protocols/
        ├── abis/              # Contract ABIs
        │   ├── rings/
        │   ├── fjord/
        │   └── fetch_abis.py
        ├── common/            # Shared utilities
        ├── rings/             # Rings protocol
        ├── fjord/             # Fjord protocol
        └── __init__.py
```

## Configuration System

### Network Configuration (rings_config.yaml)

The network configuration controls simulation-wide parameters:
```yaml
size: 20                 # Network size
trust_density: 0.1       # Target trust density
batch_size: 10          # Processing batch size
iterations: 3           # Number of iterations
blocks_per_iteration: 100  # Blocks per iteration
block_time: 5           # Seconds per block

gas_limits:
  register_human: 500000
  trust: 300000
  mint: 300000
  transfer: 300000
```

### Agent Configuration (agent_config.yaml)

The agent configuration defines participant behaviors:
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

## Agent System

### Agent Profiles

Custom agents can be created by extending the base agent:

```python
from src.framework.agents import BaseAgent, ActionType, AgentProfile

class CustomAgent(BaseAgent):
    def __init__(self, agent_id: str, profile: AgentProfile):
        super().__init__(agent_id, profile)
        # Custom initialization
```

### Actions and Behaviors

Actions use dedicated handlers for clean separation of concerns:

```python
class CustomActionHandler:
    def __init__(self, client, chain, logger):
        self.client = client
        self.chain = chain
        self.logger = logger

    def execute(self, agent: BaseAgent) -> bool:
        try:
            # Implementation
            return True
        except Exception as e:
            self.logger.error(f"Action failed: {e}")
            return False
```

## Data Collection System

### Database Schema

The new unified event logging system uses a simplified schema:

```sql
CREATE TABLE events (
    simulation_run_id INTEGER NOT NULL,
    event_name VARCHAR NOT NULL,
    block_number BIGINT NOT NULL,
    block_timestamp TIMESTAMP NOT NULL,
    transaction_hash VARCHAR NOT NULL,
    contract_address VARCHAR NOT NULL,
    topics VARCHAR,
    event_data VARCHAR,
    decoded_values VARCHAR,
    FOREIGN KEY(simulation_run_id) REFERENCES simulation_runs(run_id)
);
```

### Using the Data Collector

The data collector provides a straightforward interface:

```python
from src.framework.data import CirclesDataCollector

collector = CirclesDataCollector()

# Start a simulation run
run_id = collector.start_simulation_run(
    parameters={"network_size": 1000},
    description="Test simulation"
)

# Record events
collector.record_transaction_events(tx)

# End simulation
collector.end_simulation_run()
```

## Running Simulations

### Setting Up Contracts

First, fetch the required contract ABIs:

```bash
# Set up your GnosisScan API key in .env
python src/protocols/abis/fetch_abis.py
```

### Basic Usage

Run a simulation with default settings:

```bash
ape run rings simulate \
  --rings-config config/rings_config.yaml \
  --agent-config config/agent_config.yaml
```

### Advanced Options

Override configuration via command line:
```bash
ape run rings simulate \
  --rings-config config/rings_config.yaml \
  --agent-config config/agent_config.yaml \
  --network-size 1000 \
  --trust-density 0.2 \
  --fast-mode
```

Available options:
- `--network-size`: Number of agents to create
- `--trust-density`: Target trust network density
- `--batch-size`: Number of operations per batch
- `--iterations`: Number of simulation cycles
- `--blocks-per-iteration`: Blockchain blocks per cycle
- `--fast-mode/--no-fast-mode`: Toggle database storage

## Analyzing Results

Results are stored in the DuckDB database and can be analyzed using SQL or exported to CSV:

```python
# Export results
collector.export_to_csv("analysis_results")

# Query events
events = collector.get_events(
    event_name="Transfer",
    start_time=datetime(2024, 1, 1),
    limit=1000
)
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.