"""Command line interface for Git Sniff Otter."""

import os
import sys
from datetime import datetime, timedelta
from typing import Optional

try:
    import click
except ImportError:
    print(
        "Error: Click library not installed. Please run 'make install' or 'pip install -r requirements.txt'"
    )
    import sys

    sys.exit(1)

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
except ImportError:
    print(
        "Error: Rich library not installed. Please run 'make install' or 'pip install -r requirements.txt'"
    )
    import sys

    sys.exit(1)

from .config import Config, load_config
from .modules.data_collector import DataCollector
from .modules.data_transformer import DataTransformer
from .modules.llm_generator import LLMReportGenerator
from .modules.slack_sender import SlackSender

console = Console()


@click.group()
def cli():
    """Git Sniff Otter - Automated Git repository analysis and reporting tool."""
    pass


@cli.command()
@click.option(
    "--repos",
    "-r",
    multiple=True,
    required=True,
    help="Git repository paths to analyze (can be specified multiple times)",
)
@click.option(
    "--days", "-d", default=7, type=int, help="Number of days to analyze (default: 7)"
)
@click.option(
    "--start-date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="Start date for analysis (YYYY-MM-DD)",
)
@click.option(
    "--end-date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="End date for analysis (YYYY-MM-DD)",
)
@click.option(
    "--config", "-c", type=click.Path(exists=True), help="Path to configuration file"
)
@click.option(
    "--channel", default=None, help="Slack channel to send report to (overrides config)"
)
@click.option(
    "--dry-run", is_flag=True, help="Generate report but do not send to Slack"
)
@click.option(
    "--save-report", type=click.Path(), help="Save the generated report to a file"
)
def analyze(
    repos: tuple,
    days: int,
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    config: Optional[str],
    channel: Optional[str],
    dry_run: bool,
    save_report: Optional[str],
):
    """Analyze Git repositories and generate a report."""

    console.print(
        "🔍 [bold blue]Git Sniff Otter[/bold blue] - Starting analysis...", style="bold"
    )

    try:
        # Load configuration
        app_config = load_config(config)

        # Override configuration with CLI parameters
        app_config.repository_paths = list(repos)
        if channel:
            app_config.slack_channel = channel
        if start_date and end_date:
            app_config.start_date = start_date
            app_config.end_date = end_date
        elif start_date:
            app_config.start_date = start_date
            app_config.end_date = datetime.now()
        elif end_date:
            app_config.start_date = end_date - timedelta(days=days)
            app_config.end_date = end_date
        else:
            app_config.time_window_days = days

        # Validate repositories
        _validate_repositories(repos)

        # Show analysis parameters
        _show_analysis_parameters(app_config)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Step 1: Data Collection
            task1 = progress.add_task("Collecting repository data...", total=None)
            collector = DataCollector(app_config)
            repo_data = collector.collect_all_data()
            progress.update(task1, completed=True)

            # Step 2: Data Transformation
            task2 = progress.add_task("Transforming data...", total=None)
            transformer = DataTransformer(
                app_config.analysis_start_date, app_config.analysis_end_date
            )
            transformed_data = transformer.transform(repo_data)
            progress.update(task2, completed=True)

            # Step 3: Report Generation
            task3 = progress.add_task("Generating LLM report...", total=None)
            generator = LLMReportGenerator(app_config)
            report = generator.generate_report(transformed_data)
            progress.update(task3, completed=True)

            # Step 4: Output
            if save_report:
                task4 = progress.add_task("Saving report to file...", total=None)
                with open(save_report, "w", encoding="utf-8") as f:
                    f.write(report)
                progress.update(task4, completed=True)
                console.print(
                    f"✅ Report saved to: [bold green]{save_report}[/bold green]"
                )

            if not dry_run:
                task5 = progress.add_task("Sending to Slack...", total=None)
                slack_sender = SlackSender(app_config)
                success = slack_sender.send_report(report)
                progress.update(task5, completed=True)

                if success:
                    console.print(
                        f"✅ Report sent successfully to [bold green]{app_config.slack_channel}[/bold green]"
                    )
                else:
                    console.print(
                        "❌ [bold red]Failed to send report to Slack[/bold red]"
                    )
                    return 1
            else:
                console.print(
                    "🏃 [yellow]Dry run mode - report not sent to Slack[/yellow]"
                )
                console.print("\n[bold]Generated Report Preview:[/bold]")
                console.print("-" * 50)
                console.print(report[:500] + "..." if len(report) > 500 else report)

        console.print("\n🎉 [bold green]Analysis completed successfully![/bold green]")
        return 0

    except Exception as e:
        console.print(f"❌ [bold red]Error during analysis: {e}[/bold red]")
        return 1


