from flightkit.utils import logger
from flightkit.core import SearchCriteria
from flightkit.core import UtravsProvider
from flightkit.exporters.excel_exporter import ExcelExporter


def run_flight_crawler(target_date: str):
    """
    Main entry point.
    Searches MHD -> THR flights and appends to Excel.
    """
    logger.info(f"Starting crawler operation for date: {target_date}")
    
    # 1. Setup Dependencies
    scraper = UtravsProvider()
    exporter = ExcelExporter()
    
    criteria = SearchCriteria(origin="MHD", destination="THR", date=target_date)
    
    try:
        # 2. Fetch
        logger.info("Connecting to Utravs provider...")
        flights = scraper.get_flights(criteria)
        
        if not flights:
            logger.warning("No flights found for the specified date.")
            return

        logger.info(f"Successfully fetched {len(flights)} flights.")

        # 3. Export
        filename = "flight_database.xlsx"
        exporter.export(flights, filename)
        logger.info(f"Data successfully appended to '{filename}'.")

    except Exception as error:
        logger.error(f"Critical error during execution: {error}")


if __name__ == "__main__":
    run_flight_crawler("2025-12-03")