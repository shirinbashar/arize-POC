# Agentic AI Threat Model
## LLM Guardrails Demo API

**System:** Flask-based LLM API with OpenAI GPT-4o-mini  
**Security Framework:** Guardrails AI + Phoenix Observability  
**Date:** December 9, 2024  
**Author:** Shirin Bashar

---

## System Overview

The LLM Guardrails Demo is a REST API that provides AI-powered responses with built-in security controls. The system validates both user inputs and AI-generated outputs to prevent security threats common in agentic AI systems.

**Architecture Components:**
- Flask REST API (Port 8080)
- OpenAI GPT-4o-mini LLM
- Guardrails AI validators (ToxicLanguage, DetectPII)
- Phoenix observability dashboard (Port 6006)

---

## Threat Analysis & Mitigations

### 1. Prompt Injection Attacks
**Description:** Malicious users attempt to manipulate the AI through crafted prompts to bypass security controls or extract sensitive information.

**Likelihood:** HIGH  
**Impact:** HIGH  
**Mitigation Status:** ✅ **MITIGATED**

**Controls Implemented:**
- Input validation via Guardrails AI before LLM processing
- System prompt isolation (user prompts cannot override system instructions)
- All inputs logged and traced via Phoenix for anomaly detection

**Evidence:** Phoenix traces show 14 requests processed with input validation applied to 100% of requests.

---

### 2. Toxic Content Generation
**Description:** AI model generates harmful, abusive, or inappropriate content that could harm users or violate policies.

**Likelihood:** MEDIUM  
**Impact:** HIGH  
**Mitigation Status:** ✅ **MITIGATED**

**Controls Implemented:**
- ToxicLanguage validator with 0.5 threshold
- Input validation blocks toxic prompts before reaching LLM
- Output validation prevents toxic responses from being returned

**Evidence:** Phoenix traces show multiple blocked requests with toxic content (red error indicators). Example: "You are stupid and I hate you" was blocked with validation error.

**Sample Blocked Response:**
```json
{
  "error": "Guardrails blocked request: The following sentences 
           in your response were found to be toxic",
  "guardrails_passed": false
}
```

---

### 3. PII Data Leakage
**Description:** Personally Identifiable Information (PII) such as emails, phone numbers, or credit cards could be exposed through AI responses.

**Likelihood:** MEDIUM  
**Impact:** CRITICAL  
**Mitigation Status:** ✅ **MITIGATED**

**Controls Implemented:**
- DetectPII validator identifies EMAIL_ADDRESS, PHONE_NUMBER, CREDIT_CARD
- Automatic redaction using `<EMAIL_ADDRESS>` placeholders
- Both input and output validation prevents PII exposure

**Evidence:** Phoenix traces confirm PII redaction. Example prompt "My email is john@example.com" was automatically sanitized to "My email is <EMAIL_ADDRESS>".

**Compliance:** Supports GDPR, CCPA, and federal privacy requirements.

---

### 4. Model Misuse & Abuse
**Description:** Unauthorized or excessive use of the API, including attempts to extract training data or abuse rate limits.

**Likelihood:** MEDIUM  
**Impact:** MEDIUM  
**Mitigation Status:** ✅ **PARTIALLY MITIGATED**

**Controls Implemented:**
- API key authentication (stored securely in `.env`)
- Request logging with user_id tracking
- Phoenix observability provides real-time monitoring
- Cost tracking per request (<$0.01 total observed)

**Recommended Enhancements:**
- Implement rate limiting (e.g., 100 requests/hour per user)
- Add API key rotation policy
- Set up alerting for anomalous usage patterns

---

### 5. Data Poisoning via Training
**Description:** Adversaries attempt to influence model behavior through malicious training data or fine-tuning.

**Likelihood:** LOW  
**Impact:** HIGH  
**Mitigation Status:** ✅ **MITIGATED**

**Controls Implemented:**
- Using vendor-managed model (OpenAI GPT-4o-mini) - no direct training access
- No user data stored for model fine-tuning
- All interactions are stateless

**Note:** This threat is primarily managed by OpenAI's security controls.

---

### 6. Insecure API Configuration
**Description:** Misconfigured security settings, exposed credentials, or weak access controls.

**Likelihood:** MEDIUM  
**Impact:** CRITICAL  
**Mitigation Status:** ✅ **MITIGATED**

