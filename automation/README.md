# Security Automation Script

Automated security scanning and reporting for the LLM Guardrails Demo API.

## Overview

This Python script automates multiple security checks and generates comprehensive reports for the LLM API application. It performs SAST scanning, dependency vulnerability checking, configuration validation, and security control verification.

**Author:** Shirin Bashar  
**Date:** December 9, 2024  
**Version:** 1.0

---

## Features

The automation script performs the following security checks:

### 1. **Bandit SAST Scan** 
- Static code analysis for Python security issues
- Generates JSON, TXT, and HTML reports
- Identifies high, medium, and low severity findings
- Reports on CWE vulnerabilities

### 2. **Dependency Vulnerability Check**
- Scans Python packages for known CVEs
- Uses pip-audit to check against vulnerability databases
- Generates JSON report of vulnerable dependencies

### 3. **API Configuration Validation**
- Verifies `.env` file exists and is in `.gitignore`
- Checks for Flask debug mode settings
- Validates secure configuration practices

### 4. **Security Controls Verification**
- Confirms Guardrails AI is enabled
- Verifies Phoenix observability integration
- Checks for input validation implementation
- Validates PII detection and toxic content filters

### 5. **Executive Summary Generation**
- Calculates overall security score (0-100)
- Determines security posture (GOOD/FAIR/NEEDS ATTENTION)
- Generates markdown and JSON reports
- Provides actionable recommendations

---

## Installation

### Prerequisites

```bash
# Install required packages
pip install bandit pip-audit

# Or use requirements.txt
pip install -r requirements.txt
```

### Setup

1. Create the automation directory:
```bash
mkdir automation
```

2. Save the script as `automation/security_scan.py`

3. Make it executable (Linux/Mac):
```bash
chmod +x automation/security_scan.py
```

---

## Usage

### Basic Scan

Run all security checks:

```bash
python automation/security_scan.py
```

### Verbose Mode

Get detailed output during scanning:

```bash
python automation/security_scan.py --verbose
```

### Export Only

Generate reports from existing scan data without re-scanning:

```bash
python automation/security_scan.py --export-only
```

### Help

View all available options:

```bash
python automation/security_scan.py --help
```

---

## Output

The script generates multiple report formats in the `security-reports/` directory:

### Generated Files

```
security-reports/
├── bandit_report.json       # Machine-readable SAST results
├── bandit_report.txt        # Human-readable SAST findings
├── bandit_report.html       # Interactive HTML report
├── pip_audit.json           # Dependency vulnerability data
├── security_summary.json    # Complete scan results (JSON)
└── security_summary.md      # Executive summary (Markdown)
```

### Report Contents

**security_summary.md** includes:
- Overall security posture assessment
- Security score (0-100)
- List of all checks performed
- Summary table of findings
- Recommendations for remediation
- Links to detailed reports

**security_summary.json** contains:
- Timestamp of scan
- All checks performed
- Detailed findings with severity levels
- Security score and posture
- Recommendations

---

## Example Output

```
======================================================================
🔒 SECURITY AUTOMATION SCRIPT
======================================================================
Project: LLM Guardrails Demo API
Scan started: 2024-12-09 08:15:30
======================================================================

[08:15:30] INFO: Running Bandit SAST scan...
[08:15:32] INFO: ✓ Bandit scan completed. Found 1 high, 2 medium, 0 low severity issues
[08:15:32] INFO: Checking dependencies for vulnerabilities...
[08:15:35] INFO: ✓ Dependency check completed. Found 0 vulnerabilities
[08:15:35] INFO: Validating API configuration...
[08:15:35] INFO: ✓ .env file found
[08:15:35] INFO: ✓ .env is in .gitignore
[08:15:35] WARNING: ⚠ Configuration check found 1 issues
[08:15:35] INFO: Checking security controls...
[08:15:35] INFO: ✓ Security controls check: 5/5 enabled
[08:15:35] INFO: Generating security summary report...
[08:15:35] INFO: ✓ Security summary saved to security-reports/security_summary.json

======================================================================
📊 SCAN COMPLETE
======================================================================
Security Posture: NEEDS ATTENTION
Security Score: 60/100
High Severity Issues: 1
Medium Severity Issues: 2

📁 Reports saved to: security-reports/
   - security_summary.md (human-readable)
   - security_summary.json (machine-readable)
   - bandit_report.html (interactive)
======================================================================
```

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install bandit pip-audit
      
      - name: Run security scan
        run: python automation/security_scan.py --verbose
      
      - name: Upload reports
        uses: actions/upload-artifact@v2
        with:
          name: security-reports
          path: security-reports/
      
      - name: Fail on high severity issues
        run: |
          if [ $(jq '.summary.high_severity_issues' security-reports/security_summary.json) -gt 0 ]; then
            echo "High severity issues found!"
            exit 1
          fi
