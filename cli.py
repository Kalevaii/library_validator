#!/usr/bin/env python3
"""CLI for the Library Metadata & Barcode Validator."""

import sys
from pathlib import Path

import click

sys.path.insert(0, str(Path(__file__).parent))

from src.engine import Severity, validate_batch, validate_inventory
from src.report import export_issues_csv, format_batch_summary, format_issues_table, format_summary


@click.group()
def cli():
    """Library Metadata & Automated Barcode Validator."""
    pass


@cli.command()
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
@click.option("--severity", type=click.Choice(["all", "error", "warning"]), default="all")
@click.option("--export", "export_path", type=click.Path(), help="Export issues to CSV")
@click.option("--quiet", is_flag=True, help="Only show summary")
def validate(files, severity, export_path, quiet):
    """Validate one or more inventory files (CSV/JSON)."""
    reports = validate_batch(files)

    if len(reports) == 1:
        report = reports[0]
        click.echo(format_summary(report))
        if not quiet and report.issues:
            click.echo()
            sev = None if severity == "all" else Severity(severity.upper())
            click.echo(format_issues_table(report, sev))
    else:
        click.echo(format_batch_summary(reports))
        if not quiet:
            for report in reports:
                if report.issues:
                    click.echo(f"\n--- {report.filename} ---")
                    sev = None if severity == "all" else Severity(severity.upper())
                    click.echo(format_issues_table(report, sev))

    if export_path and len(reports) == 1:
        Path(export_path).write_text(export_issues_csv(reports[0]))
        click.echo(f"\nIssues exported to {export_path}")

    has_errors = any(r.error_count > 0 for r in reports)
    sys.exit(1 if has_errors else 0)


@cli.command()
def schema():
    """Show the expected inventory schema (Dublin Core mapping)."""
    from src.schema import INVENTORY_SCHEMA

    click.echo(f"{'Field':<15} {'Dublin Core':<20} {'Required':<10} Description")
    click.echo("-" * 70)
    for rule in INVENTORY_SCHEMA:
        req = "Yes" if rule.required else "No"
        click.echo(f"{rule.name:<15} {rule.dublin_core:<20} {req:<10} {rule.description}")


if __name__ == "__main__":
    cli()
