# PyCircleSim

![Header](img/header-pycirclesim.png)

__PyCircleSim__ is a Python framework for simulating and analyzing the Circles protocol through agent-based modeling.

## Table of Contents

- [Introduction](#introduction)
- [Installation & Setup](#installation--setup)
- [Project Structure](#project-structure)
- [Framework Components](#framework-components)
- [Configuration](#configuration)
- [Running Simulations](#running-simulations)
- [Analysis & Monitoring](#analysis--monitoring)
- [Troubleshooting](#troubleshooting)

## Introduction

Circles is a decentralized Universal Basic Income (UBI) protocol built on Gnosis Chain. Each participant mints their own personal currency token, with value flowing through trust relationships between participants.

PyCircleSim enables:
- Creating test networks with multiple types of agents
- Modeling realistic trust relationship formation
- Simulating token minting and trading behaviors
- Collecting comprehensive data for analysis
- Testing different scenarios and configurations

## Installation & Setup

### Prerequisites

- Python 3.10+
- Git
- Foundry for blockchain simulation
- GnosisScan API key

### Step-by-Step Setup

1. Install Foundry:
```bash
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

2. Install Ape and plugins:
```bash 
pip install eth-ape
ape plugins install solidity foundry etherscan
```

3. Clone and install PyCircleSim:
```bash
git clone <repository-url>
cd pyCircleSim

python -m venv circles_env
source circles_env/bin/activate  # On Windows: circles_env\Scripts\activate

pip install -e .
```

4. Configure environment:
```bash
# Create .env file with:
GNOSISSCAN_API_KEY=your_api_key_here
```

5. Create Ape config (`ape-config.yaml`):
```yaml
name: Circles-Chain-Simulator

plugins:
  - name: solidity
  - name: foundry
  - name: etherscan

foundry:
  fork:
    gnosis:
      mainnet_fork:
        upstream_provider: https://rpc.gnosischain.com

gnosis:
  default_network: mainnet-fork
  mainnet_fork:
    default_provider: foundry
```

### Contract Interface Setup

1. Fetch ABIs:
```bash
python src/protocols/abis/fetch_abis.py
```

2. Generate contract interfaces:
```bash
python src/contract_generator/generator.py src/protocols/abis/rings/0x3D61f0A272eC69d65F5CFF097212079aaFDe8267.json
```

3. Generate action types:
```bash
python src/framework/agents/actions_generator/generate_actions.py
```

## Project Structure

### Overview

PyCircleSim is organized into a clean, modular structure that separates core framework components from protocol-specific implementations and simulation configurations.

```
pyCircleSim/
├── scripts/                      # Entry point scripts
└── src/                         # Main source code
    ├── contract_generator/      # Contract interface generation
    ├── framework/              # Core framework components
    ├── protocols/              # Protocol implementations
    └── simulations/            # Simulation configurations
```

### Detailed Structure

#### Contract Generator
```
contract_generator/
├── generator.py                 # Main generator script
└── templates/                   # Jinja2 templates
    ├── basic_strategies.py.j2   # Strategy template
    ├── client.py.j2            # Client interface template
    ├── handler.py.j2           # Action handler template
    └── interface_init.py.j2    # Init file template
```

#### Framework Components
```
framework/
├── agents/                      # Agent system
│   ├── action_registry.py       # Action registration
│   ├── actions_generator/       # Action type generation
│   ├── agent_manager.py        # Agent coordination
│   ├── balance.py              # Balance tracking
│   ├── base_agent.py           # Base agent class
│   ├── profile.py              # Agent profiles
│   └── types.py                # Type definitions
├── core/                       # Core simulation
│   ├── network_builder.py      # Network initialization
│   └── network_evolver.py      # Network evolution
├── data/                       # Data collection
│   ├── collector.py            # Main collector
│   ├── duckdb/                 # Database components
│   │   ├── queries/            # SQL queries
│   │   └── schema/             # Database schema
│   └── event_logging/          # Event system
└── logging/                    # Logging system
```

#### Protocol Implementation
```
protocols/
├── abis/                       # Contract ABIs
│   ├── balancer_v2/           # Balancer V2 ABIs
│   ├── balancer_v3/           # Balancer V3 ABIs
│   ├── circles/               # Circles Protocol ABIs
│   ├── fjord/                 # Fjord Protocol ABIs
│   ├── rings/                 # Rings Protocol ABIs
│   └── tokens/                # Token ABIs
├── handler_strategies/         # Protocol strategies
│   ├── base.py                # Base strategy
│   ├── ringshub/              # Rings strategies
│   └── wxdai/                 # WXDAI strategies
└── interfaces/                # Protocol interfaces
    ├── ringshub/              # Rings interface
    └── wxdai/                 # WXDAI interface
```

#### Database Structure
```
duckdb/
├── queries/                    # SQL queries
│   ├── get_agent_profile.sql  # Agent queries
│   ├── get_event_stats.sql    # Event statistics
│   ├── get_events.sql         # Event retrieval
│   ├── insert_agent.sql       # Agent insertion
│   └── insert_event.sql       # Event logging
└── schema/                    # Database schema
    ├── agent_actions.up.sql   # Actions table
    ├── agents.up.sql          # Agents table
    ├── events.up.sql          # Events table
    └── network_stats.up.sql   # Statistics table
```

## Framework Components

### 1. Agent System
- BaseAgent: Foundation for network participants
- Agent Profiles: Behavior and constraint definitions
- Action Handlers: Contract interaction management
- Agent Manager: Agent coordination and tracking
- Action Registry: Available action catalog

### 2. Data Collection System
- Event Logger: Comprehensive event tracking
- Balance Tracker: Token balance monitoring
- Data Collector: Central storage system
- Event Handler: Contract event processing

### 3. Network Evolution
- Network Builder: Initial network construction
- Network Evolver: Ongoing network changes

### 4. Strategy System
- Base Strategy: Strategy foundation interface
- Basic Strategies: Default behaviors
- Sybil Strategies: Attack pattern implementations
- Custom Strategies: Specialized behavior framework

### 5. Protocol Interfaces
- Contract Clients: Blockchain interaction layer
- Event Decoders: Event processing system
- Transaction Management: Transaction handling system

### 6. Configuration System
- Network Configuration: Simulation-wide settings
- Agent Configuration: Agent behavior parameters
- Protocol Configuration: Protocol-specific settings

## Configuration

### Network Configuration
```yaml
size: 20                  # Network size
trust_density: 0.1       # Target trust density
batch_size: 10          # Processing batch size
iterations: 100         # Number of iterations
blocks_per_iteration: 100  # Blocks per iteration
block_time: 5           # Seconds per block

strategies:
  ringshub: 'basic'  # or 'sybil'
  wxdai: 'basic'

gas_limits:
  registerHuman: 500000
  trust: 300000
  registerGroup: 1000000
```

### Agent Configuration
```yaml
agent_distribution:
  honest_user: 10
  group_creator: 1

profiles:
  honest_user:
    description: "Regular network participant"
    base_config:
      target_account_count: 1
      max_daily_actions: 20
      risk_tolerance: 0.3
    available_actions:   
      - action: "ringshub_PersonalMint"
        probability: 0.8
        cooldown_blocks: 2
      - action: "ringshub_Trust"
        probability: 0.5
        cooldown_blocks: 1
```

## Running Simulations

### Basic Usage
```bash
ape run scripts/cli.py simulate rings \
  --network-config config/rings_config.yaml \
  --agent-config config/agent_config.yaml
```

### Advanced Options
```bash
ape run scripts/cli.py simulate rings \
  --network-config config/rings_config.yaml \
  --agent-config config/agent_config.yaml \
  --network-size 100 \
  --batch-size 20 \
  --iterations 500 \
  --blocks-per-iteration 200 \
  --fast-mode
```

Available options:
- `--network-size`: Override network size
- `--batch-size`: Override batch size  
- `--iterations`: Override iteration count
- `--blocks-per-iteration`: Override blocks per iteration
- `--fast-mode/--no-fast-mode`: Toggle database storage

## Analysis & Monitoring

Results are stored in DuckDB (`rings_simulation.duckdb`). Example usage:

```python
from src.framework.data import DataCollector

collector = DataCollector()

# Export to CSV
collector.export_to_csv("analysis_results")

# Get event statistics
stats = collector.get_event_stats(simulation_run_id=1)

# Query specific events
events = collector.get_events(
    event_name="Trust",
    start_time=datetime(2024, 1, 1),
    limit=1000
)
```

## Troubleshooting

Common issues and solutions:

1. Interface Generation
- Verify GnosisScan API key is valid
- Check ABI file exists and is valid JSON
- Ensure templates directory exists

2. Simulation Startup
- Confirm Foundry is running
- Check Ape configuration
- Verify network fork is accessible

3. Database Issues  
- Check DuckDB file permissions
- Verify SQL schema files exist
- Look for syntax errors in queries

4. Contract Interactions
- Verify gas limits are sufficient
- Check account balances
- Confirm contract ABIs match implementation

For any other issues, check the detailed logs in the console output.

## License

MIT License