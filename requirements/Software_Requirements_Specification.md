# Software Requirements Specification (SRS)

## ProfileAuditor

**Version:** 1.0  
**Date:** 2026-09-23  
**Status:** Draft for stakeholder validation  
**Document owner:** ProfileAuditor project team

> This SRS describes the current implemented product and identifies requirements that must be confirmed during stakeholder elicitation. Items marked **Proposed** are recommendations for a production-ready release, not claims about existing behavior.

## 1. Introduction

### 1.1 Purpose

ProfileAuditor evaluates the credibility of technical claims made in a resume by extracting candidate information, comparing technical claims with public GitHub and LeetCode evidence, calculating a Reality Score, and presenting the results to a recruiter or interviewer. It also provides resume editing, ATS health analysis, role-fit analysis, and DOCX export.

This document defines the product scope, actors, functional requirements, quality requirements, interfaces, data requirements, constraints, and acceptance criteria.

### 1.2 Product Scope

The system shall support the following main workflow:

1. A user uploads a PDF or DOCX resume.
2. The system extracts text and structured candidate information.
3. The user reviews or uses the extracted resume data.
4. The system verifies technical claims against public GitHub and LeetCode data when handles are available.
5. The system categorizes evidence and calculates a Reality Score.
6. The system displays score breakdown, ATS health, and optional role-fit analysis.
7. An authorized recruiter may send an interview invitation.
8. A user may edit resume content, receive live ATS feedback, and export a DOCX file.

### 1.3 Out of Scope for the Current Release

- Applicant tracking system integrations.
- Persistent multi-tenant recruiter accounts.
- Candidate ranking across a database of resumes.
- Full LinkedIn or Twitter verification implementation.
- Automated hiring decisions.
- Guaranteed proof of authorship or candidate identity.
- Replacement of human interviews and reference checks.

### 1.4 Definitions

| Term | Definition |
|---|---|
| Audit | The complete process of parsing, verifying, scoring, and presenting resume evidence. |
| Candidate | Person whose resume is being analyzed. |
| Public evidence | Information retrieved from public GitHub or LeetCode profiles. |
| Verified claim | A resume claim for which the system found matching evidence. |
| Unverified claim | A claim for which matching evidence was not found; it is not proof of dishonesty. |
| Reality Score | A 0-100 indicator based on available verification evidence. |
| ATS health | Analysis of resume structure, content, and machine-readability. |
| Role fit | Comparison between resume evidence and a supplied job description. |

## 2. Stakeholders and User Classes

| User class | Description | Primary goals |
|---|---|---|
| Recruiter / hiring manager | Reviews candidates and decides who advances | Fast, explainable screening and invitation workflow |
| Technical interviewer | Assesses technical credibility | Reliable evidence and detailed verification results |
| Candidate | Owns or supplies resume content | Fair processing, corrections, feedback, and export |
| Product owner | Defines value and release scope | Adoption, measurable outcomes, controlled risk |
| Administrator | Operates the application and integrations | Reliability, security, monitoring, and configuration |
| Privacy / legal reviewer | Reviews data and public-profile handling | Consent, transparency, retention, and deletion |

## 3. System Context and Architecture

### 3.1 Logical Components

- **React frontend:** Upload, editor, results dashboard, navigation, and invitation controls.
- **FastAPI backend:** HTTP API, request validation, workflow orchestration, and response models.
- **Resume parser:** PDF/DOCX text extraction and structured field extraction.
- **GitHub service:** Public repository, language, activity, and project evidence retrieval.
- **LeetCode service:** Public coding activity and skill evidence retrieval.
- **Scoring service:** Component scores, weighted Reality Score, and score breakdown.
- **ATS service:** Resume quality and machine-readability analysis.
- **Job matching service:** Job-description requirements and role-fit analysis.
- **Email service:** Interview invitation delivery.
- **Storage:** Current implementation uses in-memory dictionaries and temporary files. Persistent storage is a proposed production requirement.

### 3.2 External Interfaces

| Interface | Purpose |
|---|---|
| GitHub API | Retrieve public repositories and activity for verification. |
| LeetCode API / GraphQL | Retrieve public problem-solving evidence. |
| Email provider / SendGrid | Deliver interview invitations. |
| OpenRouter or Gemini, optional | Obtain an AI-assisted score fallback when configured. |

## 4. Functional Requirements

Priority uses MoSCoW: **M = Must**, **S = Should**, **C = Could**, **W = Won't for this release**.

### 4.1 Resume Upload and Parsing

