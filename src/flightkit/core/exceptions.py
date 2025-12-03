from typing import Optional

class FlightScraperException(Exception):
    """
    This is the main error for our project.
    If something goes wrong in our code, we use this error.
    """
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.original_error = original_error

class FlightValidationException(FlightScraperException):
    """
    We use this when the data is wrong.
    Example: Price is zero, or date is in the past.
    """
    pass

class ProviderConnectionException(FlightScraperException):
    """
    We use this when we cannot connect to the website.
    Example: No internet, or the website is down.
    """
    pass

class ProviderAuthenticationException(FlightScraperException):
    """
    We use this when login fails.
    Example: The token is old or wrong.
    """
    pass

class ProviderResponseException(FlightScraperException):
    """
    We use this when the website sends weird data.
    Example: We wanted JSON but got HTML.
    """
    pass

class DataExportException(FlightScraperException):
    """
    We use this when we cannot save the file.
    Example: The Excel file is open, or disk is full.
    """
    pass