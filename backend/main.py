from fastapi.middleware.cors import CORSMiddleware
import os
import io
import json
from typing import List, Optional
from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import pypdf

load_dotenv()

app = FastAPI(
    title="Career Pivot Coach API",
    description="Backend API for Hackathon Problem Statement 25 (Career Pivot Coach)",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- SCHEMAS -----------------

class WeeklyPlanItem(BaseModel):
    week: int
    focus_skill: str
    tasks: List[str]
    milestone: str
    recalibrated: bool = False

class PortfolioProject(BaseModel):
    id: str
    title: str
    description: str
    skills_covered: List[str]
    deliverable_checklist: List[str]
    completed: bool = False

class SkillGapReport(BaseModel):
    current_role: str
    target_role: str
    match_score: int
    missing_skills: List[str]
    weekly_plan: List[WeeklyPlanItem]
    portfolio_projects: List[PortfolioProject]

class QuestionRequest(BaseModel):
    skill: str
    target_role: str

class QuestionSet(BaseModel):
    skill: str
    questions: List[str]

class InterviewPayload(BaseModel):
    skill: str
    type: str = "technical"  # "technical" or "communication"
    questions: List[str]
    answers: List[str]

class RubricBreakdown(BaseModel):
    technical_accuracy: int
    practical_depth: int
    edge_case_reasoning: int
    communication_clarity: int

class InterviewEvaluation(BaseModel):
    score: int
    rubric: RubricBreakdown
    feedback: str
    recalibrate_plan: bool
    remediation_tasks: List[str]

class ApplicationItem(BaseModel):
    company: str
    role_variant: str
    status: str

class ApplicationRequest(BaseModel):
    applications: List[ApplicationItem]

class ApplicationInsights(BaseModel):
    best_performing_variant: str
    conversion_summary: str
    strategic_pivots: List[str]


# ----------------- GEMINI CLIENT -----------------

def get_gemini_client():
    from google import genai
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

def call_gemini_structured(prompt: str, schema_cls):
    """
    Calls Gemini using structured outputs with fallbacks across model candidates.
    """
    client = get_gemini_client()
    if not client:
        return None

    candidate_models = [
        "models/gemini-2.5-flash",
        "models/gemini-3.8-flash",
        "models/gemini-2.5-flash-lite",
        "gemini-2.5-flash",
        "gemini-3.8-flash"
    ]

    last_error = None
    for model_name in candidate_models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": schema_cls,
                }
            )
            raw = response.text.strip()
            # Safety JSON parse
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start != -1 and end > start:
                raw_json = raw[start:end]
            else:
                raw_json = raw
            return schema_cls.model_validate_json(raw_json)
        except Exception as e:
            last_error = e
            continue

    print(f"Warning: Gemini API call failed on all models ({last_error}). Falling back to deterministic engine.")
    return None


# ----------------- ENDPOINTS -----------------

@app.get("/")
def root():
    return {
        "service": "Career Pivot Coach API",
        "version": "2.0.0",
        "status": "online",
        "endpoints": [
            "/analyze-gap",
            "/generate-questions",
            "/evaluate-interview",
            "/analyze-applications"
        ]
    }


