"""
End-to-end example demonstrating CipherCourt with local CSV data.

This example shows how to:
1. Load match results and odds from CSV files
2. Run audits with proper schema validation
3. Detect data leakage issues
4. Generate comprehensive reports
"""

from ciphercourt.audit import AuditFramework
from ciphercourt.reports import generate_reports
from ciphercourt.utils import load_config


def example_clean_data():
    """Example with clean data - should pass all checks."""
    print("=" * 70)
    print("EXAMPLE 1: Clean Data Audit")
    print("=" * 70)
    
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
    
    # Display summary
    summary = results["summary"]
    print(f"\n📊 Audit Summary:")
    print(f"  Total Connectors: {summary['total_connectors']}")
    print(f"  ✅ Passed: {summary['passed']}")
    print(f"  ❌ Failed: {summary['failed']}")
    print(f"  ⚠️  Warnings: {summary['warnings']}")
    
    # Check match results
    match_results = results["results"]["local_csv_match_results"]
    print(f"\n🎾 Match Results Audit:")
    print(f"  Status: {match_results['overall_status'].upper()}")
    print(f"  Records loaded: {match_results['availability']['details']['records_loaded']}")
    
    # Check odds
    odds_results = results["results"]["local_csv_odds"]
    print(f"\n📈 Odds Audit:")
    print(f"  Status: {odds_results['overall_status'].upper()}")
    print(f"  Snapshots loaded: {odds_results['availability']['details']['records_loaded']}")
    print(f"  Leakage status: {odds_results['leakage_check']['status'].upper()}")
    
    return results


def example_leakage_detection():
    """Example with leakage data - should FAIL with critical issues."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Leakage Detection")
    print("=" * 70)
    
    config = {
        "local_csv_odds": {
            "csv_path": "data/samples/odds_with_leakage.csv"
        }
    }
    
    # Create audit framework
    framework = AuditFramework(config)
    
    # Run audit
    results = framework.run_audit(connectors=["local_csv_odds"])
    
    # Display summary
    summary = results["summary"]
    print(f"\n📊 Audit Summary:")
    print(f"  ✅ Passed: {summary['passed']}")
    print(f"  ❌ Failed: {summary['failed']}")
    
    # Check leakage details
    odds_results = results["results"]["local_csv_odds"]
    leakage_check = odds_results["leakage_check"]
    
    print(f"\n🚨 Leakage Detection:")
    print(f"  Status: {leakage_check['status'].upper()}")
    
    if leakage_check["status"] == "fail":
        print(f"\n  ⚠️  CRITICAL ISSUES DETECTED:")
        for issue in leakage_check["issues"]:
            print(f"    - {issue}")
        
        # Show violation details
        post_match = leakage_check["checks"]["post_match_odds"]
        if post_match["post_match_count"] > 0:
            print(f"\n  📋 Violation Details:")
            for violation in post_match["violations"]:
                print(f"    Match {violation['match_id']}:")
                print(f"      Available at: {violation['available_at']}")
                print(f"      Match start:  {violation['match_start_time']}")
                print(f"      Delay: {violation['delay_seconds']} seconds AFTER match start")
    
    return results


def example_config_file():
    """Example loading configuration from file."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Configuration File")
    print("=" * 70)
    
    # Load config from file
    config = load_config("config.yaml")
    
    print(f"\n📄 Loaded Configuration:")
    print(f"  Match results path: {config['local_csv_match_results']['csv_path']}")
    print(f"  Odds path: {config['local_csv_odds']['csv_path']}")
    print(f"  Output directory: {config['reports']['output_dir']}")
    
    # Run audit
    framework = AuditFramework(config)
    results = framework.run_audit(
        connectors=["local_csv_match_results", "local_csv_odds"]
    )
    
    # Generate reports
    output_dir = config["reports"]["output_dir"]
    generated = generate_reports(results, output_dir=output_dir)
    
    print(f"\n📝 Reports Generated:")
    for fmt, path in generated.items():
        print(f"  {fmt.upper()}: {path}")
    
    return results


def example_schema_validation():
    """Example showing schema validation."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Schema Validation")
    print("=" * 70)
    
    config = {
        "local_csv_match_results": {
            "csv_path": "data/samples/match_results.csv"
        }
    }
    
    framework = AuditFramework(config)
    results = framework.run_audit(connectors=["local_csv_match_results"])
    
    match_results = results["results"]["local_csv_match_results"]
    quality_checks = match_results["data_quality"]["checks"]
    
    print(f"\n✅ Required Fields Check:")
    required = quality_checks["required_fields"]
    print(f"  Expected fields: {', '.join(required['expected'])}")
    print(f"  Status: {required['status'].upper()}")
    
    print(f"\n📊 Data Completeness:")
    completeness = quality_checks["completeness"]
    print(f"  Total records: {completeness['total_records']}")
    print(f"  Complete records: {completeness['complete_records']}")
    print(f"  Completeness rate: {completeness['completeness_rate']:.1%}")
    
    return results


def main():
    """Run all examples."""
    print("\n" + "🏆" * 35)
    print("CipherCourt End-to-End Examples")
    print("🏆" * 35)
    
    # Example 1: Clean data
    example_clean_data()
    
    # Example 2: Leakage detection
    example_leakage_detection()
    
    # Example 3: Config file
    example_config_file()
    
    # Example 4: Schema validation
    example_schema_validation()
    
    print("\n" + "=" * 70)
    print("✅ All examples completed!")
    print("=" * 70)
    print("\n📁 Check data/audit_outputs/ for generated reports")
    print("   - audit_summary.json (machine-readable)")
    print("   - audit_report.md (human-readable)")
    print("\n🔍 Key Features Demonstrated:")
    print("   ✓ CSV-based data loading")
    print("   ✓ Schema validation (available_at, match_start_time)")
    print("   ✓ Hard FAIL rules for post-match odds")
    print("   ✓ Comprehensive reporting")
    print("   ✓ Data quality checks")
    print("   ✓ Timestamp validation")
    print("   ✓ Anti-leakage safeguards")
    print()


if __name__ == "__main__":
    main()
