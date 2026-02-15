# Data Directory

This directory contains sample CSV files and audit outputs for the CipherCourt framework.

## Structure

```
data/
├── samples/          # Sample CSV data files
│   ├── match_results.csv          # Clean match results data
│   ├── odds.csv                   # Clean pre-match odds data (no leakage)
│   └── odds_with_leakage.csv      # Odds data with leakage issues (for testing)
└── audit_outputs/    # Generated audit reports (gitignored)
    ├── audit_summary.json         # JSON summary of audit results
    ├── audit_report.md            # Human-readable Markdown report
    └── audit_report_*.csv         # CSV report with timestamp
```

## Sample Data Files

### match_results.csv

Schema:
- `match_id`: Unique identifier for the match
- `date`: Match date
- `tournament`: Tournament name  
- `circuit`: Circuit type (ATP/Challenger/ITF)
- `player1`: First player name
- `player2`: Second player name
- `score`: Match score
- `winner`: Winner name
- `match_start_time`: ISO 8601 timestamp when match started
- `available_at`: ISO 8601 timestamp when data became available

### odds.csv

Clean pre-match odds data with proper timestamps.

Schema:
- `match_id`: Match identifier
- `snapshot_timestamp`: When odds snapshot was taken
- `player1_odds`: Decimal odds for player 1
- `player2_odds`: Decimal odds for player 2
- `bookmaker`: Bookmaker name
- `available_at`: ISO 8601 timestamp when odds became available
- `match_start_time`: ISO 8601 timestamp when match started

**Critical Constraint**: `available_at` must be < `match_start_time` (enforced with HARD FAIL)

### odds_with_leakage.csv

Contains odds data where some snapshots have `available_at >= match_start_time`, which represents look-ahead bias. Used for testing the hard FAIL rules.

## Usage

### Running Audit with Sample Data

```bash
# Audit with clean data (should pass)
ciphercourt audit -c config.yaml

# Audit with leakage data (should FAIL)
ciphercourt audit -c config_leakage_test.yaml
```

### Expected Results

With clean data (`odds.csv`):
- All local CSV connectors should PASS
- No critical issues

With leakage data (`odds_with_leakage.csv`):
- local_csv_odds connector should FAIL
- Critical issues reported for post-match odds
- Exit code 1

## Adding Your Own Data

To use your own CSV files:

1. Create CSV files following the schemas above
2. Update `config.yaml` with paths to your files:

```yaml
local_csv_match_results:
  csv_path: path/to/your/match_results.csv

local_csv_odds:
  csv_path: path/to/your/odds.csv
```

3. Run the audit:

```bash
ciphercourt audit -c config.yaml
```

## Anti-Leakage Enforcement

The odds connector implements **hard FAIL rules**:

1. If `available_at >= match_start_time` → FAIL status
2. If `snapshot_timestamp >= match_start_time` → FAIL status

These rules prevent look-ahead bias by ensuring all odds are truly pre-match.
