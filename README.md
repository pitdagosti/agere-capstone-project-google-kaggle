# **Project BOH**

**Project BOH** is the solution developed for the **Agents Intensive – Capstone Project** Hackathon, hosted by **Kaggle** in collaboration with **Google**.
The competition challenges participants to design and implement advanced **AI Agent systems**, integrating reasoning, tool usage, and real-world data interaction to solve complex tasks.

🔗 Hackathon page: [https://www.kaggle.com/competitions/agents-intensive-capstone-project/team](https://www.kaggle.com/competitions/agents-intensive-capstone-project/team)

## 🚀 **Goal of the Project**

> *Add here a 3–6 line description of what your AI agent does.*

* Definition of the problem the agent solves
* Description of the architecture (LLMs, tools, pipelines, data sources)
* Highlight the innovative/unique aspect
* Mention performance, evaluation strategy, or expected outcomes


## The Team behind BOH

| Name                                                                           | GitHub_ID                                     | Kaggle_ID                                                 |
| ------------------------------------------------------------------------------ | --------------------------------------------- | --------------------------------------------------------- |
| [Pietro D'Agostino](https://www.linkedin.com/in/pietro-d-agostino-phd/)        | [@pitdagosti](https://github.com/pitdagosti)  | [pietrodagostino](https://www.kaggle.com/pietrodagostino) |
| [Abdul Basit Memon](https://www.linkedin.com/in/abdul-basit-memon-614961166/)  | [@abm1119](https://github.com/abm1119)        |                                                           |
| [Amos Bocelli](https://www.linkedin.com/in/amos-bocelli-bab86411a/)            | [@Luminare7](https://github.com/Luminare7)    | [amosboc](https://www.kaggle.com/amosboc)                 |
| []()                                                                           | [@agterzis](https://github.com/agterzis)      | [asteriosterzis](https://www.kaggle.com/asteriosterzis)   |

---

# 📁 **Repository Structure**

```
project-root/
│
├── src/                  # Source code of the agent(s)
├── notebooks/            # Experiments, evaluations, prototypes
├── data/                 # Input data, datasets (if allowed)
├── configs/              # Model/agent configuration files
├── tests/                # Unit tests, integration tests
├── docs/                 # Documentation, diagrams, architecture
├── LICENSE               # MIT License for source code
└── README.md             # You're reading it!
```

---

# 🛠️ **Installation**

### **Prerequisites**

* Python 3.10+
* pip or conda
* (Optional) GPU with CUDA for acceleration

### **Setup**

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
pip install -r requirements.txt
```

If you use conda:

```bash
conda create -n boh python=3.10
conda activate boh
pip install -r requirements.txt
```

---

# ▶️ **Usage**

After installation, you can run the main agent pipeline:

```bash
python src/main.py --config configs/default.yaml
```

To test individual modules:

```bash
pytest tests/ --verbose
```

For development mode:

```bash
python -m src.agents.dev_agent
```

---

# 🧠 **Architecture Overview**

> *Add a diagram or a textual summary here.*
> Se vuoi, posso generare un diagramma in ASCII/Markdown o anche un'immagine.

Template per questa sezione:

* Overview of the main agent(s)
* LLM model used (GPT, Gemini, LLaMA, ecc.)
* Tools implemented (search, code execution, data loaders, environment interactions)
* Memory or planning components
* Evaluation loop or reward model (if applicable)

---

# 📊 **Evaluation & Metrics**

> *Optional: fill this when you have results.*

You can include:

* Benchmarks used
* Accuracy / score / leaderboard results
* Qualitative examples of agent reasoning
* Error analysis

---

# 📦 **Deployment (Optional)**

### Local server / API:

```bash
uvicorn src.api:app --reload
```

### Docker:

```bash
docker build -t boh-agent .
docker run boh-agent
```

---

# 📜 **Source Code License**

The source code and executable distributions are licensed under the **MIT License**.
See the full text in the [LICENSE](LICENSE) file.

---

# 📄 **Documentation License**

Documentation in this repository is licensed under:

**Creative Commons Attribution–ShareAlike 4.0 (CC BY-SA 4.0)**

![CC BY-SA 4.0](https://i.creativecommons.org/l/by-sa/4.0/88x31.png)

More info: [https://creativecommons.org/licenses/by-sa/4.0/](https://creativecommons.org/licenses/by-sa/4.0/)

---

# 🤝 **How to Contribute**

Contributions are welcome!
Please submit a pull request or open an issue for discussion.

---

# ⭐ **Support the Project**

If you find this project useful, consider giving it a **GitHub star**!
It helps with visibility and supports the authors in the hackathon.

---

## Vuoi che lo adatti allo stile **Google Research**, **Hugging Face**, **Meta FAIR**, o **OpenAI**?

Oppure se mi mostri anche solo parte del codice, posso scrivere:

* una **descrizione tecnica accurata**,
* un **diagramma dell’architettura**,
* una sezione **Usage** con comandi realistici,
* e una **Project Description** precisa e convincente.

Dimmi pure!
