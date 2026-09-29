# ProfileAuditor Problem Selection and Feasibility Study

**Project:** ProfileAuditor  
**Version:** 1.0  
**Date:** 2026-09-23  
**Status:** Draft for review

## 1. Problem Statement

Recruiters and technical interviewers often rely on resume claims that are difficult to verify quickly. Manual checking of projects, programming skills, and coding activity takes time, varies between reviewers, and may provide little evidence for the final decision. Candidates also receive limited feedback about resume quality, ATS compatibility, and missing job requirements.

ProfileAuditor addresses this problem by extracting resume information, comparing technical claims with publicly available GitHub and LeetCode evidence, calculating an explainable Reality Score, and providing ATS and role-fit feedback.

## 2. Evidence and Current Situation

- Resume review is frequently manual and time-consuming.
- Project names and skill lists do not always provide evidence of actual technical work.
- GitHub and LeetCode data can provide useful signals, but access, identity, and completeness vary.
- A score without evidence or limitations can create unfair decisions.
- The current prototype already supports PDF/DOCX upload, parsing, verification, scoring, ATS analysis, role-fit analysis, and interview invitations.
- The current prototype uses in-memory storage and therefore is suitable for demonstration or development, not yet for production records.

## 3. Problem Alternatives Considered

| Alternative | Description | Strengths | Weaknesses |
|---|---|---|---|
| A1: Continue manual review | Recruiters inspect resumes and public profiles independently. | No development cost; human judgment remains central. | Slow, inconsistent, difficult to scale, limited audit trail. |
| A2: Resume keyword / ATS checker only | Analyze resume text against a job description. | Simple implementation; useful editing feedback. | Does not verify whether technical claims have public evidence. |
| A3: ProfileAuditor verification platform | Parse resumes, verify public technical evidence, calculate scores, and provide ATS feedback. | Combines screening signals and resume improvement in one workflow. | Integration failures, privacy concerns, possible bias, and identity limitations. |
| A4: Full ATS integration | Build a persistent multi-user recruiting platform with workflow integrations. | Strong long-term business capability. | Larger scope, higher cost, more security and compliance work. |

## 4. Selected Problem and Proposed Solution

**Selected problem:** Reduce the time and inconsistency involved in reviewing technical resume claims while giving candidates useful resume feedback.

**Proposed solution:** Build ProfileAuditor as a human-assisted audit tool that:

1. Accepts PDF and DOCX resumes.
2. Extracts structured candidate information.
3. Verifies available technical claims using GitHub and LeetCode evidence.
4. Shows verified, unverified, and unavailable evidence separately.
5. Calculates an explainable Reality Score and component breakdown.
6. Provides ATS health and optional role-fit analysis.
7. Allows editing and DOCX export.
8. Supports recruiter-approved interview invitations.

## 5. Feasibility Study

### 5.1 Technical Feasibility

**Assessment: Feasible for an MVP; production deployment requires additional engineering.**

The repository already contains a React frontend, FastAPI backend, parser services, GitHub and LeetCode integrations, scoring logic, ATS analysis, DOCX conversion, and Docker configuration. PDF/DOCX processing and HTTP API workflows are technically achievable with the current stack.

**Technical gaps to resolve:**

- Replace in-memory dictionaries with persistent, protected storage.
- Add authentication and role-based authorization.
- Handle provider rate limits, timeouts, schema changes, and retries.
- Improve parsing confidence and correction workflows.
- Separate missing evidence from provider failures.
- Add evidence references for score explanations.
- Test fairness and reduce the risk of treating soft skills as failed technical claims.

### 5.2 Operational Feasibility

**Assessment: Feasible for recruiter-assisted review.**

The workflow matches a real screening activity: upload, review, verify, inspect results, and optionally invite. Recruiters can use the result as a decision-support signal if the interface explains limitations and does not present the score as a final hiring decision.

**Operational requirements:**

- A clear review workflow with loading, error, and retry states.
- A visible explanation of what was and was not verified.
- Manual review before adverse candidate decisions.
- Support process for incorrect extraction or disputed claims.
- Monitoring for external provider failures and email delivery.

### 5.3 Economic Feasibility

**Assessment: Feasible as a low-cost MVP; operating costs depend on scale.**

The existing open-source Python and React stack keeps initial development cost low. Main recurring costs are hosting, API usage, email delivery, optional LLM calls, storage, monitoring, and security maintenance.

| Cost area | MVP approach | Production consideration |
|---|---|---|
| Hosting | Docker or low-cost cloud deployment | Scalable backend and frontend hosting |
| Storage | Temporary files and in-memory demo state | Managed database and object storage |
| Verification | Public provider APIs | Rate-limit management and approved API access |
| Scoring | Rule-based scoring with optional AI fallback | Cost controls, versioning, and explainability |
| Email | Configured email provider | Delivery tracking and compliance |
| Operations | Basic logs and health endpoint | Monitoring, alerting, backups, and incident response |

### 5.4 Legal, Ethical, and Privacy Feasibility

**Assessment: Feasible only with explicit safeguards and stakeholder approval.**

Resume data contains personal information, and public technical activity may be incomplete or incorrectly attributed. The system must obtain appropriate consent, disclose automated processing, protect personal data, provide correction/deletion processes, and keep human reviewers responsible for decisions.

**Required safeguards:**

- Do not claim that an unverified item is false.
- Treat missing public data as unknown unless a stakeholder-approved policy says otherwise.
- Separate technical evidence from soft-skill assessment.
- Display provider limitations and data freshness.
- Avoid automatic rejection or ranking without approved governance.
- Define retention, deletion, access, and dispute policies.
- Do not expose secrets or unnecessary resume content in logs.

### 5.5 Schedule Feasibility

**Assessment: Feasible for a staged MVP.**

| Stage | Main outcome |
|---|---|
| Stage 1 | Validate stakeholders, problem, scoring policy, privacy expectations, and success measures. |
| Stage 2 | Stabilize upload, parsing, verification, scoring, ATS analysis, and results workflow. |
| Stage 3 | Add persistent storage, authentication, authorization, audit history, and provider resilience. |
| Stage 4 | Pilot with controlled users, evaluate accuracy and fairness, and refine requirements. |
| Stage 5 | Prepare production release and operational support. |

## 6. Feasibility Decision

**Decision:** Proceed with a controlled MVP and stakeholder validation.

The problem is meaningful, the current technical foundation is sufficient for an MVP, and the workflow is operationally plausible. Production approval is conditional on persistent storage, security controls, privacy policy, evidence explainability, provider resilience, and fairness review.

## 7. Success Measures

- Reduced average time to review a technical resume.
- Percentage of audits completed without manual technical troubleshooting.
- Percentage of verified claims with understandable evidence.
- Recruiter confidence in the score explanation.
- Candidate ability to identify and correct extraction issues.
- Provider failure rate and successful retry rate.
- No critical privacy or security incidents during pilot.
- Stakeholder agreement that the tool supports, rather than replaces, human judgment.

## 8. Recommendation and Next Actions

1. Conduct interviews using [Stakeholder_Interview_Questionnaire.md](Stakeholder_Interview_Questionnaire.md).
2. Confirm scoring treatment for soft skills and missing public profiles.
3. Define a minimum evidence and explanation standard for each verified claim.
4. Prioritize persistent storage, authentication, privacy, and error handling before production.
5. Run a small pilot with representative resumes and a documented evaluation set.
6. Update the SRS and project charter based on approved stakeholder decisions.
