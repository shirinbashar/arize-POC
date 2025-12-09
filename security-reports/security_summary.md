# Security Scan Summary Report

**Scan Date:** 2025-12-09 23:10:44
**Project:** LLM Guardrails Demo API

## Overall Security Posture

**Status:** NEEDS ATTENTION  
**Security Score:** 60/100

## Checks Performed

- ✓ Bandit SAST Scan
- ✓ API Configuration Validation
- ✓ Security Controls Verification

## Findings Summary

| Check | Status | Issues Found |
|-------|--------|-------------|
| Bandit SAST | COMPLETED | 1 High, 2 Medium |
| API Configuration | COMPLETED | 1 issues |
| Security Controls | COMPLETED | N/A |

## Recommendation

High severity issues detected. Address critical findings immediately before deployment.

## Detailed Reports

Full reports available in `security-reports/` directory:
- `bandit_report.html` - Interactive SAST findings
- `bandit_report.json` - Machine-readable SAST results
- `security_summary.json` - Complete scan results
