# 🧠 AGERE 

### Autonomous Multi-Agent Recruitment Orchestrator

AGERE (**AGE**ntic **RE**cruiter) is a **hierarchical, parallel multi-agent system** designed to automate the most time-consuming steps of the recruiting pipeline: resume screening, technical assessment generation, culture-fit analysis, candidate Q&A, interview scheduling, and communication drafting.
A **Human-in-the-Loop** layer ensures that recruiters retain full control over all sensitive actions.

## The Team

| Name                                                                           | GitHub_ID                                     | Kaggle_ID                                                 |
| ------------------------------------------------------------------------------ | --------------------------------------------- | --------------------------------------------------------- |
| [Pietro D'Agostino](https://www.linkedin.com/in/pietro-d-agostino-phd/)        | [@pitdagosti](https://github.com/pitdagosti)  | [pietrodagostino](https://www.kaggle.com/pietrodagostino) |
| [Abdul Basit Memon](https://www.linkedin.com/in/abdul-basit-memon-614961166/)  | [@abm1119](https://github.com/abm1119)        | [abdulbasit1119](https://www.kaggle.com/abdulbasit1119)   |
| [Amos Bocelli](https://www.linkedin.com/in/amos-bocelli-bab86411a/)            | [@Luminare7](https://github.com/Luminare7)    | [amosboc](https://www.kaggle.com/amosboc)                 |
| [Asterios Terzis](https://www.linkedin.com/in/asterios-terzis-364862277/)      | [@agterzis](https://github.com/agterzis)      | [asteriosterzis](https://www.kaggle.com/asteriosterzis)   |


## ⭐ Core Capabilities

### 1. Hierarchical & Parallel Multi-Agent Architecture

A central **Orchestrator** coordinates specialized agents:

* **ResumeScreenerAgent** – parses PDF resumes and performs baseline match checks
* **TechAssessorAgent** – generates skill-specific coding challenges and validates them using a sandbox
* **CultureFitAgent** – evaluates soft skills and tone
* **QnAAgent** – answers candidate questions via RAG on company documents
* **SchedulerAgent** – books interviews using a real MCP calendar server
* **CommunicatorAgent** – drafts outreach emails containing challenges and proposed slots

The tech, culture, and Q&A analyses run **in parallel** to minimize latency.

## 🔌 Tooling & Infrastructure

### Model Context Protocol (MCP)

A **real MCP server** (SQLite-backed) manages company calendars. The SchedulerAgent communicates via a compliant MCP client.

### Code Execution Sandbox

The TechAssessor uses a secure execution environment to:

1. Generate a coding challenge tailored to the candidate’s claimed skills
2. Validate solvability by executing a reference solution

### Retrieval-Augmented Generation (RAG)

A local vectorstore (FAISS/Chroma recommended) powers the QnAAgent, enabling grounded responses using the documents in `data/company_docs/`.

### Human-in-the-Loop (HITL)

Before any email is sent or action is finalized, the workflow pauses. The recruiter reviews:

* candidate summary
* generated challenge
* suggested email

Approval resumes the agent cycle.

### Observability

All agent reasoning traces, tool calls, and state transitions are logged for debugging and reproducibility.

## 📁 Repository Structure

```
smart-hire-agent/
├── .env                        # API Keys
├── README.md
├── requirements.txt
├── main.py                     # Streamlit UI entrypoint

├── mcp_server/
│   ├── calendar_server.py      # Real MCP server
│   └── calendar.db             # SQLite calendar DB

├── data/
│   ├── resumes/                # Uploaded PDFs
│   └── company_docs/           # RAG knowledge base

├── src/
│   ├── orchestrator.py         # Central coordinator
│   ├── agents/
│   │   ├── screener.py
│   │   ├── tech_assessor.py
│   │   ├── culture_fit.py
│   │   ├── qna_bot.py
│   │   └── scheduler.py
│   ├── tools/
│   │   ├── code_sandbox.py
│   │   ├── file_reader.py
│   │   ├── mcp_client.py
│   │   ├── rag_engine.py
│   │   └── hitl_interface.py
│   ├── memory/
│   │   └── memory_bank.py
│   └── utils/
│       └── logger.py

└── tests/
```

## 🏗️ How It Works (High-Level Flow)

1. Recruiter uploads **resume + job description** via Streamlit
2. Orchestrator starts a session
3. Resume screening runs
4. Parallel block triggers:

   * Tech assessment generation + sandbox execution
   * Culture fit analysis
   * Candidate Q&A prep via RAG
5. SchedulerAgent retrieves available interview slots through MCP
6. CommunicatorAgent drafts the final email
7. **HITL checkpoint:** Recruiter approves or edits
8. Email sent and Memory Bank updated

## 🚀 Running Locally

```
pip install -r requirements.txt
```

Start MCP calendar server:

```
python mcp_server/calendar_server.py
```

Start UI:

```
streamlit run main.py
```

## 📎 Next Steps / Configuration Questions

If you intend to extend or customize this repository, consider:

* preferred vectorstore (local FAISS vs cloud)
* strictness of coding challenge validation
* providing mock resumes + mock policy docs for demos


## 📜 **Source Code License**

The source code and executable distributions are licensed under the **CC BY-SA 4.0**.
See the full text in the [LICENSE](LICENSE) file.


## 📄 **Documentation License**

Documentation in this repository is licensed under:

**Creative Commons Attribution–ShareAlike 4.0 (CC BY-SA 4.0)**

![CC BY-SA 4.0](https://i.creativecommons.org/l/by-sa/4.0/88x31.png)

More info: [https://creativecommons.org/licenses/by-sa/4.0/](https://creativecommons.org/licenses/by-sa/4.0/)


## 🤝 **How to Contribute**

Contributions are welcome!
Please submit a pull request or open an issue for discussion.


## ⭐ **Support the Project**

If you find this project useful, consider giving it a **GitHub star**!
It helps with visibility and supports the authors in the hackathon.