@cli.command()
@click.option(
    "--config", "-c", type=click.Path(exists=True), help="Path to configuration file"
)
def test_slack(config: Optional[str]):
    """Test Slack connection configuration."""

    console.print("🧪 [bold blue]Testing Slack connection...[/bold blue]")

    try:
        app_config = load_config(config)
        slack_sender = SlackSender(app_config)

        if slack_sender.test_connection():
            console.print("✅ [bold green]Slack connection successful![/bold green]")
            return 0
        else:
            console.print("❌ [bold red]Slack connection failed![/bold red]")
            return 1

    except Exception as e:
        console.print(f"❌ [bold red]Error testing Slack connection: {e}[/bold red]")
        return 1


@cli.command()
@click.argument("repositories", nargs=-1, required=True)
def validate_repos(repositories):
    """Validate that the specified paths are valid Git repositories."""

    console.print("🔍 [bold blue]Validating repositories...[/bold blue]")

    table = Table(title="Repository Validation Results")
    table.add_column("Repository Path", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Details", style="green")

    all_valid = True

    for repo_path in repositories:
        if not os.path.exists(repo_path):
            table.add_row(repo_path, "❌ Invalid", "Path does not exist")
            all_valid = False
        elif not os.path.exists(os.path.join(repo_path, ".git")):
            table.add_row(repo_path, "❌ Invalid", "Not a Git repository")
            all_valid = False
        else:
            # Try to get some basic info
            try:
                from git import Repo

                repo = Repo(repo_path)
                commit_count = len(list(repo.iter_commits(max_count=100)))
                details = f"Valid Git repo (~{commit_count}+ commits)"
                table.add_row(repo_path, "✅ Valid", details)
            except Exception as e:
                table.add_row(
                    repo_path, "⚠️  Warning", f"Git repo but error: {str(e)[:50]}"
                )

    console.print(table)

    if all_valid:
        console.print("\n✅ [bold green]All repositories are valid![/bold green]")
        return 0
    else:
        console.print("\n❌ [bold red]Some repositories are invalid![/bold red]")
        return 1


def _validate_repositories(repos: tuple) -> None:
    """Validate repository paths."""
    for repo_path in repos:
        if not os.path.exists(repo_path):
            raise click.ClickException(f"Repository path does not exist: {repo_path}")
        if not os.path.exists(os.path.join(repo_path, ".git")):
            raise click.ClickException(f"Path is not a Git repository: {repo_path}")


def _show_analysis_parameters(config: Config) -> None:
    """Display analysis parameters in a formatted table."""
    table = Table(title="Analysis Parameters")
    table.add_column("Parameter", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("Repositories", f"{len(config.repository_paths)} repositories")
    table.add_row("Start Date", config.analysis_start_date.strftime("%Y-%m-%d %H:%M"))
    table.add_row("End Date", config.analysis_end_date.strftime("%Y-%m-%d %H:%M"))
    table.add_row(
        "Duration",
        f"{(config.analysis_end_date - config.analysis_start_date).days} days",
    )
    table.add_row("LLM Model", config.llm_model)
    table.add_row("Slack Channel", config.slack_channel)

    console.print(table)


if __name__ == "__main__":
    sys.exit(cli())
