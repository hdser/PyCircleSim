![Header](img/header-pycirclesim.png)

__PyCircleSim__ is a Python framework for simulating and analyzing the Circles protocol. It provides tools for building test networks, evolving system state, and collecting data about token distributions and trust relationships within the Circles ecosystem.

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
- DuckDB for data storage and analysis

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
- duckdb for data storage
- other required packages

## Project Structure

```
pyCircleSim/
├── README.md
├── setup.py
├── rings_network/
│   ├── __init__.py
│   ├── network_builder.py     # Network creation and trust setup
│   ├── network_evolver.py     # Time evolution and minting
│   ├── network_analyzer.py    # Analysis tools
│   ├── circles_data_collector.py  # Data collection and storage
│   └── duckdb/               # SQL queries for data management
│       ├── schema/           # Table and view definitions
│       │   ├── humans.up.sql
│       │   ├── trusts.up.sql
│       │   ├── balance_changes.up.sql
│       │   └── network_stats.up.sql
│       ├── views/            # SQL view definitions
│       │   ├── current_balances.view.sql
│       │   └── active_trusts.view.sql
│       ├── queries/          # Data manipulation queries
│       │   ├── insert_human.sql
│       │   ├── insert_trust.sql
│       │   └── insert_balance_change.sql
│       └── analysis/         # Analysis queries
│           ├── human_growth.sql
│           ├── trust_growth.sql
│           └── token_velocity.sql
└── scripts/
    ├── rings.py              # Main simulation script
    └── abi/                  # Contract ABIs
```

## Data Collection System

PyCircleSim uses DuckDB as its data storage engine, with a well-organized SQL query system for data management. All database operations are defined in SQL files, making the system highly maintainable and extensible.

### Database Schema

The data collection system tracks four main entities:

1. Humans (Registration Data):
   - Blockchain addresses
   - Registration timestamps
   - Invitation relationships
   - Welcome bonus amounts

2. Trust Relationships:
   - Directional trust connections
   - Trust limits
   - Temporal validity
   - Historical trust changes

3. Balance Changes:
   - Account balances over time
   - Transaction details
   - Token types and amounts
   - Event classifications

4. Network Statistics:
   - Periodic network snapshots
   - Global metrics
   - Trust network density
   - Token distribution stats

### Using the Data Collector

The CirclesDataCollector class provides a high-level interface to the data storage system:

```python
from rings_network import CirclesDataCollector

# Initialize collector with default SQL directory
collector = CirclesDataCollector()

# Record network events
collector.record_human_registration(
    address="0x123...",
    block_number=1000,
    timestamp=current_time,
    welcome_bonus=100.0
)

# Record trust relationships
collector.record_trust_relationship(
    truster="0x123...",
    trustee="0x456...",
    block_number=1001,
    timestamp=current_time,
    trust_limit=1000.0,
    expiry_time=expiry_time
)

# Export data for analysis
collector.export_to_csv("analysis_results")
```

### Extending the Data Collection

To add new data collection capabilities:

1. Add new SQL files to the appropriate subdirectory in `duckdb/`
2. Update the schema if needed using new `.up.sql` files
3. Create new analysis queries in the `analysis/` directory
4. Use the collector's `_read_sql_file()` method to execute the new queries

### Analysis Queries

The system comes with pre-built analysis queries for common metrics:

- Human growth analysis
- Trust network evolution
- Token velocity tracking
- Balance distribution analysis
- Network density calculations

Access these through the collector's interface:

```python
# Get pre-defined analysis queries
queries = collector.get_analysis_queries()

# Execute specific analysis
human_growth = collector.con.execute(queries["human_growth"]).df()
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.