import os
from flask import Flask, jsonify, request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from dotenv import load_dotenv
from datetime import datetime, timedelta
from dateutil import parser

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

app = Flask(__name__)

# --- Google Calendar Configuration and Authentication ---

def get_google_calendar_service():
    """
    Create the service object for the Google Calendar API using the Refresh Token.
    """
    try:
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        credentials = Credentials(
            token=None,
            refresh_token=os.getenv('GOOGLE_REFRESH_TOKEN'),
            client_id=os.getenv('GOOGLE_CLIENT_ID'),
            client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
            token_uri='https://oauth2.googleapis.com/token',
            scopes=SCOPES
        )
        credentials.refresh(Request())
        service = build('calendar', 'v3', credentials=credentials)
        return service
    except Exception as e:
        print(f"Error during Google Calendar authentication: {e}")
        return None

CALENDAR_SERVICE = get_google_calendar_service()
CALENDAR_ID = os.getenv('CALENDAR_ID')

# --- Endpoints ---

@app.route('/', methods=['GET'])
def health_check():
    """Verify server is running and connected to Google Calendar."""
    if CALENDAR_SERVICE:
        return jsonify({
            "status": "Server running",
            "calendar_connection": "OK",
            "endpoints": ["/slots", "/book"]
        }), 200
    else:
        return jsonify({
            "status": "Server running",
            "calendar_connection": "Failed. Check .env and credentials."
        }), 500

@app.route('/slots', methods=['GET'])
def get_free_busy_slots():
    """Return busy slots in a given interval."""
    if not CALENDAR_SERVICE:
        return jsonify({"error": "Google Calendar service not initialized."}), 500

    time_min_str = request.args.get('timeMin')
    time_max_str = request.args.get('timeMax')

    if not time_min_str or not time_max_str:
        return jsonify({"error": "timeMin and timeMax parameters are required."}), 400

    try:
        body = {"timeMin": time_min_str, "timeMax": time_max_str, "items": [{"id": CALENDAR_ID}]}
        result = CALENDAR_SERVICE.freebusy().query(body=body).execute()
        busy_slots = result['calendars'][CALENDAR_ID].get('busy', [])
        return jsonify({"calendar_id": CALENDAR_ID, "busy_slots": busy_slots}), 200
    except Exception as e:
        print(f"Error during free/busy query: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/book', methods=['POST'])
def book_interview_slot():
    """Create a new event if the slot is free."""
    if not CALENDAR_SERVICE:
        return jsonify({"error": "Google Calendar service not initialized."}), 500

    data = request.get_json()
    start_time_str = data.get('start')
    end_time_str = data.get('end')
    summary = data.get('summary', 'Smart-Hire AI Technical Interview')
    candidate_email = data.get('attendee_email', None)

    # Convert strings to datetime objects
    try:
        start_dt = parser.isoparse(start_time_str)
        end_dt = parser.isoparse(end_time_str)
    except Exception as e:
        return jsonify({"status": "failed", "reason": f"Invalid datetime format: {e}"}), 400

    # Check for conflicts
    try:
        body = {"timeMin": start_time_str, "timeMax": end_time_str, "items": [{"id": CALENDAR_ID}]}
        freebusy_result = CALENDAR_SERVICE.freebusy().query(body=body).execute()
        busy_slots = freebusy_result['calendars'][CALENDAR_ID].get('busy', [])

        for b in busy_slots:
            busy_start = parser.isoparse(b['start'])
            busy_end = parser.isoparse(b['end'])
            if start_dt < busy_end and end_dt > busy_start:
                return jsonify({"status": "failed", "reason": "Slot already booked"}), 409

        # Build event
        event = {
            'summary': summary,
            'location': 'Google Meet (Automatically generated)',
            'description': f'Technical interview for {candidate_email}',
            'start': {'dateTime': start_time_str, 'timeZone': 'Europe/Rome'},
            'end': {'dateTime': end_time_str, 'timeZone': 'Europe/Rome'},
            'attendees': [{'email': CALENDAR_ID}]
        }
        if candidate_email:
            event['attendees'].append({'email': candidate_email, 'responseStatus': 'needsAction'})

        event_result = CALENDAR_SERVICE.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        return jsonify({
            "status": "success",
            "event_id": event_result['id'],
            "htmlLink": event_result['htmlLink'],
            "summary": event_result['summary']
        }), 201

    except Exception as e:
        print(f"Error while inserting event: {e}")
        return jsonify({"error": str(e)}), 500

# --- Server start ---
if __name__ == '__main__':
    if CALENDAR_SERVICE:
        print("MCP Calendar Server started. Connected to Google Calendar.")
        app.run(port=5000, debug=True)
    else:
        print("Unable to start server: Google Calendar authentication failed.")