```

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
echo "Running security scan..."
python automation/security_scan.py

if [ $? -ne 0 ]; then
    echo "Security scan failed! Fix high severity issues before committing."
    exit 1
fi
```

---

## Interpreting Results

### Security Score

- **90-100:** GOOD - Application follows security best practices
- **70-89:** FAIR - Some issues present, review before production
- **0-69:** NEEDS ATTENTION - Critical issues require immediate remediation

### Security Posture

- **GOOD:** Ready for production with standard security controls
- **FAIR:** Address medium severity issues before deployment
- **NEEDS ATTENTION:** High severity issues block production deployment

### Severity Levels

- **HIGH:** Critical security vulnerabilities requiring immediate fix
- **MEDIUM:** Security issues that should be addressed before production
- **LOW:** Minor issues or informational findings

---

## Customization

### Adding Custom Checks

Extend the `SecurityScanner` class with new methods:

```python
def check_custom_security(self):
    """Add your custom security check"""
    self.log("Running custom check...")
    
    # Your check logic here
    
    self.results["checks_performed"].append("Custom Security Check")
    self.results["findings"].append({
        "check": "Custom Check",
        "status": "COMPLETED",
        "details": {}
    })
    
    return True
```

Then add to `run_all_checks()`:
```python
self.check_custom_security()
```

### Configuring Thresholds

Modify the `generate_summary_report()` method to adjust scoring:

```python
# Example: Stricter scoring
if high_issues > 0:
    posture = "CRITICAL"
    score = 40
elif medium_issues > 1:  # More strict
    posture = "NEEDS ATTENTION"
    score = 60
```

---

## Troubleshooting

### Bandit Not Found

**Error:** `FileNotFoundError: bandit not installed`

**Solution:**
```bash
pip install bandit
```

### pip-audit Not Found

**Error:** `pip-audit not installed`

**Solution:**
```bash
pip install pip-audit
```

### Permission Denied

**Error:** `PermissionError: cannot write to security-reports/`

**Solution:**
```bash
mkdir security-reports
chmod 755 security-reports
```

### Import Errors

**Error:** `ModuleNotFoundError`

**Solution:**
```bash
# Make sure you're in the project root
cd arize-POC
python automation/security_scan.py
```

---

## Maintenance

### Regular Updates

- Run weekly scans to catch new vulnerabilities
- Update Bandit and pip-audit regularly:
  ```bash
  pip install --upgrade bandit pip-audit
  ```

### Baseline Management

Save initial scan results as baseline:
```bash
python automation/security_scan.py
cp security-reports/security_summary.json security-reports/baseline.json
```

Compare future scans against baseline to track improvements.

---

## NIST 800-53 Controls Addressed

This automation script supports the following security controls:

| Control | Description | Implementation |
|---------|-------------|----------------|
| **SA-11** | Developer Security Testing | Automated SAST scanning |
| **SI-2** | Flaw Remediation | Identifies vulnerabilities for patching |
| **RA-5** | Vulnerability Scanning | Dependency and code scanning |
| **CA-2** | Security Assessments | Regular automated assessments |
| **CA-7** | Continuous Monitoring | Supports continuous security testing |

---

## Best Practices

1. **Run Before Every Commit**
   - Catch issues early in development
   - Use pre-commit hooks

2. **Integrate with CI/CD**
   - Block deployments with high severity issues
   - Archive reports as artifacts

3. **Schedule Regular Scans**
   - Weekly full scans
   - Daily dependency checks

4. **Review All Findings**
   - Don't ignore warnings
   - Document accepted risks

5. **Track Trends**
   - Monitor security score over time
   - Set improvement goals

---

## Support & Contact

**Project:** LLM Guardrails Demo API  
**Author:** Shirin Bashar  
**Repository:** github.com/shirinbashar/arize-POC

For issues or questions:
1. Check the troubleshooting section
2. Review generated error logs
3. Contact the security team

---

## License

This automation script is part of the LLM Guardrails Demo project and follows the same licensing terms.

---

## Changelog

### Version 1.0 (2024-12-09)
- Initial release
- Bandit SAST integration
- Dependency vulnerability checking
- Configuration validation
- Security controls verification
- JSON and Markdown reporting

---

## Future Enhancements

Planned improvements:

- [ ] DAST (Dynamic Application Security Testing) integration
- [ ] Container security scanning
- [ ] Secret detection in code
- [ ] License compliance checking
- [ ] Performance benchmarking
- [ ] Automated remediation suggestions
- [ ] Integration with JIRA for issue tracking
- [ ] Slack/email notifications
- [ ] Historical trend analysis
- [ ] Custom rule configurations