# create_jobs_db.py
import sqlite3
import json

# Connessione al DB (verrà creato se non esiste)
conn = sqlite3.connect("jobs.db")
cursor = conn.cursor()

# Creazione tabella jobs
cursor.execute("""
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    company TEXT,
    location TEXT,
    description TEXT,
    responsibilities TEXT,
    skills_required TEXT -- JSON array di skills
)
""")
conn.commit()

# Esempio di job da inserire
job_example = {

    "title": "Machine Learning Engineer – Computer Vision Focus",
    "company": "TechCorp",
    "location": "Remote",
    "description": "We are seeking a Machine Learning Engineer with experience in computer vision. You will design and implement models for image classification and object detection. You will also optimize existing pipelines for performance and scalability.",
    "responsibilities": "\n- Build and train CNN-based models for image recognition. \n- Deploy and optimize ML models for production. \n- Collaborate with data engineers to handle large-scale datasets.",
    "skills_required": ["Python", "PyTorch", "TensorFlow", "OpenCV","PIL", "Flask", "FastAPI", "Docker"]
}

# Inserimento nel DB
cursor.execute("""
INSERT INTO jobs (title, company, location, description, responsibilities, skills_required)
VALUES (?, ?, ?, ?, ?, ?)
""", (
    job_example["title"],
    job_example["company"],
    job_example["location"],
    job_example["description"],
    job_example["responsibilities"],
    json.dumps(job_example["skills_required"])
))
conn.commit()
print("✅ Job inserito nel database.")

conn.close()
