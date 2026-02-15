# CipherCourt

A data availability audit framework for pre-match tennis modeling.

**⚠️ IMPORTANT: This is NOT a betting bot.** CipherCourt is designed to audit data availability, quality, timestamps, and prevent data leakage in tennis analytics pipelines.

## Overview

CipherCourt provides a comprehensive framework for auditing data sources used in tennis modeling, with a focus on:

- **Data Availability**: Verify that required data sources are accessible
- **Data Quality**: Validate completeness and consistency of data
- **Timestamp Integrity**: Ensure proper temporal ordering and prevent look-ahead bias
- **Leakage Detection**: Identify potential data leakage issues that could compromise model validity

## Features

### Modular Connectors

- **Match Results** - Audit ATP, Challenger, and ITF match results
- **Match Stats** - Validate detailed match statistics
- **Pre-match Odds** - Critical timestamp validation for odds snapshots
- **Venue Metadata** - Verify tournament and court information
- **License Status** - Track data source license compliance

### Report Formats

Generate audit reports in multiple formats:
- JSON (machine-readable)
- CSV (spreadsheet-compatible)
- Markdown (human-readable)

### CLI Interface

Simple command-line interface for running audits:
```bash
# Run full audit
ciphercourt audit

# Use custom configuration
ciphercourt audit -c config.yaml

# Audit specific connectors
ciphercourt audit -n match_results -n odds

# Generate specific report formats
ciphercourt audit -f json -f markdown
```

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/mrdeds/cipherCourt.git
cd cipherCourt

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

## Quick Start

### 1. Generate Configuration File

```bash
ciphercourt init-config -o config.yaml
```

### 2. Edit Configuration

Edit `config.yaml` to configure data sources:

```yaml
match_results:
  circuits:
    - ATP
    - Challenger
    - ITF
  data_path: /path/to/match/data

odds:
  bookmakers:
    - Pinnacle
    - Bet365
  data_path: /path/to/odds/data
```

### 3. Run Audit

```bash
ciphercourt audit -c config.yaml -o ./reports
```

## Usage Examples

### Python API

```python
from ciphercourt import AuditFramework
from ciphercourt.reports import generate_reports

# Create audit framework
framework = AuditFramework()

# Run full audit
results = framework.run_audit()

# Generate reports
generate_reports(results, output_dir="./reports")
```

### Custom Configuration

```python
from ciphercourt import AuditFramework

config = {
    "match_results": {
        "circuits": ["ATP", "Challenger"],
        "data_path": "/path/to/data"
    },
    "odds": {
        "bookmakers": ["Pinnacle"],
        "data_path": "/path/to/odds"
    }
}

framework = AuditFramework(config)
results = framework.run_audit()
```

### Specific Connectors

```python
# Audit only specific connectors
results = framework.run_audit(
    connectors=["match_results", "pre_match_odds"]
)
```

## CLI Commands

### audit

Run data availability audit:

```bash
ciphercourt audit [OPTIONS]
```

**Options:**
- `-c, --config PATH` - Path to configuration file
- `-o, --output-dir PATH` - Output directory for reports
- `-f, --format [json|csv|markdown]` - Report format(s) to generate
- `-n, --connector [...]` - Specific connector(s) to audit
- `-v, --verbose` - Enable verbose output

### init-config

Generate default configuration file:

```bash
ciphercourt init-config -o config.yaml
```

### list-connectors

List all available data connectors:

```bash
ciphercourt list-connectors
```

## Audit Checks

Each connector performs the following checks:

### 1. Availability
- Data source accessibility
- Last update timestamps
- Connection status

### 2. Data Quality
- Required field presence
- Data completeness
- Value validity
- Duplicate detection

### 3. Timestamp Integrity
- Format consistency
- Temporal ordering
- Date range reasonableness
- Timezone handling

### 4. Leakage Detection
- Future-dated records
- Post-match data appearing as pre-match
- Suspicious retroactive updates
- Odds appearing after match start

## Report Interpretation

### Status Levels

- ✅ **PASS** - All checks passed
- ⚠️ **WARNING** - Minor issues detected but usable
- ❌ **FAIL** - Critical issues that compromise data integrity
- ❓ **NOT_AVAILABLE** - Data source not accessible

### Critical Issues

Pay special attention to:
- Future-dated records (potential leakage)
- Post-match odds in pre-match snapshots (look-ahead bias)
- Expired data source licenses
- Missing timestamp information

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=ciphercourt --cov-report=html
```

### Project Structure

```
cipherCourt/
├── ciphercourt/           # Main package
│   ├── connectors/        # Data source connectors
│   │   ├── base.py        # Base connector class
│   │   ├── match_results.py
│   │   ├── match_stats.py
│   │   ├── odds.py
│   │   ├── venue.py
│   │   └── license.py
│   ├── reports/           # Report generators
│   │   └── __init__.py
│   ├── utils/             # Utilities
│   │   └── config.py
│   ├── audit.py           # Main audit framework
│   └── cli.py             # CLI interface
├── tests/                 # Test suite
├── examples/              # Usage examples
├── config.yaml            # Example configuration
└── pyproject.toml         # Project metadata
```

## License

This project is for data quality auditing purposes only. It does not facilitate or encourage betting activities.

## Contributing

Contributions are welcome! Please ensure:
1. All tests pass
2. Code follows existing style
3. New features include tests
4. Documentation is updated

## Support

For issues, questions, or contributions, please use the GitHub issue tracker.
