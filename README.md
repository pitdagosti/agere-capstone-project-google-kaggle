# **PROJECT AGERE (Agentic Recruiter) - Google x Kaggle**

AGERE (**AGE**ntic **RE**cruiter) is an **AI-powered interview assistant** built with Google's Agent Development Kit (ADK) and Gemini 2.5 models. It guides job candidates through every step of the application process: analyzing CVs, matching candidates to jobs, validating technical skills through automated coding assessments, assessing language proficiency, and scheduling live interviews.

> 🏆 **[Kaggle x Google Agents Intensive Capstone Project](https://www.kaggle.com/competitions/agents-intensive-capstone-project/overview#how-do-i-make-a-submission)**
> **Helping job candidates ace interviews with precision, confidence, and structure.**

## Click to watch the video presentation!

<p align="center">
<a href="https://www.youtube.com/watch?v=pnCnia1M5jQ">
  <img src="https://github.com/user-attachments/assets/4479c4b6-67cb-4f98-8675-4b21c0bc10e6" alt="AGERE" width="600"/>
</a>
</p>

---

## 🚨 Problem Statement

Preparing for technical interviews is often stressful and inefficient due to:

* Fragmented solutions with **no end-to-end support** from resume to interview.
* Limited **personalized feedback** on skills, coding, and language proficiency.
* Difficulty in **validating technical solutions** in coding, ML, and system design.
* Time-consuming preparation without guidance on where to focus.

AGERE solves these problems by orchestrating **specialized AI agents** in a structured workflow, providing interactive, automated guidance throughout the candidate journey.

---

## 🤖 What is AGERE?

AGERE is a **multi-agent orchestration system** that automates candidate preparation across six sequential steps:

1.  **CV Analysis:** Reads and parses CVs, extracting skills, experience, education, and languages.
2.  **Job Matching:** Recommends suitable job openings from a local database based on extracted skills.
3.  **Coding Assessment:** Presents tailored coding problems, executes submissions in a secure sandbox, and provides automatic pass/fail evaluation.
4.  **Language Assessment:** Generates and evaluates a conversational test in a candidate's non-English language (if applicable).
5.  **Interview Scheduling:** Finds available slots and books live interviews via Google Calendar, handling tokens, conflicts, and time zones.
6.  **End-to-End Orchestration:** Ensures tasks are executed sequentially (CV → Job → Coding → Language → Scheduling) for a structured candidate journey.

---

## 🏗️ Architecture

AGERE implements a **hierarchical multi-agent architecture** powered by Google’s ADK and Gemini 2.5 models.

```mermaid
graph TB
    UI[🖥️ Streamlit UI<br/>Interactive Frontend]
    ORCH[🎯 Orchestrator Agent<br/>LLM Manager<br/>Gemini 2.5]

    subgraph "Specialized Agents"
        CV[📄 CV Analysis Agent<br/>Reads & parses resumes<br/>Gemini 2.5]
        JOB[🔍 Job Matching Agent<br/>Matches candidates to jobs<br/>Gemini 2.5]
        CODE[⚙️ Code Assessment Agent<br/>Evaluates coding assignments<br/>Gemini 2.5]
        LANG[🌐 Language Assessment Agent<br/>Generates & evaluates language tests<br/>Gemini 2.5]
        CAL[📅 Calendar Agent<br/>Manages interview scheduling<br/>Gemini 2.5]
    end

    subgraph "Custom Tools Layer"
        CVTOOLS[📂 CV Tools<br/>read_cv<br/>list_available_cvs<br/>compare_candidates]
        JOBTOOLS[📋 Job Tools<br/>list_jobs_from_db]
        SANDBOX[🖥️ Code Sandbox<br/>execute_code<br/>run_code_assignment]
        CALTOOLS[📆 Calendar Tools<br/>calendar_get_busy<br/>calendar_book_slot]
    end

    subgraph "External Services"
        GCAL[📆 Google Calendar<br/>OAuth2 Integration]
        JOBDB[💾 Jobs SQLite DB]
    end

    UI <--> ORCH
    ORCH --> CV
    ORCH --> JOB
    ORCH --> CODE
    ORCH --> LANG
    ORCH --> CAL

    CV --> CVTOOLS
    JOB --> JOBTOOLS
    CODE --> SANDBOX
    CAL --> CALTOOLS

    JOBTOOLS -.-> JOBDB
    CALTOOLS <--> GCAL

    style UI fill:#667eea,stroke:#333,stroke-width:2px,color:#fff
    style ORCH fill:#764ba2,stroke:#333,stroke-width:3px,color:#fff
    style CV fill:#f093fb,stroke:#333,stroke-width:2px,color:#333
    style JOB fill:#f093fb,stroke:#333,stroke-width:2px,color:#333
    style CODE fill:#f093fb,stroke:#333,stroke-width:2px,color:#333
    style LANG fill:#f093fb,stroke:#333,stroke-width:2px,color:#333
    style CAL fill:#f093fb,stroke:#333,stroke-width:2px,color:#333
    style GCAL fill:#34a853,stroke:#333,stroke-width:2px,color:#fff
    style JOBDB fill:#ffb347,stroke:#333,stroke-width:2px,color:#333
````

-----

## 📁 Project Structure

```
agere-capstone-project-google-kaggle/
├── main.py                    # Streamlit App
├── requirements.txt
├── .env / env.example          # Configuration file
├── README.md
│
├── src/
│   ├── agents/
│   │   └── agents.py          # Orchestrator + Specialized Agents
│   ├── tools/
│   │   ├── tools.py           # CV operations & custom tools
│   │   ├── code_sandbox.py    # Sandboxed code execution
│   │ 
│   └── styles/custom.css
│
├── jobs/
│   ├── jobs.db                # SQLite job listings
│   ├── jobs_db.py
```

-----

## 🔧 Installation & Setup

### 1\. Clone & Create Environment

```bash
git clone [https://github.com/pitdagosti/agere-capstone-project-google-kaggle.git](https://github.com/pitdagosti/agere-capstone-project-google-kaggle.git)
cd agere-capstone-project-google-kaggle
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate     # Windows PowerShell
pip install --upgrade pip
pip install -r requirements.txt
```

### 2\. Setup Environment Variables

AGERE requires essential API credentials for the Gemini model and Google Calendar integration.

```bash
python -m spacy download en_core_web_sm
# Copy the template file to create your local .env file
cp env.example .env 
```

**Crucially, you must edit the newly created `.env` file and replace the placeholder values (`your_..._here`) with your actual credentials:**

  * `GOOGLE_API_KEY`: Your key to access the Gemini 2.5 models.
  * **Google Calendar OAuth Credentials**: Follow Step 3 below to obtain the `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_REFRESH_TOKEN`.
  * `CALENDAR_ID`: The email address of the calendar AGERE should use for scheduling (e.g., `recruiter@company.com`).

### 3\. Google Calendar OAuth Credentials Setup

The Calendar Agent requires the **Refresh Token** for non-interactive, long-term (offline) access. Follow these steps carefully to generate your credentials:

#### A. Google Cloud Console Setup (Client ID & Secret)

1.  **Enable API:** Go to the [Google Cloud Console](https://console.cloud.google.com/), create/select a project, and enable the **Google Calendar API**.
2.  **Consent Screen:** Navigate to **APIs & Services \> OAuth consent screen**. Configure your app details and add the scope **`https://www.googleapis.com/auth/calendar`** (required for booking).
3.  **Credentials:** Navigate to **APIs & Services \> Credentials**. Click **+ CREATE CREDENTIALS** and choose **OAuth client ID**.
4.  Select **Web application** as the type. Add `http://localhost` to the **Authorized redirect URIs** (required for the next step).
5.  Save the resulting values: **`GOOGLE_CLIENT_ID`** and **`GOOGLE_CLIENT_SECRET`**.

#### B. Generating the Refresh Token (`GOOGLE_REFRESH_TOKEN`)

1.  Go to the **[Google OAuth 2.0 Playground](https://developers.google.com/oauthplayground)**.
2.  Click the **gear icon (⚙️)**, check **"Use your own OAuth credentials,"** and input your `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`.
3.  In **Step 1**, select the Calendar scope: **`https://www.googleapis.com/auth/calendar`**. Click **Authorize APIs**.
4.  After signing in with the Google Account whose calendar AGERE will manage, you will be redirected to **Step 2**.
5.  Click **Exchange authorization code for tokens**. The resulting JSON will contain the long-lived **`refresh_token`**.
6.  Copy this token and paste it into your `.env` file as the value for **`GOOGLE_REFRESH_TOKEN`**.

### 4\. Launch Streamlit UI

```bash
streamlit run main.py
```

-----

## 👥 Team

| Name | GitHub | Kaggle | LinkedIn |
| :--- | :--- | :--- | :--- |
| Pietro D'Agostino | [@pitdagosti](https://github.com/pitdagosti) | [pietrodagostino](https://www.kaggle.com/pietrodagostino) | [LinkedIn](https://www.linkedin.com/in/pietro-d-agostino-phd/) |
| Abdul Basit Memon | [@abm1119](https://github.com/abm1119) | [abdulbasit1119](https://www.kaggle.com/abdulbasit1119) | [LinkedIn](https://www.linkedin.com/in/abdul-basit-memon-614961166/) |
| Amos Bocelli | [@Luminare7](https://github.com/Luminare7) | [amosboc](https://www.kaggle.com/amosboc) | [LinkedIn](https://www.linkedin.com/in/amos-bocelli-bab86411a/) |
| Asterios Terzis | [@agterzis](https://github.com/agterzis) | [asteriosterzis](https://www.kaggle.com/asteriosterzis) | [LinkedIn](https://www.linkedin.com/in/asterios-terzis-364862277/) |

-----

## 📜 License

**CC BY-SA 4.0** for code and documentation.
[More info](https://creativecommons.org/licenses/by-sa/4.0/)

-----

## 🤝 Contributing

We welcome community contributions\!

  * Bug reports & feature requests via GitHub Issues.
  * Pull requests for new features, bug fixes, or improvements.
  * Maintain code readability and follow existing architecture patterns.

-----

<div align="center"\>

## 🏆 Built for Kaggle x Google Agents Intensive Hackathon

**PROJECT AGERE – Your AI-Powered Career Coach**

*Prepare faster, practice smarter, and approach every interview with confidence.*

[📖 Documentation](https://github.com/pitdagosti/agere-capstone-project-google-kaggle/main/README.md) • [🐛 Report Bug](https://github.com/pitdagosti/agere-capstone-project-google-kaggle/issues) • [💡 Request Feature](https://github.com/pitdagosti/agere-capstone-project-google-kaggle/issues)
