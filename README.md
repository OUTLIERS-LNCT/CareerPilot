# CareerPilot AI — AI-Powered Placement Preparation Platform

An AI-powered placement preparation platform designed to help students prepare for technical interviews and campus placements through personalized learning roadmaps, skill assessments, resume analysis, and AI-driven mock interviews.

PrepPilot AI analyzes a student's target role, preparation timeline, and assessment performance to help identify skill gaps and organize preparation into actionable tasks. The platform integrates a React frontend, FastAPI backend, PostgreSQL database, and LLM-powered features to deliver a structured and personalized placement preparation experience.

---

## Features

<img width="1536" height="1024" alt="CareerPilot Feature Flow Diagram" src="https://github.com/user-attachments/assets/1fb17c3f-96a8-41ed-aaf4-a8006478e420" />

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React.js |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| AI / LLM Integration | OpenRouter-compatible LLM models |
| API Communication | REST API, JSON |
| Resume Processing | Text extraction pipeline |
| Authentication | Session-based authentication |
| Containerization | Docker, Docker Compose |
| Version Control | Git, GitHub |

---

## Architecture Diagram

<img width="1536" height="1024" alt="CareerPilot AI System Architecture" src="https://github.com/user-attachments/assets/a2a7cf9c-9071-42fa-afee-ae01bf9c6703" />

---

## How CareerPilot AI Works

### 1. User Registration and Profile Setup

The student creates an account and configures their preparation profile, including target job role, daily study duration, and target completion date.

### 2. Skill Assessment

The platform presents assessments containing questions associated with specific skills. Student answers and assessment results are stored for future performance analysis.

### 3. Skill Gap Analysis

Assessment results are used as evidence of the student's current skill level. The platform can use this information to identify areas requiring additional preparation.

### 4. Personalized Roadmap Generation

The roadmap service organizes preparation tasks according to the student's target date, daily study time, relevant skills, and available learning resources.

### 5. Resume and Job Description Analysis

Students can upload a resume and provide a job description. The platform stores the extracted content and analysis to support more targeted preparation.

### 6. AI Mock Interviews

The student participates in a mock interview. The interview service manages interview sessions, questions, answers, and feedback, while the LLM integration generates questions or evaluates responses where configured.

### 7. Progress Tracking

Assessment history, skill evidence, completed tasks, and interview feedback help students understand their progress and focus on areas that need improvement.

### Core Database Entities

| Entity | Purpose |
|---|---|
| `users` | Stores user profiles and preparation preferences |
| `login_sessions` | Stores authentication session information |
| `skills` | Defines technical skills and categories |
| `role_skills` | Maps job roles to relevant skills |
| `skill_prerequisites` | Defines dependencies between skills |
| `resources` | Stores learning resources linked to skills |
| `bookmarks` | Stores user-bookmarked resources |
| `question_versions` | Stores versioned assessment questions |
| `assessments` | Defines assessments and their configuration |
| `assessment_questions` | Maps questions to assessments |
| `assessment_attempts` | Stores assessment attempts and scores |
| `attempt_questions` | Stores questions and selected answers for each attempt |
| `skill_evidence` | Stores assessment-derived skill performance |
| `roadmaps` | Stores the user's personalized roadmap |
| `roadmap_versions` | Maintains roadmap history and configuration |
| `roadmap_tasks` | Stores preparation tasks |
| `scheduled_tasks` | Maps tasks to planned dates and study durations |
| `resumes` | Stores resume metadata and extracted text |
| `job_descriptions` | Stores job descriptions and analysis |
| `interviews` | Stores mock interview sessions |
| `interview_turns` | Stores questions, answers, and feedback |
| `llm_runs` | Tracks LLM execution and token usage |
| `rate_windows` | Stores rate-limiting window counters |

### Primary Data Flows

- **Authentication:** User credentials are validated and session information is maintained.
- **Assessment:** Questions are retrieved, answers are submitted, and scores are calculated.
- **Skill Evidence:** Assessment results are associated with relevant skills.
- **Roadmap:** Skill evidence and preparation preferences inform roadmap generation and scheduling.
- **Resume and Job Description:** Uploaded content is processed and stored for analysis.
- **Mock Interview:** Questions, answers, and feedback are managed within an interview session.
- **LLM Integration:** Relevant prompts are sent to the configured provider, and responses and execution metadata are processed.

### Proposed Backend Modules

| Module | Responsibilities |
|---|---|
| Authentication | Registration, login, session validation |
| Assessment | Assessment creation, attempt management, answer submission, scoring |
| Skills | Skill definitions, prerequisites, and performance evidence |
| Roadmap | Skill-gap analysis, task generation, scheduling, roadmap versioning |
| Resume | Upload handling and text extraction |
| Job Description | Job description storage and role analysis |
| Mock Interview | Interview sessions, turn management, answer processing, feedback |
| LLM Integration | Prompt construction, provider requests, response parsing, usage tracking |
| Persistence | SQLAlchemy models and PostgreSQL interactions |
| Request Protection | Rate limiting and request validation |


## Key Concepts Demonstrated

- **Artificial Intelligence Integration** — using an external LLM for selected preparation tasks.
- **Personalized Learning** — organizing preparation according to student goals and progress.
- **Skill Gap Analysis** — using assessment evidence to identify improvement areas.
- **REST API Development** — connecting a React frontend with a FastAPI backend.
- **Relational Database Design** — representing users, assessments, resources, roadmaps, and interviews using PostgreSQL.
- **ORM-Based Persistence** — managing database entities through SQLAlchemy.
- **Prompt Engineering** — structuring model inputs for relevant and consistent responses.
- **Resume and Job Description Processing** — extracting and analyzing career-related information.
- **Session Management** — maintaining authenticated user sessions.
- **Versioned Roadmaps** — preserving changes to personalized preparation plans.
- **Containerization** — packaging services for repeatable deployment.


## 👥 Contributors

| S. No. | Name | Role | Responsibilities |
| --- | --- | --- | --- |
| 1 |  **Varun Juneja** | Team Lead & Full-Stack Developer | Project planning, system architecture, backend services, frontend-backend integration, and overall development |
| 2 | **Harsh Arya** | Frontend Developer | React UI development, reusable components, and responsive layouts |
| 3 | **Aayushi Chourasia** | Frontend Developer | Dashboard design, user experience flow, and interactive views |
| 4 | **Prerna Nebhwani** | Frontend Developer | Component state management, user interface flows, and styling |
| 5 | **Mohit Rajput** | Frontend Developer | Frontend integration, responsive design, and component optimization |
| 6 | **Aditya Singh** | Backend Developer | FastAPI endpoints, business logic, request validation, and API integration |
| 7 | **Choudhary Devashish Kourav** | Backend & Database Engineer | MySQL schema design, migrations, and query optimization |
| 8 | **Haripriya Mahajan** | AI Integration Engineer | OpenRouter integration, prompt engineering, and response handling |
| 9 | **Rishita Verma** | AI Integration & Assessment Developer | AI interview logic, skill-gap analysis, and personalized study-plan logic |
| 10 | **Vanshika Gour** | AI Integration & Resume Developer | Resume processing, job-description analysis, and skill matching |

