import sqlite3
import json

conn = sqlite3.connect("jobs.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM jobs")
for row in cursor.fetchall():
    id, title, company, location, description, responsibilities, skills = row
    skills = json.loads(skills)
    print(title, company, skills)
conn.close()
