# ProfileAuditor UML Diagrams

These diagrams describe the current implementation of ProfileAuditor. They use Mermaid syntax and can be rendered in VS Code with a Mermaid preview extension or on GitHub.

## 1. Use Case Diagram

```mermaid
flowchart LR
    recruiter[Recruiter / Hiring Manager]
    candidate[Candidate]
    github[GitHub API]
    leetcode[LeetCode GraphQL API]
    email[Email Provider]

    subgraph ProfileAuditor[ProfileAuditor System]
        upload((Upload resume))
        parse((Parse resume))
        edit((Edit resume and inspect ATS health))
        verify((Verify technical claims))
        score((Calculate Reality Score))
        view((View audit results))
        invite((Send interview invitation))
        export((Export edited resume))
    end

    recruiter --> upload
    recruiter --> edit
    recruiter --> view
    recruiter --> invite
    candidate --> upload
    candidate --> edit

    upload -. includes .-> parse
    parse -. stores .-> view
    view --> verify
    verify --> github
    verify --> leetcode
    verify -. enables .-> score
    score -. updates .-> view
    edit --> export
    invite --> email
    candidate -. receives .-> email
```

**Primary actors and use cases**

- The recruiter uploads resumes, reviews results, and sends an interview invitation.
- The candidate supplies a resume and may use the resume editor.
- GitHub and LeetCode provide public evidence for verification.
- The email provider delivers the interview invitation in a background task.

## 2. Class Diagram

```mermaid
classDiagram
    class ResumeEndpoint {
        +upload_resume(file, name, email, job_description) ResumeResponse
        +get_resume(resume_id) ResumeData
        +extract_resume_text(file) dict
        +convert_pdf_to_doc(file) dict
        +export_docx(request) Response
    }

    class ResumeParser {
        +extract_text_from_file(file_path) str
        +extract_github_username(text) str
        +extract_leetcode_username(text) str
        +parse_resume(file_path) dict
    }

    class ResumeData {
        +str resume_id
        +str name
        +str email
        +str phone
        +List~str~ technical_skills
        +List~str~ soft_skills
        +List~dict~ projects
        +List~dict~ experience
        +List~dict~ education
        +str github_username
        +str leetcode_username
        +str job_description
        +str raw_text
        +str status
    }

    class VerificationEndpoint {
        +start_verification(resume_id, request) VerificationResponse
        +get_verification(resume_id) VerificationResult
        +process_verification(resume_id, resume_data, handles)
    }

    class VerificationResult {
        +str resume_id
        +str status
        +dict github
        +dict leetcode
        +List~str~ verified_skills
        +List~str~ unverified_skills
        +List~str~ verified_projects
        +List~str~ unverified_projects
    }

    class GitHubService {
        +verify_github_claims(username, skills, projects) dict
    }

    class LeetCodeService {
        +verify_leetcode_claims(username, claimed_skills) dict
    }

    class ScoreEndpoint {
        +get_score(resume_id) ScoreResponse
        +evaluate_live_ats(request) dict
        +calculate_score(resume_id, verification_data) ScoreResponse
    }

    class ScoreResponse {
        +str resume_id
        +float score
        +ScoreBreakdown breakdown
        +List~str~ verified_skills
        +List~str~ unverified_skills
        +float job_fit_score
        +float ats_score
    }

    class ScoreBreakdown {
        +float github_score
        +float leetcode_score
        +float skills_score
        +float projects_score
    }

    class ScoringService {
        +calculate_reality_score(github, leetcode, skills, projects) tuple
        +calculate_github_score(results) float
        +calculate_leetcode_score(results) float
        +calculate_skills_score(verified, unverified) float
        +calculate_projects_score(verified, unverified) float
    }

    class JobMatchingService {
        +evaluate_role_fit(job_description, verification_data) dict
    }

    class ATSService {
        +evaluate_ats_health(raw_text, parsed_resume) dict
    }

    class InviteEndpoint {
        +send_invite(resume_id, request, background_tasks) InviteResponse
    }

    class InviteRequest {
        +str message
        +str interview_date
        +str interview_location
    }

    class EmailService {
        +send_interview_invitation(email, name, score, message, date, location)
    }

    ResumeEndpoint ..> ResumeParser : parses with
    ResumeEndpoint ..> ResumeData : returns
    VerificationEndpoint ..> ResumeData : reads
    VerificationEndpoint ..> VerificationResult : creates
    VerificationEndpoint ..> GitHubService : calls
    VerificationEndpoint ..> LeetCodeService : calls
    ScoreEndpoint ..> VerificationResult : reads
    ScoreEndpoint ..> ScoreResponse : returns
    ScoreEndpoint ..> ScoringService : uses
    ScoreEndpoint ..> JobMatchingService : uses
    ScoreEndpoint ..> ATSService : uses
    ScoreResponse *-- ScoreBreakdown
    InviteEndpoint ..> ResumeData : reads
    InviteEndpoint ..> ScoreResponse : reads
    InviteEndpoint ..> InviteRequest : accepts
    InviteEndpoint ..> EmailService : schedules
```

