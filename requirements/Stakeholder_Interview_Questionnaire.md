# ProfileAuditor Stakeholder Interview and Questionnaire

**Project:** ProfileAuditor  
**Purpose:** Elicit, validate, and prioritize software requirements for resume auditing and candidate verification.  
**Version:** 1.0  
**Date:** 2026-09-23

## 1. Stakeholder Groups

| Stakeholder | Interest | Information to collect |
|---|---|---|
| Recruiter / hiring manager | Fast, explainable candidate screening | Workflow, decisions, score interpretation, invitation process |
| Technical interviewer | Trustworthy evidence of technical claims | Verification depth, evidence quality, false positives |
| Candidate | Fairness, privacy, and useful resume feedback | Consent, correction, visibility, export, dispute process |
| Product owner | Business value and adoption | MVP scope, priorities, success measures |
| System administrator | Reliability, security, and operations | Deployment, monitoring, integrations, retention |
| Legal / privacy reviewer | Compliance and responsible processing | Consent, public data use, deletion, access control |

## 2. Interview Protocol

1. Explain the purpose, expected duration, and how responses will be recorded.
2. Ask open questions before showing the current interface.
3. Separate current workflow problems from proposed solutions.
4. Ask for concrete examples and edge cases.
5. Confirm each important requirement in the stakeholder's own words.
6. Mark each requirement as **Must**, **Should**, **Could**, or **Won't** for the release.
7. Record unresolved questions and assign an owner for follow-up.

**Suggested duration:** 30-45 minutes per stakeholder.  
**Evidence to capture:** direct quote, observed workflow, pain point, requirement, priority, acceptance test, and dependency.

## 3. Common Opening Questions

1. What decision are you trying to make with a candidate resume?
2. What information do you currently collect, and where does it come from?
3. Which parts of the current process take the most time?
4. Which errors would be most costly or unfair?
5. What would make you trust an audit result?
6. What must the first release do for you to use it in a real workflow?
7. What should the system never do automatically?
8. How would you measure whether ProfileAuditor is successful?

## 4. Recruiter / Hiring Manager Questions

### Workflow

1. How do you currently receive, store, and review resumes?
2. Do you review one candidate at a time or compare candidates in batches?
3. At what point should a resume be verified?
4. Should verification be automatic after upload or explicitly started by the recruiter?
5. What information should appear first on the results page?
6. What actions should be available from the results page?

### Scoring and decisions

1. What does a score from 0 to 100 mean in your decision process?
2. Should the system show one overall score, multiple scores, or both?
3. Which evidence should contribute to the score: projects, skills, commits, stars, coding problems, or other signals?
4. Should missing public profiles reduce a score, be marked unknown, or be excluded?
5. How should a recruiter interpret conflicting evidence?
6. What explanation is required before you would use a score in screening?
7. Should recruiters be able to override or annotate a score?

### Communication

1. When should an interview invitation be available?
2. Which fields should be editable before sending an invitation?
3. Should the system keep a history of invitations and delivery status?
4. Which email provider and organizational templates must be supported?

## 5. Technical Interviewer Questions

1. What makes a GitHub repository credible evidence of candidate ownership?
2. How should forks, copied templates, inactive repositories, and shared commits be treated?
3. Which programming languages and technical skills must be recognized?
4. How should a project claim be matched to a repository?
5. Which LeetCode metrics matter: total solved, difficulty, ranking, recent activity, or language usage?
6. What evidence is sufficient to mark a skill as verified?
7. What evidence should be shown when a claim cannot be verified?
8. How should the system distinguish technical skills from soft skills?
9. What should happen when an external API is unavailable or returns incomplete data?
10. What false-positive and false-negative rates are acceptable for an initial release?

## 6. Candidate Questions

