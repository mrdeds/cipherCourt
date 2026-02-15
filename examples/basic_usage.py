"""
Example usage of CipherCourt audit framework.
"""

from ciphercourt import AuditFramework
from ciphercourt.reports import generate_reports
from ciphercourt.utils import load_config, get_default_config


def example_basic_audit():
    """Run a basic audit with default configuration."""
    print("=" * 60)
    print("EXAMPLE: Basic Audit")
    print("=" * 60)
    
    # Create audit framework with default config
    framework = AuditFramework()
    
    # Run full audit
    results = framework.run_audit()
    
    # Display summary
    summary = results["summary"]
    print(f"\nTotal Connectors: {summary['total_connectors']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Warnings: {summary['warnings']}")
    print(f"Not Available: {summary['not_available']}")
    
    if summary["critical_issues"]:
        print("\nCritical Issues:")
        for issue in summary["critical_issues"]:
            print(f"  - {issue}")
    
    return results


def example_custom_config():
    """Run audit with custom configuration."""
    print("\n" + "=" * 60)
    print("EXAMPLE: Custom Configuration")
    print("=" * 60)
    
    # Custom configuration
    config = {
        "match_results": {
            "circuits": ["ATP", "Challenger"],
            "data_path": "/path/to/data"
        },
        "odds": {
            "bookmakers": ["Pinnacle", "Bet365"],
            "data_path": "/path/to/odds"
        }
    }
    
    # Create framework with custom config
    framework = AuditFramework(config)
    
    # Run audit
    results = framework.run_audit()
    
    print(f"\nAudited {len(results['connectors_audited'])} connectors")
    print(f"Connectors: {', '.join(results['connectors_audited'])}")
    
    return results


def example_specific_connectors():
    """Run audit on specific connectors only."""
    print("\n" + "=" * 60)
    print("EXAMPLE: Specific Connectors")
    print("=" * 60)
    
    framework = AuditFramework()
    
    # Audit only odds and match results
    connectors_to_audit = ["pre_match_odds", "match_results"]
    results = framework.run_audit(connectors=connectors_to_audit)
    
    print(f"\nAudited connectors: {', '.join(results['connectors_audited'])}")
    
    return results


def example_generate_reports():
    """Generate reports in multiple formats."""
    print("\n" + "=" * 60)
    print("EXAMPLE: Generate Reports")
    print("=" * 60)
    
    # Run audit
    framework = AuditFramework()
    results = framework.run_audit()
    
    # Generate reports
    generated = generate_reports(
        results,
        output_dir="/tmp",
        formats=["json", "csv", "markdown"]
    )
    
    print("\nGenerated reports:")
    for fmt, path in generated.items():
        print(f"  {fmt}: {path}")
    
    return generated


def example_load_config():
    """Load configuration from YAML file."""
    print("\n" + "=" * 60)
    print("EXAMPLE: Load Configuration")
    print("=" * 60)
    
    try:
        # Try to load config.yaml
        config = load_config("config.yaml")
        print("\n✓ Loaded configuration from config.yaml")
        print(f"  Circuits: {config.get('match_results', {}).get('circuits', [])}")
    except FileNotFoundError:
        print("\n✗ config.yaml not found, using default configuration")
        config = get_default_config()
    
    # Run audit with loaded config
    framework = AuditFramework(config)
    results = framework.run_audit()
    
    return results


if __name__ == "__main__":
    # Run all examples
    example_basic_audit()
    example_custom_config()
    example_specific_connectors()
    example_generate_reports()
    example_load_config()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