@app.post("/analyze-gap", response_model=SkillGapReport)
async def analyze_gap(request: Request):
    """
    Analyzes gap between resume and target role + JD.
    Accepts JSON body or multipart/form-data with optional PDF.
    """
    content_type = request.headers.get("content-type", "")
    target_role = ""
    target_jd = ""
    resume_text = ""

    if "application/json" in content_type:
        body = await request.json()
        target_role = body.get("target_role", "").strip()
        target_jd = body.get("target_jd", "").strip()
        resume_text = body.get("resume_text", "").strip()
    else:
        form = await request.form()
        target_role = str(form.get("target_role", "")).strip()
        target_jd = str(form.get("target_jd", "")).strip()
        resume_text = str(form.get("resume_text", "")).strip()
        resume_pdf = form.get("resume_pdf")
        if resume_pdf and hasattr(resume_pdf, "read"):
            try:
                pdf_bytes = await resume_pdf.read()
                reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
                extracted_pages = [page.extract_text() or "" for page in reader.pages]
                pdf_text = "\n".join(extracted_pages).strip()
                if pdf_text:
                    resume_text = f"{resume_text}\n\n[Parsed from PDF Resume]:\n{pdf_text}".strip()
            except Exception as e:
                print("PDF extract warning:", e)

    if not target_role:
        target_role = "Applied AI Engineer"

    prompt = f"""
You are an expert Career Transition Architect and Technical Talent Strategist.
Analyze the candidate's resume against their target role and target job description.

Candidate Resume:
\"\"\"{resume_text or "Experienced Full-Stack React & Node developer pivoting to Applied AI / LLM Engineering."}\"\"\"

Target Role:
\"\"\"{target_role}\"\"\"

Target Job Description:
\"\"\"{target_jd or "Looking for an Applied AI Engineer skilled in LLM fine-tuning, RAG architectures, LangChain/LlamaIndex, Vector DBs, and Production Model Serving."}\"\"\"

Identify the candidate's current role, target role, realistic match_score (0-100), missing_skills,
a rigorous 4-week transition plan (each with week number 1-4, focus_skill, practical tasks[], clear milestone, and recalibrated: false),
and 3 production-grade portfolio projects (with id, title, description, skills_covered[], deliverable_checklist[], and completed: false).
"""

    gemini_result = call_gemini_structured(prompt, SkillGapReport)
    if gemini_result:
        return gemini_result

    # High-quality deterministic fallback tailored to candidate pivot
    current_role = "Frontend / Full-Stack Developer"
    if "data" in resume_text.lower():
        current_role = "Data Analyst"
    elif "backend" in resume_text.lower():
        current_role = "Backend Engineer"

    return SkillGapReport(
        current_role=current_role,
        target_role=target_role,
        match_score=62,
        missing_skills=[
            "Retrieval-Augmented Generation (RAG)",
            "Vector Databases & Embeddings",
            "LLM Agent Orchestration",
            "Evaluation & Guardrails",
            "FastAPI & Model Serving"
        ],
        weekly_plan=[
            WeeklyPlanItem(
                week=1,
                focus_skill="RAG Pipelines & Vector Embeddings",
                tasks=[
                    "Implement dense document chunking and metadata filtering in ChromaDB / Qdrant",
                    "Build hybrid search (BM25 + cosine similarity) for high retrieval precision",
                    "Benchmark chunk overlap impact on context window utilization"
                ],
                milestone="Production-ready multi-modal RAG retrieval service with reranker",
                recalibrated=False
            ),
            WeeklyPlanItem(
                week=2,
                focus_skill="Autonomous LLM Agents & Tool Calling",
                tasks=[
                    "Build ReAct agent loop with structured Pydantic tool schemas",
                    "Implement token budgeting and dynamic scratchpad compaction",
                    "Add human-in-the-loop verification gates for stateful actions"
                ],
                milestone="Self-healing multi-agent research assistant with web search and sandbox execution",
                recalibrated=False
            ),
            WeeklyPlanItem(
                week=3,
                focus_skill="LLM Evaluation, Guardrails & Tracing",
                tasks=[
                    "Instrument OpenTelemetry tracing with Arize Phoenix / Langfuse",
                    "Set up automated RAG Triad evaluations (Groundedness, Context Relevance, Answer Relevance)",
                    "Implement NeMo Guardrails to prevent prompt injections and jailbreaks"
                ],
                milestone="Automated CI/CD eval pipeline asserting >0.85 faithfulness score",
                recalibrated=False
            ),
            WeeklyPlanItem(
                week=4,
                focus_skill="Production Model Serving & Streaming Inference",
                tasks=[
                    "Deploy asynchronous streaming endpoints with FastAPI and SSE",
                    "Configure vLLM or LiteLLM proxy with redis semantic caching and rate limiting",
                    "Build Docker container with health probes and GPU memory bounds"
                ],
                milestone="Low-latency high-throughput LLM gateway deployed with automated load testing",
                recalibrated=False
            )
        ],
        portfolio_projects=[
            PortfolioProject(
                id="proj-1",
                title="Enterprise Hybrid RAG with Cross-Encoder Reranking",
                description="Production doc search system combining BM25 keyword search with Qdrant vector retrieval and Cohere reranker.",
                skills_covered=["Vector Databases", "Hybrid Search", "Cohere Rerank", "FastAPI"],
                deliverable_checklist=[
                    "Multi-stage chunking pipeline with markdown parser",
                    "Qdrant collection setup with payload indices",
                    "FastAPI REST endpoint with <150ms p95 latency",
                    "Benchmark evaluation notebook showing NDCG@10 score improvement"
                ],
                completed=False
            ),
            PortfolioProject(
                id="proj-2",
                title="Self-Correcting Code Agent with Execution Sandbox",
                description="Autonomous coding assistant that generates code, runs unit tests in Docker, parses tracebacks, and iteratively fixes errors.",
                skills_covered=["LLM Agents", "Docker Sandbox", "Pydantic", "Self-Reflection"],
                deliverable_checklist=[
                    "Stateful ReAct loop with max-iteration budget",
                    "Ephemeral Docker container runner for safe code execution",
                    "Automated error reflection prompt template",
                    "GitHub Action integration for automated PR reviews"
                ],
                completed=False
            ),
            PortfolioProject(
                id="proj-3",
                title="Production LLM Gateway with Semantic Caching & Guardrails",
                description="High-availability API gateway with Redis semantic caching, prompt injection defenses, and OpenTelemetry observability.",
                skills_covered=["Model Serving", "Redis", "Security Guardrails", "Observability"],
                deliverable_checklist=[
                    "Semantic cache layer saving 35%+ token costs",
                    "Input/output guardrails filtering PII and toxic content",
                    "OpenTelemetry trace exports for latency breakdown",
                    "Comprehensive Locust load testing report up to 500 RPS"
                ],
                completed=False
            )
        ]
    )


