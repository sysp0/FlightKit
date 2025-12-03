import uuid
import requests
from typing import List, Dict
from datetime import datetime
from pydantic_core import ValidationError as PydanticValidationError

from flightkit.core.interfaces import IFlightProvider
from flightkit.core.models import Flight, SearchCriteria
from flightkit.utils import logger


class UtravsProvider(IFlightProvider):

    BASE_URL = "https://api.utravs.com"

    def __init__(self):
        logger.debug("Initializing UtravsProvider and configuring session.")
        self._session = requests.Session()
        self._is_authenticated = False
        self._configure_session()

    def get_flights(self, criteria: SearchCriteria) -> List[Flight]:
        logger.debug("Requested flights for %s -> %s at %s",
                     criteria.origin, criteria.destination, criteria.date)
        if not self._is_authenticated:
            logger.debug("Session not authenticated. Calling _authenticate().")
            self._authenticate()
        raw_data = self._fetch_raw_flights(criteria)
        return self._map_response_to_flights(raw_data, criteria)

    def _configure_session(self):
        logger.debug("Setting default headers for Utravs session.")
        self._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:145.0) Gecko/20100101 Firefox/145.0',
            'Content-Type': 'application/json',
            'Origin': 'https://utravs.com',
            'Referer': 'https://utravs.com/',
            'tenantKey': 'C7B37B5A-2EAC-4681-A83C-C27C90C58D42',
            'projectId': '1',
        })

    def _authenticate(self):
        url = f"{self.BASE_URL}/v2/auth/Authentication/AppInit"
        headers = {'TraceId': str(uuid.uuid4()), 'Time-Zone': 'Asia/Tehran'}
        payload = {"appType": 3, "appVersion": 1}
        logger.debug("Authenticating against %s with payload %s", url, payload)

        resp = self._session.post(url, json=payload, headers=headers)
        resp.raise_for_status()

        session_key = resp.json().get('result', {}).get('sessionKey')
        logger.debug("Received session key: %s", session_key)
        self._session.cookies.set('_session', session_key)
        self._is_authenticated = True
        logger.debug("Authentication successful. Session is now authenticated.")

    def _fetch_raw_flights(self, criteria: SearchCriteria) -> Dict:
        url = f"{self.BASE_URL}/v3/flight/domestic/availability"
        payload = {
            "adultCount": 1,
            "childCount": 0,
            "infantCount": 0,
            "departureDate": criteria.date,
            "origin": criteria.origin,
            "destination": criteria.destination,
            "isTour": False
        }
        headers = {'TraceId': str(uuid.uuid4()), 'Time-Zone': 'Asia/Tehran'}
        logger.debug("Fetching flights from %s with payload %s", url, payload)

        response = self._session.post(url, json=payload, headers=headers)
        response.raise_for_status()
        logger.debug("Received raw response for flights.")
        return response.json()

    def _map_response_to_flights(self, raw_data: Dict, criteria: SearchCriteria) -> List[Flight]:
        flights = []
        raw_flights_list = raw_data.get("result", {}).get("departingFlights", [])
        logger.debug("Mapping %d raw flights to Flight objects.", len(raw_flights_list))

        for idx, item in enumerate(raw_flights_list, start=1):
            try:
                flight = Flight(
                    airline_name=item["airlineName"],
                    flight_number=item["flightNumber"],
                    departure_time=datetime.fromisoformat(item["departureDateTime"]),
                    arrival_time=datetime.fromisoformat(item["arrivalDateTime"]),
                    price=int(item["adultPrice"]),
                    capacity=int(item["capacity"]),
                    origin=criteria.origin,
                    destination=criteria.destination
                )
                flights.append(flight)
                logger.debug("Flight #%d mapped successfully: %s", idx, flight)

            except PydanticValidationError as e:
                logger.debug("Skipping invalid flight data at index %d: %s", idx, e)
                continue

            except (KeyError, ValueError) as e:
                logger.debug("Skipping bad flight data at index %d due to %s", idx, e)
                continue

        logger.debug("Finished mapping flights. Total valid flights: %d", len(flights))
        return flights