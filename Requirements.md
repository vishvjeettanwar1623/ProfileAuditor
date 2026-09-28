# ProfileAuditor Requirements

This document is the single Markdown entry point for requirements elicitation and the Software Requirements Specification.

## Requirements Elicitation

The stakeholder interview and questionnaire guide covers:

- Recruiter, interviewer, candidate, product owner, administrator, and privacy stakeholders.
- Interview protocols and opening questions.
- Workflow, scoring, fairness, verification, privacy, security, and operational questions.
- A 1-5 stakeholder questionnaire.
- Requirements capture template.
- Decisions requiring stakeholder validation.

### Full Elicitation Guide

![[requirements/Stakeholder_Interview_Questionnaire]]

[Open the stakeholder interview questionnaire](requirements/Stakeholder_Interview_Questionnaire.md)

## Software Requirements Specification

The SRS defines:

- Product purpose, scope, actors, and terminology.
- Current architecture and external integrations.
- Functional requirements for upload, parsing, verification, scoring, ATS analysis, editing, export, and invitations.
- Non-functional requirements for performance, privacy, security, reliability, usability, and maintainability.
- API interfaces, data requirements, use cases, acceptance criteria, traceability, risks, and approval checklist.

### Full SRS

![[requirements/Software_Requirements_Specification]]

[Open the full Software Requirements Specification](requirements/Software_Requirements_Specification.md)

## Key Stakeholder Decisions

The following points must be confirmed before the SRS is baselined:

1. Technical skills and soft skills should be scored separately.
2. Missing public profiles should be represented as unknown rather than negative evidence.
3. Every score should include supporting evidence and limitations.
4. Candidate correction, dispute, consent, retention, and deletion workflows must be defined.
5. Production use requires persistent storage, authentication, authorization, and backups.
6. Human reviewers must remain responsible for hiring decisions.

## Problem Selection and Feasibility

The feasibility study documents the selected problem, alternatives considered, technical, operational, economic, legal, and schedule feasibility, risks, success measures, and recommendation to proceed with a controlled MVP.

![[requirements/Problem_Selection_and_Feasibility_Study]]

[Open the problem selection and feasibility study](requirements/Problem_Selection_and_Feasibility_Study.md)

## Brief Project Charter

The project charter defines the purpose, business need, objectives, scope, deliverables, stakeholders, milestones, success criteria, assumptions, risks, and approval conditions.

![[requirements/Brief_Project_Charter]]

[Open the brief project charter](requirements/Brief_Project_Charter.md)

## Architectural Design

The architectural design describes the layered modular-monolith approach for the MVP and the microservice-inspired deployment evolution, including components, dependencies, data flow, reliability, security, trade-offs, and implementation roadmap.

![[requirements/Architectural_Design]]

[Open the architectural design](requirements/Architectural_Design.md)

## ER Diagram and Relational Schema

The database design provides an entity relationship diagram and a normalized relational schema for resumes, skills, projects, verification runs, evidence, scores, ATS analysis, role analysis, and interview invitations.

![[requirements/ER_Diagram_and_Relational_Schema]]

[Open the ER diagram and relational schema](requirements/ER_Diagram_and_Relational_Schema.md)
