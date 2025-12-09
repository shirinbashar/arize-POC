#!/usr/bin/env python3
"""
Security Automation Script
Automates security checks for the LLM Guardrails Demo API

Author: Shirin Bashar
Date: December 9, 2024

This script performs the following automated security checks:
1. Bandit SAST scan with JSON and HTML reports
2. Dependency vulnerability check
3. API configuration validation
4. Security summary report generation

Usage:
    python automation/security_scan.py
    python automation/security_scan.py --verbose
    python automation/security_scan.py --export-only
"""

import os
import sys
import json
import subprocess
import argparse
from datetime import datetime
from pathlib import Path


class SecurityScanner:
    """Automated security scanner for Python applications"""

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.results = {
            "scan_timestamp": datetime.now().isoformat(),
            "checks_performed": [],
            "findings": [],
            "summary": {}
        }
        self.project_root = Path(__file__).parent.parent
        self.reports_dir = self.project_root / "security-reports"
        self.reports_dir.mkdir(exist_ok=True)

    def log(self, message, level="INFO"):
        """Print log message if verbose mode enabled"""
        if self.verbose or level == "ERROR":
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {level}: {message}")

    def run_bandit_scan(self):
        """Run Bandit SAST scan on source code"""
        self.log("Running Bandit SAST scan...")

        try:
            # Run Bandit with JSON output
            json_report = self.reports_dir / "bandit_report.json"
            txt_report = self.reports_dir / "bandit_report.txt"
            html_report = self.reports_dir / "bandit_report.html"

            # JSON report
            result_json = subprocess.run(
                ["bandit", "-r", "src/", "-f", "json", "-o", str(json_report)],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            # Text report
            result_txt = subprocess.run(
                ["bandit", "-r", "src/", "-f", "txt", "-o", str(txt_report)],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            # HTML report
            result_html = subprocess.run(
                ["bandit", "-r", "src/", "-f", "html", "-o", str(html_report)],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            # Parse JSON results
            if json_report.exists():
                with open(json_report, 'r') as f:
                    bandit_data = json.load(f)

                metrics = bandit_data.get("metrics", {}).get("_totals", {})

                self.results["checks_performed"].append("Bandit SAST Scan")
                self.results["findings"].append({
                    "check": "Bandit SAST",
                    "status": "COMPLETED",
                    "high_severity": metrics.get("SEVERITY.HIGH", 0),
                    "medium_severity": metrics.get("SEVERITY.MEDIUM", 0),
                    "low_severity": metrics.get("SEVERITY.LOW", 0),
                    "total_issues": metrics.get("SEVERITY.HIGH", 0) +
                                    metrics.get("SEVERITY.MEDIUM", 0) +
                                    metrics.get("SEVERITY.LOW", 0),
                    "report_path": str(json_report)
                })

                self.log(f"✓ Bandit scan completed. Found {metrics.get('SEVERITY.HIGH', 0)} high, "
                         f"{metrics.get('SEVERITY.MEDIUM', 0)} medium, "
                         f"{metrics.get('SEVERITY.LOW', 0)} low severity issues")

                return True
            else:
                self.log("Bandit report not generated", "ERROR")
                return False

        except FileNotFoundError:
            self.log("Bandit not installed. Run: pip install bandit", "ERROR")
            return False
        except Exception as e:
            self.log(f"Bandit scan failed: {str(e)}", "ERROR")
            return False

    def check_dependencies(self):
        """Check for known vulnerabilities in dependencies"""
        self.log("Checking dependencies for vulnerabilities...")

        try:
            # Try using pip-audit if available
            result = subprocess.run(
                ["pip-audit", "--format", "json", "--output",
                 str(self.reports_dir / "pip_audit.json")],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                audit_file = self.reports_dir / "pip_audit.json"
                if audit_file.exists():
                    with open(audit_file, 'r') as f:
                        audit_data = json.load(f)

                    vuln_count = len(audit_data.get("vulnerabilities", []))

                    self.results["checks_performed"].append("Dependency Vulnerability Check")
                    self.results["findings"].append({
                        "check": "Dependency Vulnerabilities",
                        "status": "COMPLETED",
                        "vulnerabilities_found": vuln_count,
                        "report_path": str(audit_file)
                    })

                    self.log(f"✓ Dependency check completed. Found {vuln_count} vulnerabilities")
                    return True
            else:
                self.log("pip-audit not available, skipping dependency check", "WARNING")

        except FileNotFoundError:
            self.log("pip-audit not installed. Install with: pip install pip-audit", "WARNING")
        except Exception as e:
            self.log(f"Dependency check failed: {str(e)}", "WARNING")

        return False

    def validate_api_configuration(self):
        """Validate Flask API security configuration"""
        self.log("Validating API configuration...")

        issues = []

        # Check if .env file exists
        env_file = self.project_root / ".env"
        if not env_file.exists():
            issues.append("Missing .env file - API keys may be exposed")
        else:
            self.log("✓ .env file found")

        # Check if .gitignore includes .env
        gitignore = self.project_root / ".gitignore"
        if gitignore.exists():
            with open(gitignore, 'r', encoding='utf-8') as f:
                gitignore_content = f.read()
                if ".env" not in gitignore_content:
                    issues.append(".env not in .gitignore - credentials at risk")
                else:
                    self.log("✓ .env is in .gitignore")
        else:
            issues.append("Missing .gitignore file")

        # Check for debug mode in app.py
        app_file = self.project_root / "src" / "app.py"
        if app_file.exists():
            with open(app_file, 'r', encoding='utf-8') as f:
                app_content = f.read()
                if "debug=True" in app_content:
                    issues.append("Flask debug mode enabled - unsafe for production")
                else:
                    self.log("✓ Flask debug mode not hardcoded")

        self.results["checks_performed"].append("API Configuration Validation")
        self.results["findings"].append({
            "check": "API Configuration",
            "status": "COMPLETED",
            "issues_found": len(issues),
            "issues": issues
        })

        if issues:
            self.log(f"⚠ Configuration check found {len(issues)} issues", "WARNING")
        else:
            self.log("✓ Configuration validation passed")

        return True

    def check_security_controls(self):
        """Verify security controls are in place"""
        self.log("Checking security controls...")

        controls = {
            "Guardrails AI": False,
            "Phoenix Observability": False,
            "Input Validation": False,
            "PII Detection": False,
            "Toxic Content Filter": False
        }

        app_file = self.project_root / "src" / "app.py"
        if app_file.exists():
            with open(app_file, 'r', encoding='utf-8') as f:
                content = f.read()

                if "from guardrails import Guard" in content:
                    controls["Guardrails AI"] = True
                if "import phoenix" in content or "from phoenix" in content:
                    controls["Phoenix Observability"] = True
                if "guard.validate" in content:
                    controls["Input Validation"] = True
                if "DetectPII" in content:
                    controls["PII Detection"] = True
                if "ToxicLanguage" in content:
                    controls["Toxic Content Filter"] = True

        enabled_controls = sum(controls.values())
        total_controls = len(controls)

        self.results["checks_performed"].append("Security Controls Verification")
        self.results["findings"].append({
            "check": "Security Controls",
            "status": "COMPLETED",
            "controls_enabled": enabled_controls,
            "total_controls": total_controls,
            "details": controls
        })

        self.log(f"✓ Security controls check: {enabled_controls}/{total_controls} enabled")
        return True

    def generate_summary_report(self):
        """Generate executive summary report"""
        self.log("Generating security summary report...")

        # Calculate overall security score
        total_checks = len(self.results["checks_performed"])

        # Count high severity issues from Bandit
        high_issues = 0
        medium_issues = 0
        for finding in self.results["findings"]:
            if finding["check"] == "Bandit SAST":
                high_issues = finding.get("high_severity", 0)
                medium_issues = finding.get("medium_severity", 0)

        # Determine security posture
        if high_issues > 0:
            posture = "NEEDS ATTENTION"
            score = 60
        elif medium_issues > 2:
            posture = "FAIR"
            score = 75
        else:
            posture = "GOOD"
            score = 90

        self.results["summary"] = {
            "security_posture": posture,
            "security_score": score,
            "total_checks": total_checks,
            "high_severity_issues": high_issues,
            "medium_severity_issues": medium_issues,
            "recommendation": self._get_recommendation(posture)
        }

        # Write summary to file
        summary_file = self.reports_dir / "security_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)

        # Generate markdown report
        self._generate_markdown_report()

        self.log(f"✓ Security summary saved to {summary_file}")
        return True

    def _get_recommendation(self, posture):
        """Get recommendation based on security posture"""
        recommendations = {
            "GOOD": "Security posture is acceptable. Continue monitoring and maintain current controls.",
            "FAIR": "Some security issues detected. Review and address medium severity findings before production.",
            "NEEDS ATTENTION": "High severity issues detected. Address critical findings immediately before deployment."
        }
        return recommendations.get(posture, "Review findings and implement recommended fixes.")

    def _generate_markdown_report(self):
        """Generate human-readable markdown report"""
        md_file = self.reports_dir / "security_summary.md"

        with open(md_file, 'w', encoding='utf-8') as f:
            f.write("# Security Scan Summary Report\n\n")
            f.write(f"**Scan Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Project:** LLM Guardrails Demo API\n\n")

            f.write("## Overall Security Posture\n\n")
            posture = self.results["summary"]["security_posture"]
            score = self.results["summary"]["security_score"]
            f.write(f"**Status:** {posture}  \n")
            f.write(f"**Security Score:** {score}/100\n\n")

            f.write("## Checks Performed\n\n")
            for check in self.results["checks_performed"]:
                f.write(f"- ✓ {check}\n")
            f.write("\n")

            f.write("## Findings Summary\n\n")
            f.write("| Check | Status | Issues Found |\n")
            f.write("|-------|--------|-------------|\n")

            for finding in self.results["findings"]:
                check_name = finding["check"]
                status = finding["status"]

                if "high_severity" in finding:
                    issues = f"{finding['high_severity']} High, {finding['medium_severity']} Medium"
                elif "vulnerabilities_found" in finding:
                    issues = f"{finding['vulnerabilities_found']} vulnerabilities"
                elif "issues_found" in finding:
                    issues = f"{finding['issues_found']} issues"
                else:
                    issues = "N/A"

                f.write(f"| {check_name} | {status} | {issues} |\n")

            f.write("\n## Recommendation\n\n")
            f.write(self.results["summary"]["recommendation"])
            f.write("\n\n## Detailed Reports\n\n")
            f.write("Full reports available in `security-reports/` directory:\n")
            f.write("- `bandit_report.html` - Interactive SAST findings\n")
            f.write("- `bandit_report.json` - Machine-readable SAST results\n")
            f.write("- `security_summary.json` - Complete scan results\n")

        self.log(f"✓ Markdown report saved to {md_file}")

    def run_all_checks(self):
        """Run all security checks"""
        print("=" * 70)
        print("🔒 SECURITY AUTOMATION SCRIPT")
        print("=" * 70)
        print(f"Project: LLM Guardrails Demo API")
        print(f"Scan started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        print()

        # Run all checks
        self.run_bandit_scan()
        self.check_dependencies()
        self.validate_api_configuration()
        self.check_security_controls()
        self.generate_summary_report()

        # Print summary
        print()
        print("=" * 70)
        print("📊 SCAN COMPLETE")
        print("=" * 70)
        summary = self.results["summary"]
        print(f"Security Posture: {summary['security_posture']}")
        print(f"Security Score: {summary['security_score']}/100")
        print(f"High Severity Issues: {summary['high_severity_issues']}")
        print(f"Medium Severity Issues: {summary['medium_severity_issues']}")
        print()
        print(f"📁 Reports saved to: {self.reports_dir}")
        print(f"   - security_summary.md (human-readable)")
        print(f"   - security_summary.json (machine-readable)")
        print(f"   - bandit_report.html (interactive)")
        print("=" * 70)

        return self.results


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Automated security scanning for LLM API")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose output")
    parser.add_argument("--export-only", action="store_true",
                        help="Only generate reports from existing scan data")

    args = parser.parse_args()

    scanner = SecurityScanner(verbose=args.verbose)

    if args.export_only:
        scanner.generate_summary_report()
    else:
        results = scanner.run_all_checks()

        # Exit with error code if high severity issues found
        if results["summary"]["high_severity_issues"] > 0:
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()