| ID | Priority | Requirement |
|---|---|---|
| FR-001 | M | The system shall accept PDF and DOCX resume uploads. |
| FR-002 | M | The system shall reject unsupported file types with a clear validation message. |
| FR-003 | M | The system shall generate a unique resume ID for each accepted upload. |
| FR-004 | M | The system shall extract readable text from an uploaded resume. |
| FR-005 | M | The system shall extract available name, email, phone, skills, projects, experience, education, and public-profile handles. |
| FR-006 | M | The system shall identify whether parsing completed, is processing, or failed. |
| FR-007 | M | The system shall reject or flag files that do not contain sufficient resume signals. |
| FR-008 | S | The system should allow a user to preview and correct extracted data before verification. **Proposed.** |
| FR-009 | S | The system should preserve the original uploaded file separately from edited content. **Proposed.** |

### 4.2 Verification

| ID | Priority | Requirement |
|---|---|---|
| FR-010 | M | The system shall allow verification to be started for a completed resume. |
| FR-011 | M | The system shall use a supplied GitHub handle or a handle extracted from the resume when available. |
| FR-012 | M | The system shall use a supplied LeetCode handle or a handle extracted from the resume when available. |
| FR-013 | M | The system shall compare claimed technical skills with available GitHub and LeetCode evidence. |
| FR-014 | M | The system shall compare claimed projects with available GitHub evidence. |
| FR-015 | M | The system shall report verified and unverified skills and projects separately. |
| FR-016 | M | The system shall show an unavailable-profile or integration-error state instead of silently treating missing data as proof against a candidate. **Proposed clarification.** |
| FR-017 | S | The system should display the evidence supporting each verified claim. **Proposed.** |
| FR-018 | S | The system should distinguish technical skills, soft skills, and projects during verification. **Proposed.** |
| FR-019 | S | The system should allow a candidate or reviewer to add context to an unverified claim. **Proposed.** |

### 4.3 Scoring and Analysis

| ID | Priority | Requirement |
|---|---|---|
| FR-020 | M | The system shall calculate a Reality Score from 0 to 100 after verification completes. |
| FR-021 | M | The system shall show a score breakdown for GitHub, LeetCode, skills, and projects. |
| FR-022 | M | The system shall calculate technical role fit when a job description is supplied. |
| FR-023 | M | The system shall calculate ATS health for parsed or edited resume content. |
| FR-024 | M | The system shall prevent score retrieval until verification is complete or return a meaningful status response. |
| FR-025 | M | The system shall display the inputs and evidence categories used in scoring. |
| FR-026 | S | The system should provide a human-readable explanation of the score. |
| FR-027 | S | The system should permit configurable scoring weights and scoring policy versioning. **Proposed.** |
| FR-028 | M | The system shall state that an unverified claim is not proof that the claim is false. **Proposed user-facing requirement.** |

### 4.4 Resume Editor and ATS Workflow

| ID | Priority | Requirement |
|---|---|---|
| FR-029 | M | The system shall allow a user to upload a document into the resume editor. |
| FR-030 | M | The system shall extract editable text or rich document content from PDF/DOCX input. |
| FR-031 | M | The system shall provide live ATS analysis for edited resume text. |
| FR-032 | M | The system shall optionally compare resume text with a supplied job description. |
| FR-033 | M | The system shall export edited content as a DOCX file. |
| FR-034 | S | The system should preserve basic document structure during conversion and export. |

### 4.5 Interview Invitations

| ID | Priority | Requirement |
|---|---|---|
| FR-035 | M | The system shall allow an invitation to be initiated only when the resume and score exist. |
| FR-036 | M | The system shall require a candidate email address before sending an invitation. |
| FR-037 | M | The system shall support an optional message, interview date, and interview location. |
| FR-038 | M | The system shall queue email delivery as a background task and return an invitation status. |
| FR-039 | S | The system should record delivery success or failure for later review. **Proposed.** |
| FR-040 | S | The system should require recruiter confirmation immediately before sending. **Proposed.** |

### 4.6 Error Handling and User Feedback

| ID | Priority | Requirement |
|---|---|---|
| FR-041 | M | The system shall return actionable errors for invalid files, missing resumes, incomplete verification, and missing scores. |
| FR-042 | M | The frontend shall show loading, success, and failure states for long-running or external operations. |
| FR-043 | M | The system shall not expose API keys, provider credentials, or internal stack traces to end users. **Proposed security clarification.** |
| FR-044 | S | The system should allow retrying failed external verification independently. **Proposed.** |

## 5. Non-Functional Requirements

### 5.1 Performance

| ID | Requirement | Target / acceptance measure |
|---|---|---|
| NFR-001 | Upload and basic parsing should provide a response or status within a reasonable user wait. | Target to be confirmed; recommend 10 seconds for normal resumes. |
| NFR-002 | Results should load without unnecessary repeated external requests. | Cached or stored results are reused for the same resume and verification run. |
| NFR-003 | External API timeouts shall not block the entire application indefinitely. | Each provider has a configured timeout and failure state. |

