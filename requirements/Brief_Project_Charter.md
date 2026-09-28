# ProfileAuditor Brief Project Charter

**Project:** ProfileAuditor  
**Version:** 1.0  
**Date:** 2026-09-23  
**Status:** Draft for approval

## 1. Project Purpose

ProfileAuditor will provide a human-assisted platform for reviewing technical resume claims. It will extract resume information, compare available claims with public GitHub and LeetCode evidence, calculate an explainable Reality Score, provide ATS and role-fit feedback, and support recruiter-approved interview invitations.

## 2. Business Need

Technical resume review can be slow, inconsistent, and difficult to substantiate. ProfileAuditor aims to reduce manual verification effort while giving recruiters evidence-based review support and candidates actionable resume feedback.

## 3. Objectives

- Accept and parse PDF and DOCX resumes.
- Verify available technical skills and projects against public technical evidence.
- Present verified, unverified, and unavailable evidence clearly.
- Calculate a 0-100 Reality Score with a component breakdown.
- Provide ATS health and optional job role-fit analysis.
- Allow resume editing and DOCX export.
- Enable a recruiter to send an approved interview invitation.
- Validate fairness, privacy, usability, and technical feasibility through a controlled pilot.

## 4. In Scope

- Resume upload, text extraction, and structured parsing.
- GitHub and LeetCode verification workflows.
- Reality Score and score breakdown.
- ATS analysis and job-description matching.
- Resume editor and DOCX export.
- Results dashboard and recruiter invitation workflow.
- Stakeholder validation, acceptance criteria, and pilot evaluation.

## 5. Out of Scope

- Automated hiring or rejection decisions.
- Full applicant tracking system functionality.
- Persistent multi-tenant recruiter accounts in the MVP.
- Candidate ranking across a large resume database.
- Guaranteed identity or authorship verification.
- Complete LinkedIn and Twitter verification.

## 6. Key Deliverables

| Deliverable | Description |
|---|---|
| Working MVP | React and FastAPI application supporting the core audit workflow. |
| Stakeholder findings | Interview notes, questionnaire results, decisions, and prioritized requirements. |
| SRS | Baseline functional and non-functional requirements with acceptance criteria. |
| UML diagrams | Use case, class, activity, and sequence views of the system. |
| Feasibility study | Problem alternatives, feasibility assessment, risks, and recommendation. |
| Pilot report | Usability, accuracy, fairness, reliability, and stakeholder feedback results. |

## 7. Stakeholders and Responsibilities

| Role | Responsibility |
|---|---|
| Product owner | Approves scope, priorities, success measures, and release decisions. |
| Project team | Designs, implements, tests, documents, and demonstrates the product. |
| Recruiter / hiring manager | Validates screening workflow, score interpretation, and invitation needs. |
| Technical interviewer | Validates technical evidence and verification quality. |
| Candidate representative | Validates fairness, correction, feedback, and privacy expectations. |
| Administrator | Validates deployment, monitoring, security, and support needs. |
| Privacy / legal reviewer | Approves data handling, consent, retention, and disclosure requirements. |

## 8. High-Level Milestones

| Milestone | Exit condition |
|---|---|
| M1: Problem validation | Stakeholders confirm the problem, users, and measurable outcomes. |
| M2: Requirements baseline | SRS, questionnaire findings, assumptions, and acceptance criteria are approved. |
| M3: MVP stabilization | Core upload, parsing, verification, scoring, ATS, and invitation workflows pass tests. |
| M4: Production-readiness work | Storage, authentication, privacy, observability, provider resilience, and security controls are reviewed. |
| M5: Controlled pilot | Representative users complete audits and feedback is recorded. |
| M6: Release decision | Product owner approves, defers, or rejects broader deployment based on pilot evidence. |

## 9. Success Criteria

The project is successful when:

- A valid resume can be uploaded, parsed, verified, scored, and displayed end to end.
- Users can understand what evidence was found, not found, or unavailable.
- A recruiter can use the results as decision support without treating them as an automatic hiring decision.
- Candidates can receive useful ATS feedback and export edited content.
- Critical external API failures produce clear, recoverable states.
- Stakeholders approve the privacy, fairness, and human-review safeguards.
- Pilot results meet the agreed usability, performance, reliability, and accuracy targets.

## 10. Assumptions and Constraints

- The initial system may use public GitHub and LeetCode data within approved usage limits.
- The current prototype uses in-memory storage and temporary files.
- Resume parsing quality varies by document structure and format.
- External API availability and rate limits may affect audit completeness.
- A human remains responsible for candidate decisions.
- Production deployment requires persistent storage, access control, data retention rules, and secure secret management.

## 11. Major Risks

| Risk | Response |
|---|---|
| Missing public evidence is mistaken for false claims. | Use unknown/unavailable states and explain limitations. |
| Soft skills reduce a technical score unfairly. | Separate skill categories and validate scoring policy. |
| Incorrect parsing changes candidate information. | Add preview, correction, confidence, and fixture-based tests. |
| Provider APIs fail or change. | Add timeouts, retries, caching, monitoring, and manual retry. |
| Resume data is exposed or retained improperly. | Apply access control, encryption, retention, deletion, and logging policies. |
| Automated score introduces bias. | Keep human oversight, test representative cases, and review score policy. |

## 12. Approval Conditions

The charter is ready for approval when stakeholders confirm:

- [ ] Project purpose and primary users.
- [ ] MVP scope and explicit exclusions.
- [ ] Success measures and pilot approach.
- [ ] Ownership and decision-making responsibilities.
- [ ] Privacy, fairness, and human-review principles.
- [ ] Major milestones and feasibility assumptions.
- [ ] Funding, time, and technical resource availability.

## 13. Authorization

| Approval role | Name | Signature / approval | Date |
|---|---|---|---|
| Product owner |  |  |  |
| Project supervisor |  |  |  |
| Privacy / legal reviewer |  |  |  |
| Technical lead |  |  |  |