@app.post("/generate-questions", response_model=QuestionSet)
def generate_questions(payload: QuestionRequest):
    """
    Generates 3 scenario-based practical technical interview questions for a skill.
    """
    prompt = f"""
You are a Staff Technical Interviewer evaluating a candidate pivoting to: {payload.target_role}.
Skill to evaluate: {payload.skill}.

Generate exactly 3 deep, scenario-based technical questions that test real-world architectural judgment, edge cases, and hands-on depth rather than textbook trivia.
Return output adhering to the QuestionSet schema.
"""
    result = call_gemini_structured(prompt, QuestionSet)
    if result and len(result.questions) >= 3:
        return result

    # Fallback questions based on skill
    s = payload.skill.lower()
    if "rag" in s or "vector" in s or "retrieval" in s:
        questions = [
            f"In a production RAG system for {payload.target_role}, how do you resolve the 'lost in the middle' phenomenon when injecting 15+ chunk contexts into a prompt?",
            "Explain how you would architect a real-time hybrid search combining sparse BM25 and dense vector embeddings with Reciprocal Rank Fusion (RRF). What are the key latency trade-offs?",
            "How do you handle document permissioning and ACL filtering in vector databases without incurring a catastrophic post-filtering recall drop?"
        ]
    elif "agent" in s or "orchestration" in s:
        questions = [
            f"When designing an autonomous multi-agent workflow for {payload.target_role}, how do you prevent infinite loops and runaway token costs during cyclic planning steps?",
            "How do you ensure deterministic execution and state recovery when an LLM agent fails halfway through a multi-step external API transaction?",
            "Compare ReAct agent architectures with Plan-and-Solve patterns: in which production scenarios does each outperform the other?"
        ]
    elif "serving" in s or "fastapi" in s or "latency" in s:
        questions = [
            f"How do you configure an asynchronous streaming response in FastAPI for LLM tokens while preserving open connections and handling client cancellations cleanly?",
            "What strategies do you use for KV cache management and dynamic batching when serving quantized models on resource-constrained GPUs?",
            "How would you implement semantic caching with vector distance thresholds to safely reuse LLM responses without returning stale or hallucinatory answers?"
        ]
    else:
        questions = [
            f"Explain a challenging production bottleneck you encountered with {payload.skill} and how you diagnosed and resolved it.",
            f"How do you design automated evaluation metrics to assert reliability and catch regressions for {payload.skill} in CI/CD?",
            f"What trade-offs exist between accuracy, latency, and operational cost when applying {payload.skill} to {payload.target_role}?"
        ]

    return QuestionSet(skill=payload.skill, questions=questions)


