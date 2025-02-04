# PyCircleSim

![PyCircleSim Header](img/header-pycirclesim.png)

**PyCircleSim** is a Python framework for simulating and analyzing the [Circles protocol](https://circles.foundation) through agent-based modeling in realistic scenarios.


## Table of Contents

- [Introduction](#introduction)
- [Key Features](#key-features)
- [Installation & Setup](#installation--setup)
- [Project Structure](#project-structure)
- [Framework Components](#framework-components)
- [Configuration](#configuration)
- [Basic Usage](#basic-usage)
- [Running Simulations](#running-simulations)
- [License](#license)


## Introduction

Circles is a decentralized Universal Basic Income (UBI) protocol built on the Gnosis Chain, where each participant mints their own personal currency token. Token value flows through trust relationships between participants.

**PyCircleSim** enables you to:
- Create test networks with various types of agents.
- Model realistic trust relationship formation.
- Simulate token minting and trading behaviors.
- Collect comprehensive data for analysis.
- Test different scenarios and configurations.


## Key Features

- **Unified Contract Interaction:** Centralizes all contract interactions through a master interface.
- **Configurable Agent Behavior:** Flexible agent profiles and action sequences.
- **Comprehensive Data Collection:** Built-in mechanisms to collect and analyze simulation data.
- **Network Evolution:** Simulate the evolution of decentralized UBI networks.
- **State Management:** Robust state tracking and synchronization across contracts.


## Installation & Setup

### Prerequisites

- Python 3.10+
- Git
- [Foundry](https://github.com/foundry-rs/foundry) for blockchain simulation
- GnosisScan API key

### Step-by-Step Instructions

1. **Install Foundry:**
   ```bash
   curl -L https://foundry.paradigm.xyz | bash
   foundryup
   ```

2. **Install Ape and Required Plugins:**
   ```bash
   pip install eth-ape
   ape plugins install solidity foundry etherscan
   ```

3. **Clone and Install PyCircleSim:**
   ```bash
   git clone <repository-url>
   cd pyCircleSim

   python -m venv circles_env
   source circles_env/bin/activate 

   pip install -e .
   ```

4. **Configure Environment:**
   Create a `.env` file with the following content:
   ```dotenv
   GNOSISSCAN_API_KEY=your_api_key_here
   ```

5. **Create Ape Configuration (`ape-config.yaml`):**
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

1. **Fetch ABIs:**
   ```bash
   python src/protocols/abis/fetch_abis.py
   ```

2. **Generate Contract Interfaces:**
   ```bash
   python src/contract_generator/generator.py src/protocols/abis/rings/0x3D61f0A272eC69d65F5CFF097212079aaFDe8267.json
   ```


## Project Structure

```
pyCircleSim/
├── img/                     # Images and logos
├── config/                  # Configuration files (agent and network)
├── scripts/                 # CLI and helper scripts
├── src/
│   ├── framework/           # Core simulation components
│   │   ├── agents/          # Agent system
│   │   │   ├── agent_manager.py
│   │   │   ├── base_agent.py
│   │   │   └── profile.py
│   │   ├── core/            # Simulation engine
│   │   │   ├── context.py
│   │   │   └── network_evolver.py
│   │   └── data/            # Data collection system
│   │       └── collector.py
│   ├── protocols/           # Protocol-specific implementations
│   │   ├── interfaces/      # Contract interfaces
│   │   │   └── master/      # Master interface components
│   │   │       ├── master_client.py
│   │   │       └── master_handler.py
│   │   └── implementations/ # Protocol implementations
│   │       └── circleshub/  # CirclesHub-specific implementations
│   └── contract_generator/  # Tools for generating contract interfaces
└── README.md                # Project documentation
```


## Framework Components

### Master Interface

The **MasterClient** is the single entry point for all contract interactions, offering:
- A unified implementation registry and management.
- Centralized state tracking across contracts.
- Consistent error handling and reporting.
- Simplified transaction management and batching.

The **MasterHandler** complements this by managing:
- Implementation execution flow.
- Simulation context management.
- Parameter validation.
- Consistent state updates.
- Coordination between contract interactions.

### Implementation System

Implementations are registered via a decorator. For example:

```python
from src.protocols.implementations.registry import register_implementation
from src.protocols.implementations.base import BaseImplementation
from typing import List
from src.framework.core import SimulationContext
from src.protocols.interfaces.master import ContractCall

@register_implementation("circleshub_trust")
class TrustImplementation(BaseImplementation):
    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        return [
            ContractCall(
                client_name="circleshub",
                method="trust",
                params={
                    "sender": context.agent.address,
                    "trustReceiver": context.get_trustee(),
                    "expiry": context.get_expiry_time()
                }
            )
        ]
```

This design provides:
- **Clean Separation of Concerns:** Easy maintenance and testing.
- **Reusable Implementation Patterns:** Quickly add new protocol features.
- **Simplified Testing:** Isolate and test individual components.


## Configuration

PyCircleSim uses two main configuration files:

### Agent Configuration (`agent_config.yaml`)

```yaml
# Agent distribution and profiles
agent_distribution:
  circles_user: 10  # Create 10 basic users

profiles:
  circles_user:
    description: "Regular network participant"
    base_config:
      target_account_count: 1
      risk_tolerance: 0.5
    action_sequences:
      - name: "registration"
        steps:
          - action: "circleshub_registerHuman"
          - action: "circleshub_personalMint"
```

### Network Configuration (`circles_config.yaml`)

```yaml
# Basic simulation parameters
batch_size: 10
iterations: 100
blocks_per_iteration: 10

# State tracking configuration
state_variables:
  CirclesHub:
    variables:
      trustMarkers:
        type: mapping
        slot: 29
        iterable: true
```


## Basic Usage

Below is an example of how to initialize and run a simulation:

```python
from src.protocols.interfaces.master import MasterClient
from src.framework.core import SimulationContext
from src.protocols.clients import circles_hub_client, wxdai_client

# Initialize the master client with required contract clients
master_client = MasterClient(clients={
    'circleshub': circles_hub_client,
    'wxdai': wxdai_client
})

# Create a simulation context with agents, network state, etc.
context = SimulationContext(
    agent=agent,
    agent_manager=agent_manager,
    clients=master_client.clients,
    chain=chain,
    network_state=network_state
)

# Execute an implementation (e.g., register a human participant)
success, error = master_client.execute(
    'circleshub_registerHuman',
    context,
    sender=user_address,
    inviter=inviter_address
)

if success:
    print("Implementation executed successfully!")
else:
    print(f"Error encountered: {error}")
```


## Running Simulations

Use the CLI to start a simulation. For example:

```bash
ape run scripts/cli.py simulate circles \
    --network-config config/circles_config.yaml \
    --agent-config config/agent_config.yaml \
    --network-size 100 \
    --iterations 500
```

**Available Options:**
- `--network-size`: Override the configured network size.
- `--batch-size`: Override the batch processing size.
- `--iterations`: Set the number of simulation iterations.
- `--blocks-per-iteration`: Number of blocks to mine per iteration.
- `--fast-mode`: Disable data collection for faster execution.



## License

This project is licensed under the [MIT License](LICENSE).

