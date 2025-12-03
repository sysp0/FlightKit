import sys
import os
import time
import click
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from rich.theme import Theme

# Allow running without installing as package
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
})
console = Console(theme=custom_theme)


def print_banner():
    """Shows ASCII art when in interactive mode."""
    console.clear()
    art = """
 ███████╗██╗     ██╗ ██████╗ ██╗  ██╗████████╗██╗  ██╗██╗████████╗
 ██╔════╝██║     ██║██╔════╝ ██║  ██║╚══██╔══╝██║ ██╔╝██║╚══██╔══╝
 █████╗  ██║     ██║██║  ███╗███████║   ██║   █████╔╝ ██║   ██║   
 ██╔══╝  ██║     ██║██║   ██║██╔══██║   ██║   ██╔═██╗ ██║   ██║   
 ██║     ███████╗██║╚██████╔╝██║  ██║   ██║   ██║  ██╗██║   ██║   
 ╚═╝     ╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝   ╚═╝   
"""
    console.print(Panel(Text(art, justify="center", style="bold cyan"),
                        subtitle="[bold white]flightkit • domestic crawler[/]",
                        border_style="blue"))
    console.print("[italic grey50]Interactive mode activated. Let's find tickets![/]\n")


def ask_date():
    """Asks user for date via Questionary."""
    return questionary.text(
        "Enter flight date (YYYY-MM-DD):",
        default="2025-12-03",
        validate=lambda text: True if len(text) == 10 else "Use format YYYY-MM-DD"
    ).ask()


@click.command()
@click.option("--date", "-d", help="Flight date (YYYY-MM-DD).")
def main(date: str):
    """
    CLI main entry point.
    Batch mode if --date or FLIGHT_DATE provided.
    Interactive mode otherwise.
    """
    env_date = os.getenv("FLIGHT_DATE")
    target_date = date or env_date

    interactive_allowed = sys.stdin.isatty() and sys.stdout.isatty()

    if not target_date:
        if not interactive_allowed:
            raise click.ClickException(
                "No date provided and interactive mode is unavailable. "
                "Use '--date YYYY-MM-DD' or set FLIGHT_DATE env."
            )
        print_banner()
        target_date = ask_date()
        if not target_date:
            console.print("[warning]Operation cancelled by user.[/]")
            return
    else:
        console.print(f"[info]Batch mode[/info] - target date set to [bold]{target_date}[/bold]")

    console.print(f"[info]Route:[/info] MHD → THR | [info]Date:[/info] {target_date}")

    try:
        from flightkit.core import UtravsProvider, SearchCriteria
        from flightkit.exporters.excel_exporter import ExcelExporter

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
            console.print(Panel(f"No flights for {target_date}.", border_style="yellow"))
            return

        console.print(f"[success]Found {len(flights)} flights.[/success]")

        filename = "flight_database.xlsx"
        with console.status(f"Saving to {filename}...", spinner="dots"):
            exporter.export(flights, filename)
            time.sleep(0.5)

        console.print(Panel(
            f"Saved to [bold]{filename}[/bold].",
            title="DONE",
            border_style="green"
        ))

    except Exception as exc:
        console.print(f"[error]Error:[/error] {exc}")
    


if __name__ == "__main__":
    main()