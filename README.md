# Jobcadence &bull; Career Pivot Coach (PS 25)

> An intelligent, closed-loop career transition architect that bridges the gap between your current software engineering experience and high-demand roles like **Applied AI Engineer**.

Built for **Hackathon Problem Statement 25**.

---

## 🚀 Key Features

1. **AI Skill Gap Intake (`/intake`):**
   - Parses resume text or uploaded PDF resumes using server-side `pypdf`.
   - Analyzes target roles and job descriptions to extract missing technical competencies and compute baseline **Role Match %**.
   - Includes 1-click **"Load Sample Career Pivot"** (*React Developer &rarr; Applied AI Engineer*).

2. **Closed-Loop Transition Dashboard (`/dashboard`):**
   - Live metrics: **Role Match %**, **Target Readiness**, and **Active Streak**.
   - Interactive `<LearningCurve />` visualization displaying milestone progress across sprints.
   - Dynamic 4-Week Recalibrated Roadmap with tasks and concrete milestones.
   - **Roadmap Recalibrated Alert Banner** that triggers whenever mock interview performance requires remedial adjustment.

3. **Scenario Mock Interview & 4-Dimension Rubric (`/verify-skills`):**
   - Pre-populated with missing skills identified in the gap analysis.
   - Server-side Gemini generation of scenario-based technical questions.
   - Rigorous grading across 4 dimensions: *Technical Accuracy*, *Practical Depth*, *Edge Case Reasoning*, and *Communication Clarity*.
   - **Closed-Loop Recalibration Rule:**
     - Score &lt; 70%: Automatically prepends a tailored remediation module to **Week 1** of your roadmap.
     - Score &ge; 70%: Awards +5% to Role Match and issues an AI-Verified Skill Badge.

4. **Portfolio Proof Projects (`/projects`):**
   - Hands-on, production-grade deliverables proving practical competence (e.g., Enterprise Hybrid RAG, Self-Correcting Code Agent).
   - Marking a project complete adds **+7%** to Match Score and awards a verified badge.

5. **Application Funnel Analytics (`/applications`):**
   - Compare callback velocity across targeted resume variants (e.g., *Applied AI Engineer* vs. *Full-Stack AI*).
   - Generates executive strategic intel highlighting optimal positioning.

---

## 🛠️ Tech Stack

- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui, Framer Motion, Recharts
- **State Management:** Single unified `CareerContext` synced to `localStorage` (`career_pivot_state`)
- **Backend:** FastAPI, Python 3.12, `google-genai` SDK (`gemini-2.5-flash` / `gemini-3.8-flash`), `pydantic` v2, `pypdf`, `uvicorn`

---

## ⚙️ Quickstart

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
# source venv/bin/activate

pip install -r requirement.txt
# Copy .env.example to .env and add your GEMINI_API_KEY
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Frontend Setup
```bash
npm install
npm run dev
```
Open [http://localhost:8080](http://localhost:8080) in your browser.

---

## 📜 Backend API Endpoints

- `POST /analyze-gap` &bull; Resume &amp; JD gap analysis &rarr; structured `SkillGapReport`
- `POST /generate-questions` &bull; Scenario interview question generation &rarr; `QuestionSet`
- `POST /evaluate-interview` &bull; 4-dimension rubric grading &rarr; `InterviewEvaluation`
- `POST /analyze-applications` &bull; Funnel analytics &amp; variant conversion &rarr; `ApplicationInsights`

---

&copy; 2026 Jobcadence. Built with Google Gemini.
