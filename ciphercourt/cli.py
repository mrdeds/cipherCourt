"""
Command-line interface for CipherCourt audit framework.
"""

import click
import sys
from pathlib import Path
from typing import Optional

from ciphercourt.audit import AuditFramework
from ciphercourt.reports import generate_reports
from ciphercourt.utils.config import load_config, get_default_config, save_config


@click.group()
@click.version_option(version="0.1.0")
def main():
    """
    CipherCourt - Data availability audit framework for pre-match tennis modeling.
    
    This is NOT a betting bot. It is designed to audit data availability,
    quality, timestamps, and prevent data leakage in tennis analytics.
    """
    pass


@main.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Path to configuration YAML file"
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(),
    default=".",
    help="Output directory for audit reports"
)
@click.option(
    "--format",
    "-f",
    "formats",
    multiple=True,
    type=click.Choice(["json", "csv", "markdown"], case_sensitive=False),
    help="Report format(s) to generate"
)
@click.option(
    "--connector",
    "-n",
    "connectors",
    multiple=True,
    type=click.Choice([
        "match_results",
        "match_stats",
        "pre_match_odds",
        "venue_metadata",
        "license_status"
    ], case_sensitive=False),
    help="Specific connector(s) to audit"
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output"
)
def audit(config: Optional[str], 
          output_dir: str,
          formats: tuple,
          connectors: tuple,
          verbose: bool):
    """
    Run data availability audit.
    
    Examples:
    
        # Run full audit with default config
        ciphercourt audit
        
        # Run audit with custom config
        ciphercourt audit -c config.yaml
        
        # Run specific connectors only
        ciphercourt audit -n match_results -n odds
        
        # Generate specific report formats
        ciphercourt audit -f json -f markdown
    """
    # Load configuration
    if config:
        try:
            audit_config = load_config(config)
            if verbose:
                click.echo(f"✓ Loaded configuration from {config}")
        except Exception as e:
            click.echo(f"✗ Error loading configuration: {e}", err=True)
            sys.exit(1)
    else:
        audit_config = get_default_config()
        if verbose:
            click.echo("✓ Using default configuration")
    
    # Initialize audit framework
    if verbose:
        click.echo("Initializing audit framework...")
    
    try:
        framework = AuditFramework(audit_config)
    except Exception as e:
        click.echo(f"✗ Error initializing audit framework: {e}", err=True)
        sys.exit(1)
    
    # Run audit
    if verbose:
        click.echo("Running audit checks...")
        if connectors:
            click.echo(f"  Connectors: {', '.join(connectors)}")
    
    try:
        audit_results = framework.run_audit(connectors=list(connectors) if connectors else None)
    except Exception as e:
        click.echo(f"✗ Error running audit: {e}", err=True)
        sys.exit(1)
    
    # Display summary
    summary = audit_results.get("summary", {})
    click.echo("\n" + "=" * 60)
    click.echo("AUDIT SUMMARY")
    click.echo("=" * 60)
    click.echo(f"Total Connectors:  {summary.get('total_connectors', 0)}")
    click.echo(f"Passed:            {summary.get('passed', 0)} ✓")
    click.echo(f"Failed:            {summary.get('failed', 0)} ✗")
    click.echo(f"Warnings:          {summary.get('warnings', 0)} ⚠")
    click.echo(f"Not Available:     {summary.get('not_available', 0)}")
    
    critical_issues = summary.get("critical_issues", [])
    if critical_issues:
        click.echo("\n⚠️  CRITICAL ISSUES:")
        for issue in critical_issues:
            click.echo(f"  - {issue}")
    
    # Generate reports
    report_formats = list(formats) if formats else audit_config.get("reports", {}).get("formats", ["json", "csv", "markdown"])
    
    if verbose:
        click.echo(f"\nGenerating reports in formats: {', '.join(report_formats)}")
    
    try:
        generated_reports = generate_reports(
            audit_results,
            output_dir=output_dir,
            formats=report_formats
        )
        
        click.echo("\n" + "=" * 60)
        click.echo("REPORTS GENERATED")
        click.echo("=" * 60)
        for fmt, path in generated_reports.items():
            click.echo(f"{fmt.upper():12s}: {path}")
    except Exception as e:
        click.echo(f"✗ Error generating reports: {e}", err=True)
        sys.exit(1)
    
    # Exit with appropriate code
    if summary.get("failed", 0) > 0:
        sys.exit(1)
    elif summary.get("warnings", 0) > 0:
        sys.exit(0)  # Warnings don't cause failure
    else:
        sys.exit(0)


@main.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="config.yaml",
    help="Output path for configuration file"
)
def init_config(output: str):
    """
    Generate a default configuration file.
    
    Example:
        ciphercourt init-config -o my-config.yaml
    """
    try:
        config = get_default_config()
        save_config(config, output)
        click.echo(f"✓ Configuration file created: {output}")
    except Exception as e:
        click.echo(f"✗ Error creating configuration file: {e}", err=True)
        sys.exit(1)


@main.command()
def list_connectors():
    """
    List all available data connectors.
    """
    connectors = [
        ("match_results", "Audit match results from ATP/Challenger/ITF"),
        ("match_stats", "Audit detailed match statistics"),
        ("pre_match_odds", "Audit pre-match odds snapshots with timestamps"),
        ("venue_metadata", "Audit venue and tournament metadata"),
        ("license_status", "Audit data source license status")
    ]
    
    click.echo("\nAvailable Data Connectors:")
    click.echo("=" * 60)
    for name, description in connectors:
        click.echo(f"{name:20s} - {description}")
    click.echo()


if __name__ == "__main__":
    main()
