# Database and AI behavior

## Tables

| Table | What it stores |
|---|---|
| `users`, `profiles` | Sign-in identity/role and student target, study time, deadline |
| `skills`, `resources`, `questions` | Admin-curated catalogue, verified links, private MCQ answer keys |
| `attempts` | Server-calculated overall and per-question answer evidence |
| `roadmaps`, `roadmap_tasks` | Versioned plan, estimated study time, due dates, priority and completion state |
| `resume_documents`, `analyses` | Private uploaded-file path/text and owner-scoped JD match result |
| `interview_sessions` | Text conversation transcript and final feedback |
| `study_sessions` | Actual/planned study minutes, optional linked task and student reflection |
| `study_guidance` | JSON snapshot of AI or deterministic study guide linked to a roadmap |

Use `alembic upgrade head` to create tables. `python -m scripts.seed_catalogue` inserts missing starter records without overwriting admin edits. The seed includes small sample questions, so review and replace them before using the app with students.

## AI provider

`app/ai.py` calls the OpenAI-compatible OpenRouter chat-completions endpoint. Configure `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, and optionally `OPENROUTER_BASE_URL` in backend `.env`. The API key never appears in a route response. The model slug comes from configuration because models and account availability can change.

AI is used for coaching language and suggestions:

- Roadmap study guides consider the student's incomplete task titles, time estimates, target role, and the verified resource catalogue. The schedule, due dates, task status and scores stay deterministic. Model resource recommendations must refer to existing database resource IDs; returned resource links are checked against the catalogue.
- Interview follow-ups use the role, recent transcript and current student answer. The model returns four coaching scores (correctness, clarity, completeness and examples), one improvement, and a next question. These are coaching signals, not objective grading.
- Resource recommendation ranking starts from verified resources already linked to incomplete roadmap tasks. AI can explain picks but cannot create a URL.

When the key is absent, the provider times out, or output fails validation, the endpoints use a local fallback. No LLM call changes a score or writes a new task. Callers can check `GET /api/v1/ai/status`.

AI routes send the interview answer or roadmap task/catalogue metadata to OpenRouter. The current AI routes do not send resume or JD content. If adding resume analysis later, use a separate explicit opt-in and tell the student what text leaves the backend. Provider data handling depends on the provider and account configuration.

## Progress loop

A student takes an assessment; the server scores the answer key and persists an attempt. If a roadmap exists, the latest assessment creates another roadmap version with a change reason. A task update records its state; a study-session log records time actually spent and reflection. The dashboard aggregates score history, roadmap completion and study minutes. The guide and resource recommendation routes use incomplete roadmap tasks as the next-study context.