## 3. Activity Diagram

```mermaid
flowchart TD
    start([Start]) --> choose{Choose workflow}

    choose -->|Audit candidate| select[Select PDF or DOCX resume]
    select --> valid{File type valid?}
    valid -->|No| uploadError[Show upload error]
    uploadError --> stop([End])
    valid -->|Yes| save[Save file and create resume ID]
    save --> parse[Extract text and parse candidate data]
    parse --> parsed{Parsing completed?}
    parsed -->|No| processingError[Store error and return failure]
    processingError --> stop
    parsed -->|Yes| completed[Store resume with completed status]
    completed --> handles[Read GitHub and LeetCode handles]
    handles --> gh{GitHub handle available?}
    gh -->|Yes| github[Verify skills and projects on GitHub]
    gh -->|No| noGithub[Record no GitHub evidence]
    github --> lc{LeetCode handle available?}
    noGithub --> lc
    lc -->|Yes| leetcode[Verify problem-solving evidence on LeetCode]
    lc -->|No| noLeetcode[Record no LeetCode evidence]
    leetcode --> merge[Merge verified and unverified claims]
    noLeetcode --> merge
    merge --> score[Calculate Reality Score, role fit, and ATS health]
    score --> results[Display results dashboard]
    results --> invite{Invite candidate?}
    invite -->|Yes| email[Queue interview email as background task]
    invite -->|No| stop
    email --> stop

    choose -->|Improve resume| editor[Open resume editor]
    editor --> editorInput[Upload or edit resume text]
    editorInput --> ats[Evaluate live ATS health and role fit]
    ats --> export{Export DOCX?}
    export -->|Yes| docx[Generate downloadable DOCX]
    export -->|No| stop
    docx --> stop
```

## 4. Sequence Diagram: Candidate Audit

```mermaid
sequenceDiagram
    actor Recruiter
    participant UI as React ResultsPage
    participant API as FastAPI API
    participant Resume as Resume endpoint
    participant Parser as ResumeParser
    participant Verify as Verification endpoint
    participant GitHub as GitHub service
    participant LeetCode as LeetCode service
    participant Score as Score endpoint
    participant Scoring as Scoring service
    participant Email as Email service

    Recruiter->>UI: Upload PDF/DOCX and candidate details
    UI->>Resume: POST /api/resume/upload
    Resume->>Resume: Generate resume_id and save file
    Resume->>Parser: parse_resume(file_path)
    Parser-->>Resume: ResumeData fields
    Resume-->>UI: ResumeResponse(resume_id, completed)

    UI->>Verify: GET /api/verification/{resume_id}
    Verify-->>UI: 404 when not verified
    UI->>Verify: POST /api/verification/{resume_id}
    Verify->>GitHub: verify_github_claims(handle, skills, projects)
    GitHub-->>Verify: GitHub evidence and verified claims
    Verify->>LeetCode: verify_leetcode_claims(handle, skills)
    LeetCode-->>Verify: LeetCode evidence and verified skills
    Verify->>Verify: Merge verified and unverified skills/projects
    Verify-->>UI: VerificationResponse(completed)

    UI->>Verify: GET /api/verification/{resume_id}
    Verify-->>UI: VerificationResult
    UI->>Score: GET /api/score/{resume_id}
    Score->>Scoring: calculate_reality_score(evidence)
    Scoring-->>Score: score and breakdown
    Score->>Score: Evaluate role fit and ATS health
    Score-->>UI: ScoreResponse
    UI-->>Recruiter: Render Reality Score and audit details

    opt Recruiter sends invitation
        Recruiter->>UI: Submit invitation
        UI->>API: POST /api/invite/{resume_id}
        API->>Email: Queue send_interview_invitation(...)
        API-->>UI: InviteResponse(sent)
        Email-->>Recruiter: Delivery handled asynchronously
    end
```

## Implementation Mapping

- API composition: `backend/app/main.py` and `backend/app/api/routes.py`
- Resume upload and parsing: `backend/app/api/endpoints/resume.py` and `backend/app/services/resume_parser.py`
- Public-profile verification: `backend/app/api/endpoints/verification.py`, `github_service.py`, and `leetcode_service.py`
- Scoring and ATS analysis: `backend/app/api/endpoints/score.py`, `scoring_service.py`, `job_matching_service.py`, and `ats_service.py`
- Interview invitations: `backend/app/api/endpoints/invite.py` and `email_service.py`
- Frontend orchestration: `frontend/src/pages/UploadPage.js`, `ResultsPage.js`, and `ResumeEditorPage.js`

## Notes

- The current backend uses in-memory dictionaries for resume, verification, and score storage. The diagrams therefore show those endpoint-owned stores as part of the service layer rather than as a persistent database.
- Resume processing is currently synchronous inside the upload request. Interview email sending is the explicitly asynchronous part of the main audit workflow.