### 5.2 Security and Privacy

| ID | Requirement | Target / acceptance measure |
|---|---|---|
| NFR-004 | Resume files and extracted personal data shall be transmitted over HTTPS in production. | No production HTTP-only deployment. |
| NFR-005 | Secrets shall be stored in environment configuration or a secret manager. | No credentials committed to source control or returned in API responses. |
| NFR-006 | The system shall provide a documented retention and deletion policy. | Policy approved by privacy stakeholder before production. |
| NFR-007 | Access to candidate data shall be restricted to authorized users. **Proposed.** | Role-based authorization test passes. |
| NFR-008 | The system shall disclose that public-profile verification is an automated signal, not a hiring decision. | Notice visible before or with results. |
| NFR-009 | The system shall support correction and deletion requests. **Proposed.** | Request can be recorded, fulfilled, and audited. |

### 5.3 Reliability and Availability

| ID | Requirement | Target / acceptance measure |
|---|---|---|
| NFR-010 | Provider failures shall produce a recoverable result and clear status. | GitHub/LeetCode outage test returns an error or unavailable state without crashing the API. |
| NFR-011 | Production data shall not rely on process memory as the only copy. **Proposed.** | Persistent database and backup restore test pass. |
| NFR-012 | The system shall expose health status for deployment monitoring. | `/health` returns a valid health response. |

### 5.4 Usability and Accessibility

| ID | Requirement | Target / acceptance measure |
|---|---|---|
| NFR-013 | A first-time recruiter shall be able to upload a resume and reach results without developer assistance. | Usability test succeeds for at least 4 of 5 participants. |
| NFR-014 | Results shall use plain language and explain score limitations. | Stakeholder review approval. |
| NFR-015 | The UI shall support keyboard navigation, readable contrast, and responsive layouts. | Accessibility review finds no critical issue. |

### 5.5 Maintainability and Observability

| ID | Requirement | Target / acceptance measure |
|---|---|---|
| NFR-016 | Backend services shall remain separated by responsibility. | Parser, verification, scoring, ATS, and email logic remain independently testable. |
| NFR-017 | The system shall log provider failures and workflow failures without logging sensitive resume content unnecessarily. | Log review passes privacy checklist. |
| NFR-018 | API contracts shall be documented and versionable. | FastAPI documentation and response models remain current. |

