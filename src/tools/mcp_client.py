import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

# BASE URL of the server (the one you started)

BASE_URL = "http://127.0.0.1:5000"

class CalendarClient:
    """
    Client to interact with the Real MCP Calendar Server via REST API.
    Provides methods to query free/busy slots and book appointments.
    """

    def __init__(self, base_url: str = BASE_URL):
        """
        Initializes the client with the server's base URL.
        """
        self.base_url = base_url
        print(f"CalendarClient initialized for URL: {self.base_url}")


    def get_busy_slots(self, time_min: str, time_max: str) -> Optional[List[Dict[str, str]]]:
        """
        Calls the GET /slots endpoint to retrieve BUSY slots
        within the specified time range.

        Args:
            time_min (str): Lower bound of the interval (ISO 8601, e.g., 2025-11-20T09:00:00Z).
            time_max (str): Upper bound of the interval (ISO 8601).

        Returns:
            Optional[List[Dict[str, str]]]: A list of busy slots or None in case of error.
        """
        endpoint = f"{self.base_url}/slots"
        
        # GET parameters are passed as query string
        params = {
            'timeMin': time_min,
            'timeMax': time_max
        }
        
        try:
            print(f"GET request to {endpoint} with params: {params}")
            response = requests.get(endpoint, params=params)
            response.raise_for_status()  # Raise exception for 4xx/5xx status codes
            
            data = response.json()
            
            # Server returns busy_slots
            return data.get('busy_slots')

        except requests.exceptions.RequestException as e:
            print(f"Error in request to /slots: {e}")
            return None


    def book_slot(self, start_time: str, end_time: str, candidate_email: str, summary: str = "Smart-Hire AI Technical Interview") -> Optional[Dict[str, Any]]:
        """
        Calls the POST /book endpoint to create a new event.

        Args:
            start_time (str): Event start time (ISO 8601).
            end_time (str): Event end time (ISO 8601).
            candidate_email (str): Candidate's email to invite.
            summary (str): Event title.

        Returns:
            Optional[Dict[str, Any]]: Details of the created event or None in case of error.
        """
        endpoint = f"{self.base_url}/book"
        
        # POST body is passed as JSON
        payload = {
            "start": start_time,
            "end": end_time,
            "summary": summary,
            "attendee_email": candidate_email
        }
        
        try:
            print(f"POST request to {endpoint} with payload: {payload}")
            response = requests.post(endpoint, json=payload)
            response.raise_for_status()  # Raise exception for 4xx/5xx status codes
            
            # Return the JSON with event details
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Error in request to /book: {e}")
            # If response is available, print body for debug
            response = getattr(e, 'response', None)
            if response is not None and response.text:
                print(f"Server response (error): {response.text}")
            return None