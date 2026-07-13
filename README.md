# AI Skills Radar

[![Python](https://img.shields.io/badge/Python-3.12-blue)]()
[![Streamlit](https://img.shields.io/badge/Streamlit-Live-red)]()
[![AWS EC2](https://img.shields.io/badge/AWS-EC2-orange)]()
[![SQLite](https://img.shields.io/badge/SQLite-Database-blue)]()

> An end-to-end AI job market intelligence platform that analyzes Australian AI & Data job postings to identify in-demand skills, hiring trends, salary insights, and market demand.

## Live Demo

https://ai-skills-radar-rewa.streamlit.app/

## Deployment

**Public Demo**
- Streamlit Community Cloud

**Production Deployment**
- AWS EC2
- Ubuntu Linux
- Nginx Reverse Proxy
- systemd Service
- Elastic IP

---

# Overview

AI Skills Radar automatically collects Australian AI and Data job postings, extracts technical skills using a hybrid Dictionary + Local LLM pipeline, filters irrelevant roles, and presents interactive market intelligence through a Streamlit dashboard.

The platform answers questions such as:

- Which AI skills are currently most in demand?
- Which companies are hiring the most?
- Which Australian cities have the highest demand?
- What salary ranges are employers offering?
- Which skills are trending over time?
- What proportion of jobs are Junior, Mid, and Senior level?

---

# Project Highlights

- End-to-end AI job market intelligence platform
- Hybrid Dictionary + Local LLM skill extraction
- AI/Data role relevance classification
- Seniority detection
- Interactive Streamlit dashboard
- Historical skill trend tracking
- Public deployment on Streamlit Community Cloud
- Production deployment on AWS EC2

---

# Dashboard Preview

## Dashboard Overview

![Dashboard Overview](screenshots/dashboard-overview.png)

---

## Market Intelligence

![Market Intelligence](screenshots/market-insights.png)

---

## Skills & Job Explorer

![Skills & Job Explorer](screenshots/details-table.png)

---

# Key Features

### Data Collection

- Collects live Australian AI & Data job postings from the Adzuna Jobs API
- Stores structured job data in SQLite
- Supports repeated data collection for updated market insights

### AI Skill Extraction

- Hybrid Dictionary + Local LLM (Qwen via Ollama)
- Technical skill normalization
- Duplicate skill removal
- Alias mapping

### Intelligent Classification

- Relevant vs irrelevant AI/Data role classification
- Junior, Mid and Senior role detection

### Interactive Dashboard

- Market overview
- Top in-demand technical skills
- Hiring companies
- Hiring locations
- Salary insights
- Historical skill trends
- CSV export

---

# Tech Stack

| Category | Technologies |
|-----------|--------------|
| Programming Language | Python 3 |
| Data Processing | Pandas |
| Database | SQLite |
| Dashboard | Streamlit |
| Visualization | Plotly |
| Local LLM | Ollama + Qwen 2.5 7B |
| Job API | Adzuna Jobs API |
| Public Hosting | Streamlit Community Cloud |
| Cloud Deployment | AWS EC2 (Ubuntu Linux) |
| Reverse Proxy | Nginx |
| Process Manager | systemd |
| Version Control | Git & GitHub |

---

# Project Architecture

```text
                    Adzuna Jobs API
                           │
                           ▼
                  fetch_jobs.py
                           │
                           ▼
                    SQLite Database
                           │
            ┌──────────────┴──────────────┐
            │                             │
            ▼                             ▼
     extract_skills.py          save_snapshot.py
 (Dictionary + Local LLM)    Historical Skill Tracking
            │
            ▼
       analytics.py
            │
            ▼
     Streamlit Dashboard
            │
            ▼
  Streamlit Cloud / AWS EC2
```

---

# Data Pipeline

1. Fetch live AI & Data job postings from the Adzuna Jobs API.
2. Store raw job postings in SQLite.
3. Match predefined technical skills using a curated dictionary.
4. Use a local Qwen model via Ollama to:
   - Extract additional technical skills
   - Classify seniority
   - Determine job relevance
5. Merge and normalize extracted skills.
6. Store enriched results back into SQLite.
7. Generate daily historical snapshots.
8. Display interactive market intelligence through Streamlit.

---

# Cloud Deployment

## Streamlit Community Cloud

The public dashboard is deployed on Streamlit Community Cloud.

Live Demo:

https://ai-skills-radar-rewa.streamlit.app/

---

## AWS EC2

The project was also deployed using a production-style AWS environment featuring:

- Ubuntu Linux
- Nginx Reverse Proxy
- systemd Service
- Elastic IP
- Python Virtual Environment
- SSH Deployment

This deployment demonstrates Linux server administration, cloud deployment and production web application hosting.

---

# Project Structure

```text
ai-skills-radar/
│
├── app.py
├── analytics.py
├── extract_skills.py
├── fetch_jobs.py
├── save_snapshot.py
├── reextract_empty_skills.py
├── sample_job_postings.db
├── requirements.txt
├── .env.example
├── screenshots/
│   ├── dashboard-overview.png
│   ├── market-insights.png
│   └── details-table.png
└── README.md
```

---

# Installation

Clone the repository

```bash
git clone https://github.com/rewa-d/ai-skills-radar.git
cd ai-skills-radar
```

Create a virtual environment

```bash
python -m venv venv
```

Activate it

### Windows

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file:

```env
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key
```

---

# Running the Project

Fetch job postings

```bash
python fetch_jobs.py
```

Extract skills

```bash
python extract_skills.py
```

Save historical snapshots

```bash
python save_snapshot.py
```

Launch the dashboard

```bash
streamlit run app.py
```

---

# Dashboard Features

- AI & Data job market overview
- Top technical skills
- Seniority distribution
- Relevant vs irrelevant role analysis
- Hiring company insights
- Hiring location insights
- Salary analytics
- Historical skill trends
- Download filtered job listings

---

# Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| LLM responses occasionally returned malformed JSON | Implemented retry logic and validation. |
| Duplicate skills from dictionary and LLM extraction | Added normalization, alias mapping and deduplication. |
| Generic AI terms reduced dashboard quality | Added filtering and validation rules. |
| Non-technical roles appeared in results | Implemented LLM-based relevance classification. |
| Historical trend analysis | Added daily SQLite snapshots. |
| Cloud deployment | Deployed using Streamlit Community Cloud and AWS EC2. |

---

# Skills Demonstrated

- Python
- SQL
- SQLite
- Pandas
- Streamlit
- Plotly
- Prompt Engineering
- Local LLM Integration
- Ollama
- REST API Integration
- AWS EC2
- Ubuntu Linux
- Nginx
- systemd
- Git
- GitHub
- Data Visualization
- Cloud Deployment

---

# Future Improvements

- Automated daily job refresh
- Docker containerization
- GitHub Actions CI/CD
- HTTPS with Let's Encrypt
- Multi-country job analysis
- Semantic skill clustering
- Skill demand forecasting
- REST API
- User authentication

---

# About

This project was built as part of my portfolio while pursuing a **Master of Artificial Intelligence at RMIT University**. It demonstrates end-to-end AI application development—from collecting live job data and LLM-powered skill extraction to interactive visualization and deployment on both Streamlit Community Cloud and AWS EC2.

---

# Author

**Rewa Dambal**

Master of Artificial Intelligence  
RMIT University

- GitHub: https://github.com/rewa-d
- LinkedIn: https://www.linkedin.com/in/rewa-dambal

---

# Support

If you found this project useful or interesting, consider starring the repository.