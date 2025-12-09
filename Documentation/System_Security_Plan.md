# System Security Plan (SSP)
## LLM Guardrails Demo API

**Classification:** Unclassified  
**Version:** 1.0  
**Date:** December 9, 2024  
**Prepared by:** Shirin Bashar  
**Security Category:** FIPS 199 Low Impact

---

## 1. SYSTEM IDENTIFICATION

### 1.1 System Name
**LLM Guardrails Demo API**

### 1.2 System Description
A Flask-based REST API that provides AI-powered text generation with integrated security guardrails. The system uses OpenAI's GPT-4o-mini model with real-time input/output validation to prevent toxic content generation, PII leakage, and prompt injection attacks.

### 1.3 System Purpose
To demonstrate secure implementation of Large Language Model (LLM) APIs with defense-in-depth security controls for agentic AI systems. The system serves as a proof-of-concept for implementing NIST RMF controls in AI-powered applications.

### 1.4 System Components

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Web Framework | Flask | 3.1.2 | REST API server |
| LLM Provider | OpenAI GPT-4o-mini | API v1 | AI text generation |
| Security Controls | Guardrails AI | 0.7.0 | Input/output validation |
| Observability | Arize Phoenix | 4.0+ | Tracing and monitoring |
| Language | Python | 3.13 | Application runtime |

### 1.5 System Environment
- **Deployment:** Local development (Port 8080)
- **Future State:** Cloud deployment (AWS/Azure recommended)
- **Network:** Private network during development
- **Access:** API key authentication

### 1.6 System Boundaries
**In Scope:**
- Flask REST API application (`/ask`, `/health`, `/stats` endpoints)
- Guardrails AI validators (ToxicLanguage, DetectPII)
- OpenAI API integration
- Phoenix observability dashboard
- Python automation scripts

**Out of Scope:**
- OpenAI's internal infrastructure
- Phoenix cloud services
- Operating system hardening
- Network infrastructure

---

## 2. SECURITY CATEGORIZATION

### 2.1 FIPS 199 Categorization

Per NIST FIPS 199, the system security categorization is:

**SC LLM-API = {(confidentiality, LOW), (integrity, MODERATE), (availability, LOW)}**

**Overall System Categorization: MODERATE**

### 2.2 Categorization Rationale

| Security Objective | Impact Level | Justification |
|-------------------|--------------|---------------|
| **Confidentiality** | LOW | System processes user prompts but stores no persistent PII. API keys protected via environment variables. Temporary data in memory only. |
| **Integrity** | MODERATE | Integrity of AI responses critical - toxic content or manipulated outputs could harm users or violate policies. Guardrails ensure output integrity. |
| **Availability** | LOW | System downtime affects demo/testing only. No critical business operations dependent on availability. Can tolerate temporary outages. |

---

## 3. SYSTEM ARCHITECTURE

### 3.1 System Diagram

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │ HTTPS (recommended)
       ▼
┌─────────────────────────────────────────┐
│   Flask REST API (Port 8080)            │
│   ┌───────────────────────────────┐    │
│   │  Input Validation Layer       │    │
│   │  - ToxicLanguage Filter       │    │
│   │  - PII Detection & Redaction  │    │
│   └───────────┬───────────────────┘    │
│               ▼                         │
│   ┌───────────────────────────────┐    │
│   │  LLM Integration Layer        │    │
│   │  - OpenAI API Client          │    │
│   │  - Request Handling           │    │
│   └───────────┬───────────────────┘    │
│               ▼                         │
│   ┌───────────────────────────────┐    │
│   │  Output Validation Layer      │    │
│   │  - Response Sanitization      │    │
│   │  - Guardrails Validation      │    │
│   └───────────────────────────────┘    │
└──────────┬──────────────────────────────┘
           │
           ├──────────────┐
           ▼              ▼
    ┌─────────────┐  ┌──────────────┐
    │  OpenAI     │  │   Phoenix    │
    │  GPT-4o     │  │ Observability│
    │  (External) │  │ (Port 6006)  │
    └─────────────┘  └──────────────┘