1. What information are you comfortable uploading and processing?
2. What consent should be requested before public GitHub or LeetCode data is accessed?
3. Should you be able to preview the extracted resume data before an audit begins?
4. Which extracted fields must be correctable?
5. Should you be able to explain or dispute an unverified claim?
6. What feedback would make the resume editor useful?
7. Which ATS suggestions are helpful, and which could be misleading?
8. Should you be able to export the improved resume as DOCX or PDF?
9. How long should uploaded resumes and audit results be retained?
10. How should you request deletion or correction of your data?

## 7. Product Owner Questions

1. Who is the primary user for the first release?
2. Is the MVP focused on individual resume audits, recruiter pipelines, or both?
3. Which integrations are required for launch?
4. What are the top three measurable outcomes for the first release?
5. Which features may be mocked or rule-based initially?
6. What is the expected number of resumes per day and per month?
7. What is the acceptable audit completion time?
8. What is explicitly out of scope for the first release?
9. Which risks require mitigation before pilot use?
10. What is the release acceptance authority?

## 8. Administrator and Privacy Questions

1. Where may resume files and extracted data be stored?
2. Is in-memory storage acceptable outside development and demonstration environments?
3. What authentication and authorization roles are required?
4. Which events must be audited?
5. Which secrets and external API credentials need rotation and monitoring?
6. What is the retention period for files, extracted data, verification results, and email logs?
7. How should consent, deletion, and access requests be handled?
8. Are public-profile terms of service or rate limits applicable to each integration?
9. What availability, backup, and recovery targets are required?
10. What security testing is required before production deployment?

## 9. Questionnaire for Broader Response Collection

Use a 1-5 scale where **1 = strongly disagree** and **5 = strongly agree**.

| Statement | Rating |
|---|---:|
| Resume upload should accept PDF and DOCX files. | 1 2 3 4 5 |
| Extracted resume data should be reviewable before verification. | 1 2 3 4 5 |
| Verification should require explicit user confirmation. | 1 2 3 4 5 |
| Every score should include an evidence breakdown. | 1 2 3 4 5 |
| Missing public profiles should not automatically imply dishonesty. | 1 2 3 4 5 |
| Technical and soft skills should be scored separately. | 1 2 3 4 5 |
| Candidates should be able to correct extracted information. | 1 2 3 4 5 |
| Candidates should be able to dispute an unverified claim. | 1 2 3 4 5 |
| The system should show when external data is unavailable. | 1 2 3 4 5 |
| Recruiters should be able to send an interview invitation from results. | 1 2 3 4 5 |
| Audit results should be retained for later review. | 1 2 3 4 5 |
| Resume and public-profile data should be deleted on request. | 1 2 3 4 5 |

**Open response:** Which one feature would provide the greatest value?  
**Open response:** Which one behavior would make you distrust the system?  
**Open response:** What requirement is missing from this questionnaire?

## 10. Requirements Capture Template

| ID | Stakeholder | Need / observation | Requirement statement | Priority | Acceptance evidence | Owner |
|---|---|---|---|---|---|---|
| ELIC-001 |  |  |  | Must / Should / Could / Won't |  |  |
| ELIC-002 |  |  |  | Must / Should / Could / Won't |  |  |
| ELIC-003 |  |  |  | Must / Should / Could / Won't |  |  |

## 11. Decisions Requiring Validation

1. Should soft skills be excluded from the technical verification score rather than marked unverified?
2. Should a missing GitHub or LeetCode profile be treated as **unknown** instead of evidence against the candidate?
3. Should the product support recruiter accounts and multiple candidates in a persistent database?
4. What minimum explanation and evidence must accompany a Reality Score?
5. What consent and retention policy is required before production use?
6. Is automated interview invitation sending allowed, or must a recruiter approve the final message?

## 12. Outputs After Interviews

The completed elicitation activity should produce:

- Approved stakeholder list and assumptions.
- Prioritized functional and non-functional requirements.
- Glossary of domain terms such as **Reality Score**, **verified claim**, and **public evidence**.
- Updated use cases and acceptance criteria.
- Decision log for unresolved questions.
- Traceability from stakeholder evidence to SRS requirements and tests.
