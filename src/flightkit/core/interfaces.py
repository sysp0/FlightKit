"""
This file has our contracts (interfaces).
Any class that wants to work with flights must follow these rules.
"""

from abc import ABC, abstractmethod
from typing import List

from flightkit.core.models import Flight, SearchCriteria


class IFlightProvider(ABC):
    """
    Contract for flight providers.
    Any class that gets flights must have this method.
    """
    @abstractmethod
    def get_flights(self, criteria: SearchCriteria) -> List[Flight]:
        """
        Gets flights based on search criteria.
        Args:
            criteria: Search criteria object.
        Returns:
            List of Flight objects.
        Raises:
            ProviderException: If any error occurs.
        """
        pass

class IFlightExporter(ABC):
    """
    Contract for exporting flight data.
    """
    
    @abstractmethod
    def export(self, flights: List[Flight], filename: str) -> None:
        """
        Saves flights to a file.
        
        Args:
            flights: List of Flight objects to save.
            filename: Name of the file (e.g., "flights.xlsx").
        """
        pass