## 6. External and API Interfaces

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/resume/upload` | Upload and parse a PDF/DOCX resume. |
| GET | `/api/resume/{resume_id}` | Retrieve parsed resume data or processing status. |
| POST | `/api/resume/extract-text` | Extract raw text for the editor. |
| POST | `/api/resume/convert-pdf-to-doc` | Convert uploaded content into rich document data. |
| POST | `/api/resume/export-docx` | Export edited resume content as DOCX. |
| POST | `/api/verification/{resume_id}` | Start GitHub/LeetCode verification. |
| GET | `/api/verification/{resume_id}` | Retrieve verification results. |
| GET | `/api/score/{resume_id}` | Retrieve or calculate the Reality Score. |
| POST | `/api/score/live-ats` | Evaluate live ATS health and optional role fit. |
| POST | `/api/invite/{resume_id}` | Queue an interview invitation. |
| GET | `/health` | Return service health status. |

## 7. Data Requirements

### 7.1 Resume Data

Required identity: `resume_id`, `status`.  
Optional fields: `name`, `email`, `phone`, `technical_skills`, `soft_skills`, `projects`, `experience`, `education`, `github_username`, `leetcode_username`, `job_description`, and `raw_text`.

### 7.2 Verification Result

A verification result shall contain the resume ID, status, provider results, verified skills, unverified skills, verified projects, unverified projects, and any error information. Provider data should include enough evidence references to support the displayed result in a production release.

### 7.3 Score Result

A score result shall contain the resume ID, overall score, component breakdown, verified and unverified claims, optional role-fit data, and optional ATS analysis.

### 7.4 Data Quality Rules

- Resume IDs must be unique within the storage lifetime.
- Status values must be controlled: `processing`, `completed`, or `error`.
- Scores must be bounded from 0 to 100.
- A missing external profile must be distinguishable from a failed provider request.
- Personal data must not be placed in logs unless required for support and approved by policy.

## 8. Use Cases and Acceptance Criteria

### UC-01: Audit a Resume

**Actor:** Recruiter or interviewer  
**Preconditions:** User has a PDF/DOCX resume.  
**Success flow:** Upload, parse, verify available profiles, calculate score, display evidence.  
**Acceptance criteria:**

- Valid PDF/DOCX upload returns a unique resume ID.
- Invalid file type is rejected with a clear message.
- Parsed resume reaches `completed` or a meaningful error state.
- Verification results distinguish verified and unverified claims.
- Score includes overall value and breakdown.
- Results identify unavailable provider data rather than hiding it.

### UC-02: Improve and Export a Resume

**Actor:** Candidate or recruiter  
**Preconditions:** User has a PDF/DOCX resume or editable resume text.  
**Success flow:** Open editor, edit content, inspect ATS/role fit, export DOCX.  
**Acceptance criteria:**

- Editor accepts supported document formats.
- ATS analysis updates for submitted text.
- Job description analysis is optional.
- Export downloads a readable DOCX file.

### UC-03: Send an Interview Invitation

**Actor:** Recruiter  
**Preconditions:** Resume, candidate email, and score exist.  
**Success flow:** Enter optional details, confirm, queue invitation, show status.  
**Acceptance criteria:**

- Missing resume, score, or email prevents sending.
- Message, date, and location are passed to the email service.
- API returns a clear sent or failed status.
- Production release records delivery outcome.

## 9. Traceability Matrix

| Business need | SRS requirements | Verification method |
|---|---|---|
| Reduce manual resume review time | FR-001 to FR-007, FR-020 to FR-025 | API and UI integration tests |
| Validate technical claims | FR-010 to FR-019 | Provider contract tests and fixture tests |
| Give fair, explainable feedback | FR-017, FR-018, FR-028, NFR-008, NFR-014 | Stakeholder review and usability tests |
| Improve resume quality | FR-029 to FR-034 | Editor and export tests |
| Support recruiter follow-up | FR-035 to FR-040 | Invitation workflow tests |
| Protect candidate data | NFR-004 to NFR-009, NFR-017 | Security, privacy, and deletion tests |
| Operate reliably | FR-041 to FR-044, NFR-001 to NFR-003, NFR-010 to NFR-012 | Failure injection and monitoring tests |

## 10. Assumptions, Constraints, and Risks

### Assumptions

- Users provide resumes they are authorized to process.
- GitHub and LeetCode handles are public or accessible through approved APIs.
- A score supports human review and does not make a final hiring decision.
- Initial deployment may use Docker and a local or serverless environment.

### Constraints

- The current prototype uses in-memory storage.
- External API rate limits and availability can affect verification.
- Resume formats vary and may not extract perfectly.
- Current processing and some scoring work occurs synchronously.

### Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Soft skills are treated as failed technical claims | Unfair score reduction | Separate skill categories and validate scoring policy with stakeholders. |
| Missing public evidence is interpreted as dishonesty | Candidate harm | Use an `unknown` state, show limitations, and require human review. |
| Provider changes or rate limits | Incomplete audits | Timeouts, retries, caching, provider status, and manual retry. |
| In-memory storage loses data | Reliability and privacy risk | Introduce persistent storage, retention rules, and backups before production. |
| Parsing errors alter candidate information | Incorrect audit | Preview, correction workflow, confidence indicators, and test fixtures. |
| Automated score creates hiring bias | Legal and reputational risk | Explainability, human oversight, bias review, and no automatic rejection. |

## 11. Open Questions and Approval Checklist

The following must be resolved before treating this SRS as baselined:

- [ ] Approve stakeholder roles and primary user.
- [ ] Confirm whether technical and soft skills are scored separately.
- [ ] Define the treatment of missing profiles and unavailable providers.
- [ ] Approve score weights, explanation requirements, and policy versioning.
- [ ] Approve consent, retention, deletion, and correction policies.
- [ ] Define authentication and authorization requirements.
- [ ] Confirm performance, availability, and scale targets.
- [ ] Confirm production database and backup requirements.
- [ ] Approve the invitation approval and delivery workflow.
- [ ] Review all proposed requirements with stakeholders and assign priorities.

## 12. References to Current Implementation

- Backend entry point and API composition: `backend/app/main.py`, `backend/app/api/routes.py`
- Resume workflow: `backend/app/api/endpoints/resume.py`, `backend/app/services/resume_parser.py`
- Verification workflow: `backend/app/api/endpoints/verification.py`, `backend/app/services/github_service.py`, `backend/app/services/leetcode_service.py`
- Scoring workflow: `backend/app/api/endpoints/score.py`, `backend/app/services/scoring_service.py`
- ATS and role fit: `backend/app/services/ats_service.py`, `backend/app/services/job_matching_service.py`
- Invitation workflow: `backend/app/api/endpoints/invite.py`, `backend/app/services/email_service.py`
- Frontend workflows: `frontend/src/pages/UploadPage.js`, `frontend/src/pages/ResultsPage.js`, `frontend/src/pages/ResumeEditorPage.js`