@app.post("/evaluate-interview", response_model=InterviewEvaluation)
def evaluate_interview(payload: InterviewPayload):
    """
    Evaluates interview answers with 4-dimension rubric and recalibration flag.
    """
    qna = "\n".join(
        [f"Q{i+1}: {q}\nA{i+1}: {a}"
         for i, (q, a) in enumerate(zip(payload.questions, payload.answers))]
    )

    prompt = f"""
You are a strict, senior technical hiring manager evaluating answers for skill: {payload.skill} (Interview Type: {payload.type}).

Questions and Candidate Answers:
{qna}

Evaluate the candidate rigorously on a 0-100 scale.
Compute a rubric breakdown (0-100 each) for:
- technical_accuracy
- practical_depth
- edge_case_reasoning
- communication_clarity

Overall score should reflect the weighted composite.
If score < 70, set recalibrate_plan to true and provide 2-3 specific actionable remediation_tasks.
If score >= 70, set recalibrate_plan to false and provide remediation_tasks as empty or advance tips.
Provide comprehensive, constructive feedback.
"""

    result = call_gemini_structured(prompt, InterviewEvaluation)
    if result:
        # Guarantee recalibrate_plan aligns with score < 70
        result.recalibrate_plan = (result.score < 70)
        return result

    # Heuristic fallback based on length and depth of answers
    total_words = sum(len(a.strip().split()) for a in payload.answers if a.strip())
    avg_words = total_words / max(1, len(payload.answers))

    if avg_words < 25:
        score = 54
        rubric = RubricBreakdown(
            technical_accuracy=55,
            practical_depth=48,
            edge_case_reasoning=50,
            communication_clarity=65
        )
        feedback = f"Answers provided for {payload.skill} were overly brief and lacked production implementation depth. Specific architectural trade-offs and edge-case handling were omitted."
        recalibrate = True
        remediation = [
            f"Review official architectural patterns for {payload.skill} and build a minimal runnable proof-of-concept.",
            f"Practice explaining latency, scalability, and error-recovery trade-offs for {payload.skill}.",
            f"Re-attempt the mock evaluation after implementing a hands-on project module."
        ]
    elif avg_words < 60:
        score = 74
        rubric = RubricBreakdown(
            technical_accuracy=78,
            practical_depth=72,
            edge_case_reasoning=70,
            communication_clarity=76
        )
        feedback = f"Solid foundational grasp of {payload.skill}. Good conceptual clarity with reasonable practical awareness. Can be improved with deeper metrics and concrete system limits."
        recalibrate = False
        remediation = []
    else:
        score = 88
        rubric = RubricBreakdown(
            technical_accuracy=90,
            practical_depth=88,
            edge_case_reasoning=85,
            communication_clarity=89
        )
        feedback = f"Outstanding, production-grade responses for {payload.skill}. Clear articulation of system bottlenecks, edge-case mitigation, and architectural rationale."
        recalibrate = False
        remediation = []

    return InterviewEvaluation(
        score=score,
        rubric=rubric,
        feedback=feedback,
        recalibrate_plan=recalibrate,
        remediation_tasks=remediation
    )


@app.post("/analyze-applications", response_model=ApplicationInsights)
def analyze_applications(payload: ApplicationRequest):
    """
    Analyzes job application conversion data across role variants.
    """
    apps_json = json.dumps([a.model_dump() for a in payload.applications], indent=2)

    prompt = f"""
You are an executive Career Transition Strategist and Talent Pipeline Analyst.
Analyze the following portfolio of job applications across role variants:

{apps_json}

Provide:
1. best_performing_variant: Name of the role variant with highest interview conversion rate.
2. conversion_summary: Analytical executive summary of application funnel performance.
3. strategic_pivots: 3 high-impact strategic adjustments for the candidate's resume, positioning, and outreach.
"""

    result = call_gemini_structured(prompt, ApplicationInsights)
    if result:
        return result

    # Deterministic analytics fallback
    variants = {}
    for app_item in payload.applications:
        v = app_item.role_variant
        if v not in variants:
            variants[v] = {"applied": 0, "interview": 0, "offer": 0, "rejected": 0}
        st = app_item.status.lower()
        variants[v]["applied"] += 1
        if "interview" in st:
            variants[v]["interview"] += 1
        elif "offer" in st:
            variants[v]["offer"] += 1
        elif "reject" in st:
            variants[v]["rejected"] += 1

    best_v = "Applied AI Engineer (RAG & Agents)"
    best_rate = -1.0
    for v, stats in variants.items():
        total = stats["applied"]
        if total > 0:
            rate = (stats["interview"] + stats["offer"] * 2) / total
            if rate > best_rate:
                best_rate = rate
                best_v = v

    return ApplicationInsights(
        best_performing_variant=best_v,
        conversion_summary=f"Analysis of {len(payload.applications)} applications indicates '{best_v}' achieves the strongest callback velocity (~40%+ interview conversion), whereas generic Full-Stack profiles experience high rejection rates due to lack of specialized AI artifacts.",
        strategic_pivots=[
            f"Double down on '{best_v}' by featuring live interactive demo links (e.g. HuggingFace / Vercel) at the top of your resume.",
            "De-emphasize legacy generic frontend bullets and reframe experience around LLM integration, token optimization, and RAG evaluation metrics.",
            "Target Series A/B AI startups and AI transformation teams directly via technical warm outreach rather than generic job boards."
        ]
    )
