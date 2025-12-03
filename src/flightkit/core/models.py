from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from .exceptions import FlightValidationException

class SearchCriteria(BaseModel):
    """
    This class holds the search info.
    It tells us where and when to fly.
    """
    origin: str = Field(..., min_length=2, description="City code or name (Start)")
    destination: str = Field(..., min_length=2, description="City code or name (End)")
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Date like YYYY-MM-DD")
    
    @field_validator('origin', 'destination')
    @classmethod
    def to_upper(cls, v: str) -> str:
        """
        Changes city name to uppercase letters.
        Example: 'tehran' -> 'TEHRAN'
        """
        return v.upper()


class Flight(BaseModel):
    """
    This is our standard flight object.
    We convert website data to this format.
    """
    airline_name: str
    flight_number: str
    departure_time: datetime
    arrival_time: datetime
    price: int = Field(gt=0, description="Price must be more than 0")
    capacity: int = Field(ge=0, description="Capacity cannot be negative")
    origin: str
    destination: str
    
    # [TODO] Add more fields as needed
    # aircraft_type: Optional[str] = None
    # is_charter: bool = False

    @model_validator(mode='after')
    def check_flight_duration(self) -> 'Flight':
        """
        Checks if the time makes sense.
        You cannot arrive before you leave!
        """
        if self.arrival_time < self.departure_time:
            # We use our custom error here
            raise FlightValidationException(
                f"Arrival time ({self.arrival_time}) cannot be before departure time ({self.departure_time})."
            )
        return self

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S") # save datetime in JSON correctly
        }