import os
import sys
from datetime import datetime

import click
import questionary
from rich.console import Console
from rich.theme import Theme

# Allow running locally without package install
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

# Configuration
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
})
console = Console(theme=custom_theme)

# CLI Commands
@click.group()
def cli():
    """FlightKit CLI Tool."""
    pass

@cli.command(name="fetch")
@click.option("--date", "-d", required=True, help="Flight date (YYYY-MM-DD or 1404-09-12).")
@click.option("--output", "-o", help="Output filename.", default=None)
def fetch_command(date, output):
    """
    Single run mode: Fetches flights for a specific date and exits.
    Example: flightkit fetch --date 1404-09-12
    """
    from flightkit.utils.date import normalize_to_gregorian
    from flightkit.cli.utils import run_flight_search_task
    try:
        target_date = normalize_to_gregorian(date)
        
        if not output:
            timestamp = datetime.now().strftime("%H-%M-%S")
            output = f"flights_{target_date}_{timestamp}.xlsx"
            
        run_flight_search_task(target_date, output, console)
        
    except ValueError as e:
        console.print(f"[error]Invalid Date:[/error] {e}")


@cli.command(name="menu")
def interactive_command():
    """
    Interactive mode: Shows menu and enters search loop.
    """
    from flightkit.cli.utils import print_banner
    from flightkit.cli.utils import get_user_parameters_loop
    print_banner(console)
    
    # Main Menu
    choice = questionary.select(
        "Welcome to FlightKit. Select an option:",
        choices=[
            "1. Find Flights",
            "2. Exit"
        ]
    ).ask()

    if choice and choice.startswith("1"):
        get_user_parameters_loop(console)
    else:
        console.print("[dim]Goodbye![/dim]")


if __name__ == "__main__":
    cli()