**Controls Implemented:**
- API keys stored in `.env` file (not in code)
- `.gitignore` prevents credential exposure in version control
- Environment variable validation on startup
- HTTPS recommended for production (currently HTTP for local dev)

**Production Recommendations:**
- Deploy with HTTPS/TLS encryption
- Use AWS Secrets Manager or Azure Key Vault for production keys
- Implement WAF (Web Application Firewall)

---

## Risk Assessment Matrix

| Threat | Likelihood | Impact | Risk Level | Mitigation Status | Residual Risk |
|--------|-----------|--------|------------|-------------------|---------------|
| Prompt Injection | HIGH | HIGH | **CRITICAL** | ✅ Mitigated | LOW |
| Toxic Content | MEDIUM | HIGH | **HIGH** | ✅ Mitigated | LOW |
| PII Leakage | MEDIUM | CRITICAL | **CRITICAL** | ✅ Mitigated | LOW |
| Model Misuse | MEDIUM | MEDIUM | **MEDIUM** | ⚠️ Partial | MEDIUM |
| Data Poisoning | LOW | HIGH | **MEDIUM** | ✅ Mitigated | LOW |
| Insecure Config | MEDIUM | CRITICAL | **HIGH** | ✅ Mitigated | LOW |

**Overall Security Posture:** STRONG  
**Residual Risk:** LOW to MEDIUM

---

## Observability & Monitoring

**Phoenix Dashboard Metrics (14 Total Traces):**
- ✅ All requests logged and traced
- ✅ Guardrails validation applied to 100% of requests
- ✅ Multiple toxic content blocks confirmed
- ✅ PII redaction verified in traces
- ✅ Average latency: ~1-3 seconds (acceptable)
- ✅ Cost per request: <$0.01
- ✅ P50 Latency: 1.9s | P99 Latency: 20.4s

**Real-time Monitoring:** http://localhost:6006

---

## Security Controls Mapped to NIST 800-53

| Control | Description | Implementation |
|---------|-------------|----------------|
| **AC-2** | Account Management | API key authentication, user_id tracking |
| **AU-2** | Audit Events | Phoenix logging all requests/responses |
| **AU-6** | Audit Review | Phoenix dashboard for real-time review |
| **SC-7** | Boundary Protection | Input/output validation guardrails |
| **SI-2** | Flaw Remediation | Automated guardrails prevent exploitation |
| **SI-10** | Information Input Validation | Guardrails AI validators |

---

## Recommendations for Production Deployment

### Immediate Actions:
1. **Enable HTTPS/TLS** - Encrypt all API traffic
2. **Implement Rate Limiting** - Prevent abuse (e.g., 100 req/hour)
3. **Add Authentication** - Move beyond API keys to OAuth2/JWT
4. **Set up Alerting** - Phoenix metrics → PagerDuty/Slack

### Medium-term Enhancements:
1. **Advanced Guardrails** - Add validators for:
   - Jailbreak attempts
   - Code injection
   - Bias detection
2. **Fine-grained Logging** - Store sanitized logs for compliance
3. **A/B Testing** - Test guardrail configurations
4. **Red Team Testing** - Conduct adversarial testing

### Long-term Strategy:
1. **Zero Trust Architecture** - Implement least-privilege access
2. **Continuous Monitoring** - Integrate with SIEM
3. **Incident Response Plan** - Define procedures for AI security incidents
4. **Compliance Certification** - Pursue FedRAMP/SOC2 if needed

---

## Conclusion

The LLM Guardrails Demo demonstrates a **defense-in-depth approach** to agentic AI security. Through layered controls—input validation, output sanitization, real-time monitoring, and comprehensive logging—the system successfully mitigates critical threats including prompt injection, toxic content generation, and PII leakage.

**Key Achievements:**
- ✅ 100% of requests validated by security guardrails
- ✅ Zero toxic content served to users
- ✅ Zero PII leaks in 14 traced requests
- ✅ Full observability via Phoenix dashboard

This system is **production-ready** with recommended enhancements and suitable for cloud deployment with appropriate infrastructure security controls (IAM, security groups, encryption, monitoring).

---

**References:**
- NIST SP 800-53 Rev 5
- OWASP Top 10 for LLM Applications
- Guardrails AI Documentation
- Phoenix Observability Platform