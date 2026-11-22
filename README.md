# Jobcadence — A Closed-Loop Career Pivot Coach

> **Turn your career switch into a feedback loop, not a one-time Q&A.**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react)](https://react.dev/)
[![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-4285F4?style=flat&logo=google)](https://deepmind.google/technologies/gemini/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=flat&logo=typescript)](https://www.typescriptlang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Table of Contents

1. [The Problem](#1-the-problem)
2. [What Already Exists](#2-what-already-exists)
3. [The Jobcadence Loop](#3-the-jobcadence-loop)
4. [System Architecture](#4-system-architecture)
5. [Scoring & Recalibration](#5-scoring--recalibration)
6. [Worked Example](#6-worked-example)
7. [Running Locally](#7-running-locally)
8. [API Reference](#8-api-reference)
9. [Privacy & Security](#9-privacy--security)
10. [Roadmap](#10-roadmap)
11. [Sources](#11-sources)

---

## 1. The Problem

Most people who try to switch careers inside tech don't fail for lack of courses — they fail because **nothing tells them whether the studying is working**.

The scale of the shift is easy to see in the numbers:

- The **WEF Future of Jobs Report 2025** (1,000+ employers, 14M+ workers) found **63 %** cite skill gaps as their biggest barrier.
- **39 %** of workers' core skills are expected to change by 2030.
- Roughly **170 million new roles** against **92 million displaced** — AI and big data among the fastest-growing.

A frontend developer with three years of React who wants to move into Applied AI Engineering hits three specific walls:

| Wall | What it means |
|------|---------------|
| **Hidden gaps** | Job posts list dozens of tools and never say which ones actually block a hire |
| **Generic study plans** | Courses start from scratch for everyone, regardless of existing skills |
| **No market feedback** | Dozens of applications go out, with no insight into what's failing or why |

One-shot AI advice makes this worse, not better:

| Weakness | What goes wrong | Jobcadence's response |
|----------|-----------------|----------------------|
| Open loop | The plan is written once and never checked against what was actually learned | Every action updates shared state — the plan keeps changing |
| Free-form text | Output can't feed progress charts or task lists | Responses follow a fixed schema |
| Lenient grading | Buzzword-heavy answers get praised | Weighted four-part rubric with a 70-point pass mark |
| No market data | Resume variants are never compared | Applications tagged by role variant with callback rates compared |

---

## 2. What Already Exists

Every existing tool handles **one stage** of the job hunt well. None connects the stages.

| Category | Examples | Does well | Leaves out |
|----------|----------|-----------|-----------|
| Resume matchers | Jobscan, Teal | Keyword gaps, ATS-style formatting | Competence, learning plan, interview readiness |
| Trackers | Huntr, Teal | Kanban pipeline, reminders, basic metrics | Role-variant comparison that feeds back into strategy |
| Roadmaps | roadmap.sh | Broad, free, community-maintained skill tree | Personalisation and proof of work |
| AI interview tools | Various | Fast practice questions | A graded result that changes what you study next |

Jobcadence sits in the **gap between all four**.

---

## 3. The Jobcadence Loop

Jobcadence treats a career switch as a **feedback loop**, not a one-time Q&A. Whatever you produce changes the plan you see next.

```
┌─────────────────────────────────────────────────────────┐
│                   THE JOBCADENCE LOOP                   │
│                                                         │
│  Resume + JD ──► Gap Analysis ──► 4-Week Plan           │
│                                        │                │
│                                   Portfolio Projects    │
│                                        │                │
│                                   Mock Interview ◄──┐  │
│                                        │            │  │
│                             Pass ≥70?──┤       Recalib  │
│                              ↓   No───┘            │  │
│                             Yes                    │  │
│                              ↓                     │  │
│                        Verified Badge              │  │
│                              │                     │  │
│                       Application Log ─────────────┘  │
│                              │                         │
│                       Funnel Insights                  │
└─────────────────────────────────────────────────────────┘
```

**Forward arrows** = the plan.  
**Dashed arrows** = what makes it a loop: a failed interview rewrites Week 1; application results change how the next round is positioned.

> **Design principle:** Borrowed from Benjamin Bloom's 1984 *2 Sigma Problem* — students taught with mastery learning (regular small tests + corrective work) outperform a standard class by ~1 standard deviation. You don't move on until a check shows you have the material, and a failed check gives targeted correction instead of more of the same.

---

## 4. System Architecture

```
┌──────────────────┐     HTTP      ┌──────────────────┐    API     ┌──────────────────┐
│   React 18 + TS  │ ──────────── │   FastAPI (Py)   │ ─────────│  Gemini 2.5 Flash │
│   Tailwind CSS   │              │   Pydantic v2    │           │   (JSON schema)  │
│   Framer Motion  │              │   pypdf (PDF)    │           └──────────────────┘
│   Recharts       │              │   Rubric logic   │
└──────────────────┘              └──────────────────┘
        │                                  │
   CareerState                      API key stays
  (localStorage)                    server-side only
```

**Rule: the browser never talks to the model directly.**

### Front End
- **React 18 / TypeScript** — five views: Intake, Dashboard, Projects, Verify Skills, Applications
- **Shared context** — `CareerState` saved to `localStorage` under key `career_pivot_state_v1`
- A failed interview on the verification page shows the recalibration banner on the dashboard **immediately**, with no reload

### Orchestration Layer (FastAPI)
- **Python 3.12 + Pydantic v2** — the only code that holds the Gemini API key
- PDFs parsed in memory with `pypdf` — never written to disk
- Prompts, rubric weights, and grading logic all live here (not in the browser)

### Inference Layer
- **Gemini 2.5 Flash** called with `response_mime_type="application/json"` and a Pydantic class as schema
- Replies arrive as typed objects, eliminating markdown-fence and missing-key parse failures

---

## 5. Scoring & Recalibration

Every answer is scored on **four axes**; the composite is computed in code — not by the model.

| Dimension | Weight | What it looks for |
|-----------|--------|-------------------|
| Technical accuracy | **35 %** | Correctness of algorithms, protocols, and system behaviour |
| Practical depth | **30 %** | Concrete choices (batching, caching, indexing, schema design) |
| Edge-case reasoning | **20 %** | Failure modes, latency limits, hallucinations, race conditions, scale |
| Communication clarity | **15 %** | Structured explanation of decisions and trade-offs |

**Composite formula:**

$$I_{score} = \text{round}(0.35\,R_{acc} + 0.30\,R_{depth} + 0.20\,R_{edge} + 0.15\,R_{comm})$$

### The Mastery Gate

| Result | Effect |
|--------|--------|
| **Score ≥ 70** | +5 to match score (capped at 100) + verified-skill badge |
| **Score < 70** | 2 remediation tasks → top of Week 1 · Week 1 focus skill changes · `recalibrated` flag set · alert banner on dashboard |

### State Transitions

| Action | Condition | Effect |
|--------|-----------|--------|
| Complete a project | User marks done (repo link optional) | +7 to match score · skill leaves missing list · verified milestone |
| Pass an interview | Composite ≥ 70 | +5 to match score · verified-skill badge |
| Fail an interview | Composite < 70 | 2 remediation tasks added · Week 1 rewritten |
| Log an application | Company, variant, status, date entered | Application joins the pipeline |
| Analyse applications | User presses analyse button | Best variant + summary + 3 pivots saved |

> **Arithmetic check:** A failed attempt `(62, 48, 40, 74)` → `21.7 + 14.4 + 8.0 + 11.1 = 55.2 ≈ 55`. A retake `(84, 80, 76, 85)` → `29.4 + 24.0 + 15.2 + 12.75 = 81.35 ≈ 81`.

---

## 6. Worked Example

> **Note:** This is a simulated walkthrough to test the mechanism — not a user study.

**Scenario:** A React developer (3 yrs React, TypeScript, Tailwind, REST, Redux) targeting an Applied AI Engineer role (Python, FastAPI, vector DBs, structured LLM outputs, eval harnesses).

**Baseline match:** 54 % · **Missing skills:** hybrid RAG + vector indexing, FastAPI async orchestration, LLM structured outputs, AI evaluation + latency benchmarking.

| Step | Action | System Response | Match Score |
|------|--------|-----------------|-------------|
| 1 | Submitted resume + JD | Built plan, set baseline | **54 %** |
| 2 | Shallow answers on hybrid RAG | Scored 55 — below gate. 2 remediation tasks → Week 1. Alert appeared | **54 %** (held) |
| 3 | Finished hybrid-RAG project | +7 pts · skill removed from missing list · milestone added | **61 %** |
| 4 | Retook interview with chunking/reranking trade-offs | Scored 81 — badge awarded · alert cleared | **66 %** |
| 5 | Finished schema-enforced triage API project | +7 pts | **73 %** |

**Step 2 is the design working:** A weak edge-case sub-score (40) didn't push the candidate forward — it rewrote their week.

### Application Funnel

| Variant | Sent | Screens / Interviews | Callback Rate |
|---------|------|---------------------|---------------|
| Full-stack AI product engineer | 7 | 4 | **57.1 %** |
| Core infrastructure ML engineer | 5 | 0 | **0.0 %** |

$$\text{Callback}(v) = \frac{|\{a_i \in A_v : \text{status}_i \in \{\text{Screen, Interview, Offer}\}\}|}{|A_v|} \times 100\%$$

---

## 7. Running Locally

### Prerequisites
- Python 3.12+
- Node.js 18+
- A [Gemini API key](https://aistudio.google.com/app/apikey)

### Backend

```bash
cd "Samarth Saarthi Updated Ui/backend"

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirement.txt

# Set your API key
echo GEMINI_API_KEY=your_key_here > .env

# Start the server
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Backend runs at **http://127.0.0.1:8000**  
Swagger docs at **http://127.0.0.1:8000/docs**

### Frontend

```bash
cd "Samarth Saarthi Updated Ui"

npm install
npm run dev
```

Frontend runs at **http://localhost:5173**

---

## 8. API Reference

| Method | Endpoint | Input | Returns |
|--------|----------|-------|---------|
| `POST` | `/analyze-gap` | Target role, job description, resume text or PDF (≤10 MB) | Match score, 4–6 missing skills, 4-week plan, 3 project briefs |
| `POST` | `/generate-questions` | Skill, target role, type | 3 scenario questions |
| `POST` | `/evaluate-interview` | Skill, questions, answers | Rubric scores, composite, feedback, remediation tasks |
| `POST` | `/analyze-applications` | List of applications | Best variant, conversion summary, 3 strategic pivots |

**Response codes:** `200` success · `422` validation failure · `500` model timeout

### Data Models

| Model | Key Fields |
|-------|-----------|
| `SkillGapReport` | current/target role, match score (0–100), missing skills, weekly plan, portfolio projects |
| `QuestionSet` | skill, 3 scenario questions |
| `RubricBreakdown` | technical accuracy, practical depth, edge-case reasoning, communication clarity (each 0–100) |
| `InterviewEvaluation` | composite score, rubric, feedback, recalibrate flag, remediation tasks |
| `ApplicationInsights` | best variant, conversion summary, 3 strategic pivots |

---

## 9. Privacy & Security

| Area | Current state |
|------|--------------|
| **API key** | Server-side only — never in the browser bundle |
| **Grading prompts** | Server-side — cannot be softened via DevTools |
| **PDF uploads** | Parsed in memory, never written to disk |
| **Score determinism** | Weights and thresholds are plain code — identical performance always gives identical state change |
| **Bias mitigation** | Gap-analysis prompt instructs the model to judge demonstrated skills and shipped work, not university names or career gaps |

### Known Risks

1. **Prompt injection** — User-supplied text (resume, interview answers) could contain hidden instructions. Mitigation: wrap user text in clear delimiters, treat model as untrusted, flag suspicious scores server-side.
2. **Data residency** — Resume text is sent to the Gemini API and stored in `CareerState` in `localStorage`. "Ephemeral" only means no server disk storage. A "delete my data" button is planned.
3. **Indian data protection** — India's DPDP Act rules (notified Nov 2025) will require clear consent and stated purpose for any deployed version handling residents' resumes.
4. **Grader fairness** — Four axes reduce arbitrary judgment but don't prove fairness. Planned checks: run the same answer 5× and report score spread; test with/without unrelated details (name, school).

---

## 10. Roadmap

| Phase | Problem today | Planned change |
|-------|--------------|----------------|
| **1 · Persistence** | All state in one browser's `localStorage` — no cross-device sync | Move to PostgreSQL with JSONB columns + row-level security per user; keep `localStorage` as fast local cache |
| **2 · Project verification** | Completion rests on the user's word + optional GitHub link | Read repo via GitHub API, check libraries/patterns exist, run tests in isolated container before awarding +7 pts |
| **3 · Portable credentials** | Badges exist only inside the app | Issue signed **W3C Verifiable Credentials 2.0** (became a Recommendation in 2025) carrying skill, rubric sub-scores, timestamp, and issuer signature |

### Also planned

- **Score farming prevention** — one reward per skill, or cooldown between retake attempts
- **Grader consistency** — report spread of repeated scores on the same answer; add graded example answers (40 / 70 / 90) to the prompt
- **Parse-failure handling** — explicit handling of empty parsed results and truncated output
- **Calibration** — treat 70 / 7 / 5 as tunable parameters; compare against real outcomes (interview invitations) once data exists
- **User evidence** — even 5–10 volunteers using the tool for two weeks would turn a design claim into a result

---

## 11. Sources

### Labour Market & Skills
- World Economic Forum, *The Future of Jobs Report 2025*
- Scrimba, *How to become an AI engineer: a developer's roadmap for 2026* *(secondary source for LinkedIn and PwC figures)*

### Existing Tools
- Jobscan — resume scanner and independent review
- Huntr / Teal / Careerflow — comparison articles
- roadmap.sh — AI Engineer roadmap

### Learning & Assessment Research
- Bloom, B. S. (1984). *The 2 Sigma Problem.* Educational Researcher, 13(6), 4–16.
- Jonsson, A. & Svingby, G. (2007). *The use of scoring rubrics: reliability, validity and educational consequences.* Educational Research Review, 2(2), 130–144.

### Engineering & Security
- Google — Structured output (Vertex AI / Gemini API)
- python-genai issue #1039 — empty parse on token limit
- OWASP — LLM01: Prompt Injection
- Press Information Bureau — DPDP Rules 2025 notified; EY DPDP Rules summary
- W3C — Verifiable Credentials 2.0 Recommendation

### Also cited
- FastAPI and Pydantic v2 documentation
- Google GenAI SDK documentation
- ESCO skills taxonomy (European Commission, 2023)
- Mavin et al. (2009) on EARS requirements syntax

---

## Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Add my feature"`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## License

MIT © [Nehal848](https://github.com/Nehal848)

---

<p align="center">
  Built for the Agentic AI Hackathon · November 2026
</p>
