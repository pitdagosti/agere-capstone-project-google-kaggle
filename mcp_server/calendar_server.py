# ==============================
# calendar_server.py
# ==============================
import os
from flask import Flask, jsonify, request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

app = Flask(__name__)

def get_google_calendar_service():
    try:
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        creds = Credentials(
            token=None,
            refresh_token=os.getenv('GOOGLE_REFRESH_TOKEN'),
            client_id=os.getenv('GOOGLE_CLIENT_ID'),
            client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
            token_uri='https://oauth2.googleapis.com/token',
            scopes=SCOPES
        )
        creds.refresh(Request())
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"Google Calendar auth failed: {e}")
        return None

CALENDAR_SERVICE = get_google_calendar_service()
CALENDAR_ID = os.getenv('CALENDAR_ID')

@app.route('/', methods=['GET'])
def health_check():
    status = "OK" if CALENDAR_SERVICE else "Failed"
    return jsonify({"status": "Server running", "calendar_connection": status, "endpoints": ["/slots", "/book"]}), 200

@app.route('/slots', methods=['GET'])
def get_free_busy_slots():
    if not CALENDAR_SERVICE:
        return jsonify({"error": "Google Calendar service not initialized."}), 500
    time_min = request.args.get('timeMin')
    time_max = request.args.get('timeMax')
    if not time_min or not time_max:
        return jsonify({"error": "timeMin and timeMax required"}), 400
    try:
        body = {"timeMin": time_min, "timeMax": time_max, "items": [{"id": CALENDAR_ID}]}
        result = CALENDAR_SERVICE.freebusy().query(body=body).execute()
        busy_slots = result['calendars'][CALENDAR_ID].get('busy', [])

        free_slots = []
        start = datetime.fromisoformat(time_min.replace('Z', '+00:00'))
        end = datetime.fromisoformat(time_max.replace('Z', '+00:00'))
        slot = start
        while slot + timedelta(hours=1) <= end:
            overlap = any(slot.isoformat() < b['end'] and (slot + timedelta(hours=1)).isoformat() > b['start'] for b in busy_slots)
            if not overlap:
                free_slots.append({"start": slot.isoformat(), "end": (slot + timedelta(hours=1)).isoformat()})
            slot += timedelta(hours=1)

        return jsonify({"calendar_id": CALENDAR_ID, "busy_slots": busy_slots, "free_slots": free_slots}), 200
    except Exception as e:
        print(f"Error in /slots: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/book', methods=['POST'])
def book_interview_slot():
    if not CALENDAR_SERVICE:
        return jsonify({"error": "Google Calendar service not initialized."}), 500
    data = request.get_json()
    start_time = data.get('start')
    end_time = data.get('end')
    summary = data.get('summary', 'Smart-Hire AI Technical Interview')
    candidate_email = data.get('attendee_email')

    try:
        body = {"timeMin": start_time, "timeMax": end_time, "items": [{"id": CALENDAR_ID}]}
        freebusy_result = CALENDAR_SERVICE.freebusy().query(body=body).execute()
        busy_slots = freebusy_result['calendars'][CALENDAR_ID].get('busy', [])
        for b in busy_slots:
            if start_time < b['end'] and end_time > b['start']:
                return jsonify({"status": "failed", "reason": "Slot already booked"}), 409

        event = {
            'summary': summary,
            'location': 'Google Meet (Automatically generated)',
            'description': f'Technical interview for {candidate_email}',
            'start': {'dateTime': start_time, 'timeZone': 'Europe/Rome'},
            'end': {'dateTime': end_time, 'timeZone': 'Europe/Rome'},
            'attendees': []
        }
        if candidate_email:
            event['attendees'].append({'email': candidate_email, 'responseStatus': 'needsAction'})

        event_result = CALENDAR_SERVICE.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        return jsonify({"status": "success", "event_id": event_result['id'], "htmlLink": event_result['htmlLink'], "summary": event_result['summary']}), 201
    except Exception as e:
        print(f"Error in /book: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    if CALENDAR_SERVICE:
        print("MCP Calendar Server started. Connected to Google Calendar.")
        app.run(port=5000, debug=True)
    else:
        print("Unable to start server: Google Calendar authentication failed.")
