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

**Local CSV Connectors** (with sample data):
- **LocalCSVMatchResultsConnector** - Audit match results from CSV files
- **LocalCSVOddsConnector** - **Hard FAIL rules** for post-match odds detection

**Legacy Connectors**:
- **Match Results** - Audit ATP, Challenger, and ITF match results
- **Match Stats** - Validate detailed match statistics
- **Pre-match Odds** - Critical timestamp validation for odds snapshots
- **Venue Metadata** - Verify tournament and court information
- **License Status** - Track data source license compliance

### Hard FAIL Rules

The LocalCSVOddsConnector enforces **critical anti-leakage rules**:
- ❌ **FAIL** if `available_at >= match_start_time` (look-ahead bias)
- ❌ **FAIL** if `snapshot_timestamp >= match_start_time`
- Detailed violation reporting with timestamps and delays

### Report Formats

Generate audit reports in multiple formats:
- **audit_summary.json** - Machine-readable summary
- **audit_report.md** - Human-readable Markdown report
- **audit_report_*.csv** - Spreadsheet-compatible format

Reports are saved to `data/audit_outputs/` by default.

### CLI Interface

Simple command-line interface for running audits:
```bash
# Run full audit with sample data
ciphercourt audit -c config.yaml

# Audit specific connectors
ciphercourt audit -n local_csv_match_results -n local_csv_odds

# Test with leakage data (should FAIL)
ciphercourt audit -c config_leakage_test.yaml -n local_csv_odds

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

### 1. Run with Sample Data

The repository includes sample CSV data to get started immediately:

```bash
# Run audit with included sample data
ciphercourt audit -c config.yaml

# Test leakage detection (should FAIL)
ciphercourt audit -c config_leakage_test.yaml -n local_csv_odds
```

Sample data is located in `data/samples/`:
- `match_results.csv` - 10 match records with proper schemas
- `odds.csv` - 20 clean odds snapshots
- `odds_with_leakage.csv` - Odds with post-match timestamps (for testing)

### 2. Check Results

Reports are generated in `data/audit_outputs/`:
```bash
cat data/audit_outputs/audit_report.md
cat data/audit_outputs/audit_summary.json
```

### 3. Use Your Own Data

Create CSV files following the required schemas:

**Match Results CSV:**
```csv
match_id,date,tournament,circuit,player1,player2,score,winner,match_start_time,available_at
M001,2024-01-15,Australian Open,ATP,Player A,Player B,6-4 6-3,Player A,2024-01-15T10:00:00Z,2024-01-15T09:00:00Z
```

**Odds CSV:**
```csv
match_id,snapshot_timestamp,player1_odds,player2_odds,bookmaker,available_at,match_start_time
M001,2024-01-15T08:00:00Z,1.85,2.10,Pinnacle,2024-01-15T08:00:00Z,2024-01-15T10:00:00Z
```

Update `config.yaml`:
```yaml
local_csv_match_results:
  csv_path: path/to/your/match_results.csv

local_csv_odds:
  csv_path: path/to/your/odds.csv
```

## Usage Examples

### Python API with Local CSV

```python
from ciphercourt import AuditFramework
from ciphercourt.reports import generate_reports

# Configure with CSV paths
config = {
    "local_csv_match_results": {
        "csv_path": "data/samples/match_results.csv"
    },
    "local_csv_odds": {
        "csv_path": "data/samples/odds.csv"
    }
}

# Create audit framework
framework = AuditFramework(config)

# Run audit
results = framework.run_audit(
    connectors=["local_csv_match_results", "local_csv_odds"]
)

# Generate reports
generate_reports(results, output_dir="data/audit_outputs")

# Check for failures
if results["summary"]["failed"] > 0:
    print("⚠️ CRITICAL ISSUES DETECTED:")
    for issue in results["summary"]["critical_issues"]:
        print(f"  - {issue}")
```

### Leakage Detection Example

```python
config = {
    "local_csv_odds": {
        "csv_path": "data/samples/odds_with_leakage.csv"
    }
}

framework = AuditFramework(config)
results = framework.run_audit(connectors=["local_csv_odds"])

# Check leakage status
odds_result = results["results"]["local_csv_odds"]
if odds_result["overall_status"] == "fail":
    leakage = odds_result["leakage_check"]
    violations = leakage["checks"]["post_match_odds"]["violations"]
    
    for v in violations:
        print(f"Match {v['match_id']}: odds available {v['delay_seconds']}s AFTER match start")
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
