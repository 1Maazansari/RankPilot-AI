# 🚀 RankPilot AI

> **AI-Powered SEO Website Auditor & Optimization Assistant**

RankPilot AI is an intelligent SEO auditing platform that analyzes websites, detects technical and on-page SEO issues, calculates an SEO score, and generates AI-powered recommendations to improve search engine visibility.

Built with **FastAPI**, **Streamlit**, and **Google Gemini**, RankPilot AI combines rule-based SEO analysis with generative AI to deliver actionable insights in seconds.

---

## ✨ Features

### 🔍 Website Analysis
- Website crawling
- Metadata extraction
- Heading structure analysis
- Image SEO analysis
- Internal & external link analysis
- Technical SEO checks
- Robots.txt detection
- Sitemap.xml detection

### 📊 SEO Dashboard
- Overall SEO Score
- Grade Calculation
- Issue Severity Breakdown
- Interactive Analytics Charts
- Website Statistics
- Metadata Overview

### 🤖 AI Recommendations
- Personalized SEO recommendations
- Priority-based improvements
- Estimated implementation effort
- SEO impact analysis
- Actionable optimization suggestions

### ⚡ Technical SEO
- Title Tag Analysis
- Meta Description Analysis
- Canonical URL Validation
- Heading Hierarchy
- Image Alt Text Detection
- Link Analysis
- Robots.txt Validation
- Sitemap Detection

---

## 📸 Screenshots

### Dashboard

> Add a screenshot here

```
docs/dashboard.png
```

### AI Recommendations

> Add a screenshot here

```
docs/recommendations.png
```

### SEO Issues

> Add a screenshot here

```
docs/issues.png
```

---

## 🏗️ Architecture

```text
                User
                  │
                  ▼
        Streamlit Dashboard
                  │
                  ▼
           FastAPI Backend
                  │
      ┌───────────┴───────────┐
      ▼                       ▼
 Website Scanner        SEO Rule Engine
      │                       │
      └───────────┬───────────┘
                  ▼
           Google Gemini AI
                  │
                  ▼
        AI SEO Recommendations
```

---

## 🛠️ Tech Stack

### Frontend
- Streamlit

### Backend
- FastAPI
- Uvicorn

### AI
- Google Gemini

### Web Scraping
- BeautifulSoup4
- Requests
- lxml

### Data Processing
- Pandas

### Visualization
- Plotly

### Language
- Python 3.11+

---

## 📁 Project Structure

```text
RankPilot-AI/

├── backend/
│   ├── api/
│   ├── scanner/
│   ├── seo/
│   ├── ai/
│   └── app.py
│
├── frontend/
│   ├── components/
│   ├── services/
│   ├── styles/
│   └── streamlit_app.py
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/RankPilot-AI.git

cd RankPilot-AI
```

### Create Virtual Environment

```bash
python -m venv .venv
```

Windows

```bash
.venv\Scripts\activate
```

Linux / Mac

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file

```env
GEMINI_API_KEY=YOUR_API_KEY
```

---

## ▶️ Running the Project

### Start FastAPI

```bash
uvicorn app:app --reload
```

Backend

```
http://127.0.0.1:8000
```

---

### Start Streamlit

```bash
streamlit run frontend/streamlit_app.py
```

Frontend

```
http://localhost:8501
```

---

## 📡 API Endpoints

### Health Check

```
GET /
```

Response

```json
{
    "status": "running"
}
```

---

### Analyze Website

```
POST /scan
```

Request

```json
{
    "url":"https://example.com"
}
```

Response

```json
{
    "scan": {},
    "seo": {},
    "ai": {}
}
```

---

## 📊 Workflow

```text
Enter Website URL
        │
        ▼
Website Scanner
        │
        ▼
SEO Rule Engine
        │
        ▼
Score Calculation
        │
        ▼
Gemini AI Analysis
        │
        ▼
Dashboard Visualization
```

---

## 🚀 Future Roadmap

### ✅ Version 1 (Completed)

- Website Scanner
- SEO Analysis
- Technical SEO
- Dashboard
- AI Recommendations
- SEO Score
- Charts
- Issue Detection

### 🔄 Version 2

- PDF SEO Reports
- Scan History
- Website Comparison
- Multi-page Crawling
- AI SEO Chat Assistant
- Export Reports
- Scheduled Website Monitoring

### 🤖 Version 3

- SEO Planner Agent
- Technical SEO Agent
- Content Optimization Agent
- Auto Fix Suggestions
- WordPress Integration
- Shopify Integration
- Team Dashboard

---

## 🤝 Contributing

Contributions are welcome!

Feel free to fork the repository, open issues, or submit pull requests to improve RankPilot AI.

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Maaz Ansari**

- GitHub: https://github.com/1Maazansari
- LinkedIn: https://linkedin.com/in/maazansari-ml

---

⭐ If you found this project useful, consider giving it a star!
