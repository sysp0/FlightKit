import time
from datetime import datetime

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text


# UI Helpers
def print_banner(console: Console):
    """Shows ASCII art."""
    console.clear()
    art = """
    ███████╗██╗     ██╗ ██████╗ ██╗  ██╗████████╗██╗  ██╗██╗████████╗
    ██╔════╝██║     ██║██╔════╝ ██║  ██║╚══██╔══╝██║ ██╔╝██║╚══██╔══╝
 █████╗  ██║     ██║██║  ███╗███████║   ██║   █████╔╝ ██║   ██║   
 ██╔══╝  ██║     ██║██║   ██║██╔══██║   ██║   ██╔═██╗ ██║   ██║   
 ██║     ███████╗██║╚██████╔╝██║  ██║   ██║   ██║  ██╗██║   ██║   
 ╚═╝     ╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝   ╚═╝   
"""
    console.print(
        Panel(
            Text(art, justify="center", style="bold cyan"),
            subtitle="[bold white]flightkit • crawler[/]",
            border_style="blue"
        )
    )

def validate_date_input(text):
    """Validator that ensures the date is parsable."""
    from flightkit.utils.date import normalize_to_gregorian
    
    try:
        normalize_to_gregorian(text)
        return True
    except ValueError:
        return "Invalid date! Use YYYY-MM-DD (e.g., 1404-09-12 or 2025-12-03)"


# Core Business Logic
def run_flight_search_task(target_date: str, filename: str, console: Console):
    """
    Executes the main logic: connects to API, fetches flights, saves to Excel.
    This function is agnostic to how it was called (CLI or Interactive).
    """
    # Lazy imports
    from flightkit.core import SearchCriteria, UtravsProvider
    from flightkit.exporters.excel_exporter import ExcelExporter

    console.print(f"[info]Route:[/info] THR → MHD | [info]Date:[/info] {target_date}")

    try:
        flights = []
        with Progress(
            SpinnerColumn(style="magenta"),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        ) as progress:
            
            prep = progress.add_task("Preparing services...", total=None)
            scraper = UtravsProvider()
            exporter = ExcelExporter()
            criteria = SearchCriteria(origin="MHD", destination="THR", date=target_date)
            time.sleep(0.3)
            progress.remove_task(prep)

            fetch = progress.add_task("Fetching flights from Utravs...", total=None)
            flights = scraper.get_flights(criteria)
            progress.remove_task(fetch)

        if not flights:
            console.print(Panel(f"No flights found for {target_date}.", border_style="yellow"))
            return

        console.print(f"[success]Found {len(flights)} flights.[/success]")

        # Ensure extension
        if not filename.endswith(".xlsx"):
            filename += ".xlsx"

        with console.status(f"Saving to {filename}...", spinner="dots"):
            exporter.export(flights, filename)
            time.sleep(0.5)

        console.print(Panel(
            f"Saved to [bold]artifacts/{filename}[/bold].",
            title="DONE",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"[error]Task Failed:[/error] {e}")

def get_user_parameters_loop(console: Console):
    """
    Handles the input loop for interactive mode.
    """
    from flightkit.utils.date import normalize_to_gregorian

    while True:
        console.print("\n[info]-- New Search (Press Ctrl+C to Return/Exit) --[/info]")
        try:
            # 1. Ask for Date
            date_input = questionary.text(
                "Enter flight date (Shamsi or Gregorian):",
                default="1404-09-12",
                validate=validate_date_input
            ).ask()
            
            if date_input is None: # Handle Ctrl+C in questionary
                break

            target_date = normalize_to_gregorian(date_input)

            # 2. Auto-generate filename or ask
            current_time = datetime.now().strftime("%H-%M-%S")
            default_name = f"flights_{target_date}_{current_time}.xlsx"
            
            filename = questionary.text(
                "Output filename:",
                default=default_name
            ).ask()
            
            if filename is None: 
                break

            # 3. Run Logic
            run_flight_search_task(target_date, filename, console)

        except KeyboardInterrupt:
            console.print("\n[warning]Loop interrupted by user.[/]")
            break