```

### 3.2 Data Flow

1. User submits prompt via POST `/ask`
2. Input validation via Guardrails (toxic content, PII detection)
3. If validation passes, request forwarded to OpenAI API
4. LLM generates response
5. Output validation via Guardrails
6. Sanitized response returned to user
7. All interactions logged to Phoenix for monitoring

### 3.3 User Roles

| Role | Access Level | Permissions |
|------|-------------|-------------|
| API Consumer | Authenticated | Submit prompts, receive responses |
| Administrator | Full Access | Configure guardrails, view logs, manage keys |
| Security Analyst | Read-Only | View Phoenix traces, analyze security events |

---

## 4. NIST 800-53 SECURITY CONTROL IMPLEMENTATION

### AC-2: Account Management

**Control Description:** Manage system accounts including creation, modification, and removal.

**Implementation:**
- API access requires valid API key stored in `.env` file
- Each request includes `user_id` for accountability
- API keys rotated per security policy (recommended: 90 days)
- No default or shared accounts

**Implementation Status:** ✅ Implemented  
**Evidence:** Environment variable configuration, request logging with user attribution

---

### IA-2: Identification and Authentication (Organizational Users)

**Control Description:** Uniquely identify and authenticate organizational users.

**Implementation:**
- OpenAI API key authentication for LLM access
- API key validation on application startup
- Failed authentication logged and blocked
- Keys stored securely in `.env` (excluded from version control)

**Implementation Status:** ✅ Implemented  
**Evidence:** `.gitignore` includes `.env`, startup validation check, secure key storage

---

### SC-7: Boundary Protection

**Control Description:** Monitor and control communications at external boundaries.

**Implementation:**
- Input validation at API boundary (Guardrails AI)
- Output sanitization before response transmission
- Toxic content blocked at boundary
- PII redacted before external transmission
- Future: HTTPS/TLS encryption, WAF deployment

**Implementation Status:** ✅ Implemented (application layer)  
**Planned Enhancement:** Network layer protections (firewall, WAF)  
**Evidence:** Guardrails validators, Phoenix trace logs showing blocked requests

---

### AU-2: Audit Events

**Control Description:** Determine and log security-relevant events.

**Implementation:**
- All API requests logged with timestamp, user_id, prompt, response
- Guardrails decisions logged (pass/block/modify)
- Security events captured: toxic content attempts, PII detection, validation failures
- Token usage and latency tracked per request

**Events Logged:**
- Successful API calls
- Blocked toxic content
- PII redaction actions
- Authentication failures
- Configuration changes

**Implementation Status:** ✅ Implemented  
**Evidence:** Phoenix observability dashboard, `api_logs.jsonl` file, 14+ traces captured

---

### AU-6: Audit Review, Analysis, and Reporting

**Control Description:** Review and analyze audit records for inappropriate or unusual activity.

**Implementation:**
- Real-time monitoring via Phoenix dashboard (http://localhost:6006)
- Automated security scan reports (`security_summary.md`)
- Security posture scoring (0-100 scale)
- Metrics tracked: block rate, latency P50/P99, token usage, cost
- Guardrails effectiveness analysis

**Review Frequency:** Real-time (Phoenix), Weekly (automated reports)

**Implementation Status:** ✅ Implemented  
**Evidence:** Phoenix dashboard, automated reporting script, security metrics

---

### CM-2: Baseline Configuration

**Control Description:** Develop, document, and maintain baseline configuration.

**Implementation:**
- Application dependencies defined in `requirements.txt`
- Configuration managed via environment variables (`.env` template)
- Version control for all code and configuration
- Infrastructure-as-Code (future: Terraform/CloudFormation)

**Baseline Components:**
- Python 3.13
- Flask 3.1.2
- Guardrails AI 0.7.0
- OpenAI SDK 1.109.1
- Security validators: ToxicLanguage, DetectPII

**Configuration Management:**
- Git version control
- `.gitignore` prevents credential exposure
- Documented deployment procedures

**Implementation Status:** ✅ Implemented  
**Evidence:** `requirements.txt`, `.env` template, Git repository

---

### SI-2: Flaw Remediation

**Control Description:** Identify, report, and correct system flaws.

**Implementation:**
- Automated SAST scanning via Bandit (weekly recommended)
- Dependency vulnerability scanning via pip-audit
- Security automation script generates remediation reports
- Findings prioritized by severity (HIGH/MEDIUM/LOW)
- Guardrails provide runtime vulnerability prevention

**Remediation Process:**
1. Automated scan identifies vulnerabilities
2. Security report generated with severity ratings
3. High severity issues block production deployment
4. Medium/Low severity tracked and scheduled for remediation
5. Fixes validated via re-scan

**Current Status:**
- 1 HIGH severity: Flask debug mode (accepted risk for dev)
- 2 MEDIUM severity: Configuration improvements
- Remediation plan documented in SAST report

**Implementation Status:** ✅ Implemented  
**Evidence:** Bandit reports, automated security scan script, remediation tracking

---

### SI-10: Information Input Validation

**Control Description:** Check validity of information inputs.

**Implementation:**
- Multi-layer input validation architecture
- Guardrails AI validates all user inputs before LLM processing
- Toxic language detection with 0.5 threshold
- PII detection for EMAIL, PHONE, CREDIT_CARD
- Prompt length limits (2000 characters)
- JSON schema validation for API requests

**Validation Rules:**
- Empty prompts rejected
- Toxic content blocked with detailed error message
- PII automatically redacted using placeholders
- Malformed requests return 400 Bad Request

**Effectiveness:** 100% of requests validated (per Phoenix traces)

**Implementation Status:** ✅ Implemented  
**Evidence:** Guardrails configuration, Phoenix traces showing blocked toxic content, PII redaction examples

---

### PL-8: Security and Privacy Architectures

**Control Description:** Develop security and privacy architectures.

**Implementation:**
- Defense-in-depth security architecture
- Zero Trust principles: validate all inputs/outputs
- Privacy-by-design: PII detection at all boundaries
- Threat model documented (Agentic AI Threat Model)
- Security controls mapped to NIST 800-53

**Architecture Principles:**
1. **Least Privilege:** API keys scoped to minimum required permissions
2. **Defense in Depth:** Input validation → LLM processing → Output validation
3. **Fail Secure:** Validation failures block requests (not bypass)
4. **Audit Everything:** Comprehensive logging and tracing
5. **Privacy First:** PII redacted before processing or storage

**Security Layers:**
- Layer 1: API authentication
- Layer 2: Input validation (Guardrails)
- Layer 3: LLM processing (vendor-managed security)
- Layer 4: Output validation (Guardrails)
- Layer 5: Monitoring and alerting (Phoenix)

**Implementation Status:** ✅ Implemented  
**Evidence:** System architecture diagram, threat model, layered security implementation

---

## 5. RISK ASSESSMENT

### 5.1 Identified Risks

| Risk ID | Threat | Likelihood | Impact | Risk Level | Mitigation |
|---------|--------|------------|--------|------------|------------|
| R-01 | Prompt Injection Attack | HIGH | HIGH | **CRITICAL** | Input validation via Guardrails, monitoring |
| R-02 | Toxic Content Generation | MEDIUM | HIGH | **HIGH** | ToxicLanguage validator, output sanitization |
| R-03 | PII Data Leakage | MEDIUM | CRITICAL | **CRITICAL** | DetectPII validator, automatic redaction |
| R-04 | API Key Compromise | LOW | CRITICAL | **HIGH** | Secure storage in `.env`, key rotation |
| R-05 | Model Misuse/Abuse | MEDIUM | MEDIUM | **MEDIUM** | Rate limiting (planned), usage monitoring |
| R-06 | Debug Mode in Production | HIGH | CRITICAL | **CRITICAL** | Configuration validation, deployment checklist |
| R-07 | Dependency Vulnerabilities | MEDIUM | MEDIUM | **MEDIUM** | Automated scanning, regular updates |
| R-08 | Insufficient Logging | LOW | MEDIUM | **LOW** | Phoenix observability, comprehensive logging |

### 5.2 Residual Risk

**Overall Residual Risk: LOW to MEDIUM**

After implementing security controls, residual risks are acceptable for the system's LOW-MODERATE categorization. Critical risks (R-01, R-03, R-06) have effective technical controls in place.

**Accepted Risks:**
- Flask debug mode enabled (development environment only)
- Local deployment without HTTPS (dev/test environment)
- Basic API key authentication (vs. OAuth2/JWT)

**Conditions for Acceptance:**
- Not deployed to production
- Used in controlled development environment
- Network access restricted

---

## 6. SECURITY CONTROLS ASSESSMENT

### 6.1 Control Testing Results

| Control | Status | Test Method | Results | Next Assessment |
|---------|--------|-------------|---------|-----------------|
| AC-2 | ✅ Pass | Manual review | API key auth functional | 90 days |
| IA-2 | ✅ Pass | Manual review | Authentication enforced | 90 days |
| SC-7 | ✅ Pass | Functional testing | Guardrails blocking toxic content | 30 days |
| AU-2 | ✅ Pass | Log review | All events captured | 30 days |
| AU-6 | ✅ Pass | Dashboard review | Real-time monitoring active | 30 days |
| CM-2 | ✅ Pass | Config audit | Baseline documented | 90 days |
| SI-2 | ✅ Pass | Automated scan | SAST findings documented | 7 days |
| SI-10 | ✅ Pass | Functional testing | 100% input validation | 30 days |
| PL-8 | ✅ Pass | Architecture review | Defense-in-depth implemented | 180 days |

### 6.2 Security Testing Evidence

**Evidence Available:**
1. Phoenix trace logs (14+ requests)
2. Bandit SAST report (JSON, TXT, HTML)
3. Automated security scan results
4. Guardrails validation examples
5. PII redaction demonstrations
6. Configuration audit results

---

## 7. CONTINUOUS MONITORING STRATEGY

### 7.1 Monitoring Tools

| Tool | Purpose | Frequency | Metrics |
|------|---------|-----------|---------|
| Phoenix Dashboard | Real-time request monitoring | Continuous | Latency, errors, guardrails actions |
| Bandit SAST | Code vulnerability scanning | Weekly | HIGH/MEDIUM/LOW findings |
| pip-audit | Dependency vulnerabilities | Weekly | CVE count, severity |
| Security Automation | Comprehensive security checks | On-demand | Security score, posture |

### 7.2 Key Performance Indicators (KPIs)

- **Security Score:** Target ≥85/100
- **Guardrails Block Rate:** < 5% (indicates normal usage)
- **High Severity Findings:** 0 (blocker for production)
- **PII Redaction Rate:** 100% of detected instances
- **Average Response Latency:** < 3 seconds
- **Authentication Failure Rate:** < 1%

### 7.3 Incident Response

**Detection:**
- Automated alerts for high severity security events
- Real-time monitoring via Phoenix
- Automated scan failures

**Response:**
1. Security analyst reviews Phoenix traces
2. Incident categorized (LOW/MEDIUM/HIGH/CRITICAL)
3. Immediate mitigation if CRITICAL
4. Root cause analysis
5. Remediation and validation
6. Lessons learned documentation

---

## 8. SYSTEM INTERCONNECTIONS

### 8.1 External Systems

| System | Interface | Data Exchanged | Security Controls |
|--------|-----------|----------------|-------------------|
| OpenAI API | HTTPS REST | User prompts, AI responses | API key auth, TLS encryption |
| Phoenix (Local) | HTTP | Trace data, metrics | Local network only |

### 8.2 Data Flows

**Inbound:**
- User prompts (validated before processing)
- API authentication credentials (environment variables)

**Outbound:**
- AI responses (sanitized by guardrails)
- Telemetry data to Phoenix (local only)
- OpenAI API requests (encrypted via TLS)

---

## 9. COMPLIANCE AND REGULATIONS

### 9.1 Applicable Standards

- **NIST Risk Management Framework (RMF)**
- **NIST SP 800-53 Rev 5** - Security and Privacy Controls
- **NIST SP 800-171** - Protecting CUI (if applicable)
- **OWASP Top 10 for LLM Applications**
- **FIPS 199** - Security Categorization

### 9.2 Privacy Compliance

**PII Protection:**
- Automatic PII detection and redaction
- No persistent storage of PII
- Compliance support for GDPR, CCPA

**Data Retention:**
- Logs retained for 30 days
- No PII in permanent storage
- Right to deletion supported

---

## 10. PLAN OF ACTION AND MILESTONES (POA&M)

### 10.1 Open Findings

| ID | Finding | Severity | Remediation | Due Date | Status |
|----|---------|----------|-------------|----------|--------|
| F-01 | Flask debug mode enabled | HIGH | Configure via environment variable | Before Prod | Open |
| F-02 | Binding to all interfaces | MEDIUM | Deploy behind reverse proxy | Before Prod | Open |
| F-03 | Missing request timeout | MEDIUM | Add 30s timeout to requests | 2024-12-15 | Open |
| F-04 | No rate limiting | MEDIUM | Implement Flask-Limiter | 2025-01-15 | Planned |
| F-05 | HTTP only (no HTTPS) | HIGH | Enable TLS/SSL | Before Prod | Planned |

### 10.2 Planned Enhancements

**Short-term (30 days):**
- Implement rate limiting (100 requests/hour)
- Add API key rotation policy
- Enable HTTPS for all connections
- Implement comprehensive error handling

**Medium-term (90 days):**
- Deploy to cloud with WAF protection
- Implement OAuth2/JWT authentication
- Add advanced guardrails (jailbreak detection)
- Automated dependency updates

**Long-term (180 days):**
- Achieve FedRAMP compliance (if required)
- Implement zero-trust architecture
- Add advanced threat detection
- Conduct penetration testing

---

## 11. AUTHORIZATION

### 11.1 Security Authorization Decision

**Authorizing Official:** [To Be Determined]  
**Authorization Decision:** Conditional Authorization  
**Authorization Date:** [Pending Production Deployment]  

**Conditions:**
1. Flask debug mode must be disabled for production
2. HTTPS/TLS must be enabled
3. All HIGH severity findings remediated
4. Rate limiting implemented
5. Production deployment behind WAF

**Authorization Termination Date:** [TBD + 12 months]

### 11.2 Prepared By

**Information System Security Officer (ISSO):** Shirin Bashar  
**Date:** December 9, 2024  
**Signature:** ____________________

---

## 12. APPENDICES

### Appendix A: Acronyms

- **API** - Application Programming Interface
- **FIPS** - Federal Information Processing Standard
- **LLM** - Large Language Model
- **NIST** - National Institute of Standards and Technology
- **PII** - Personally Identifiable Information
- **POA&M** - Plan of Action and Milestones
- **RMF** - Risk Management Framework
- **SAST** - Static Application Security Testing
- **SSP** - System Security Plan
- **TLS** - Transport Layer Security

### Appendix B: References

1. NIST SP 800-53 Rev 5: Security and Privacy Controls
2. NIST SP 800-37 Rev 2: Risk Management Framework
3. NIST FIPS 199: Standards for Security Categorization
4. OWASP Top 10 for LLM Applications 2023
5. Guardrails AI Documentation
6. Arize Phoenix Documentation

### Appendix C: Supporting Documentation

- Agentic AI Threat Model
- SAST Findings Summary (Bandit Report)
- Security Automation Script and README
- System Architecture Diagrams
- Configuration Baseline Documentation
- Audit Logs and Phoenix Traces

---

**Document Control:**
- **Version:** 1.0
- **Classification:** Unclassified
- **Review Frequency:** Annually or upon significant system changes
- **Next Review Date:** December 9, 2025
- **Document Owner:** Shirin Bashar

---

*This System Security Plan is prepared in accordance with NIST SP 800-18 Rev 1 and supports the Risk Management Framework (RMF) assessment and authorization process.*