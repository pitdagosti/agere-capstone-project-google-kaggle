# ==============================
# mcp_client.py
# ==============================
import requests
from datetime import datetime
from typing import List, Dict, Optional, Any

BASE_URL = "http://127.0.0.1:5000"

class CalendarClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        print(f"CalendarClient initialized for URL: {self.base_url}")

    def _validate_iso(self, dt_str: str) -> bool:
        try:
            datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            return True
        except ValueError:
            return False

    def get_busy_slots(self, time_min: str, time_max: str) -> Optional[List[Dict[str, str]]]:
        if not self._validate_iso(time_min) or not self._validate_iso(time_max):
            print(f"Invalid ISO datetime: {time_min}, {time_max}")
            return None
        endpoint = f"{self.base_url}/slots"
        params = {'timeMin': time_min, 'timeMax': time_max}
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            return response.json().get('busy_slots', [])
        except requests.exceptions.RequestException as e:
            print(f"GET /slots failed: {e}")
            return None

    def book_slot(self, start_time: str, end_time: str, candidate_email: str, summary: str = "Smart-Hire AI Technical Interview") -> Optional[Dict[str, Any]]:
        if not self._validate_iso(start_time) or not self._validate_iso(end_time):
            print(f"Invalid ISO datetime: {start_time}, {end_time}")
            return None
        endpoint = f"{self.base_url}/book"
        payload = {
            "start": start_time,
            "end": end_time,
            "summary": summary,
            "attendee_email": candidate_email
        }
        try:
            response = requests.post(endpoint, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"POST /book failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Server response: {e.response.text}")
            return None
