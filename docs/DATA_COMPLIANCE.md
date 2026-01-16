# Data Handling & Compliance

This document outlines how Code AI handles sensitive data, complies with regulations, and manages security and privacy.

## Data Classification

### Public Data
- API documentation
- Product roadmap
- Publicly shared examples

### Confidential Data
- User code (prompts, completions)
- API keys
- Billing information
- Usage statistics

### Sensitive Data
- Account credentials
- Personally identifiable information (PII)
- Financial data

## Compliance Frameworks

### GDPR (General Data Protection Regulation)
- **Scope:** Users in the EU and UK
- **Key obligations:**
  - Legal basis for data processing (consent, contract, legitimate interest)
  - Data Protection Impact Assessments (DPIA) for high-risk processing
  - User rights: access, deletion, portability, objection
  - 72-hour breach notification
  - Data Protection Officer: dpo@codeai.example.com

### CCPA (California Consumer Privacy Act)
- **Scope:** California residents
- **Key rights:** Access, deletion, opt-out, non-discrimination
- **Implementation:** Privacy Policy, opt-out mechanisms

### SOC 2 Type II
- **Scope:** Security, availability, processing integrity, confidentiality
- **Requirements:** Annual audit, monitoring, incident response
- **Status:** Planned for 2026 Q2

## Data Security

### Encryption
- **In Transit:** TLS 1.3 for all communication
- **At Rest:** AES-256 encryption for sensitive data
- **Key Management:** Managed by cloud provider (e.g., AWS KMS)

### Access Control
- Role-based access control (RBAC)
- Multi-factor authentication (MFA) for staff
- API key rotation every 90 days (recommended)
- Audit logs for all admin access

### Network Security
- Private subnets for backend services
- VPC/firewall rules
- Web Application Firewall (WAF) rules for common attacks
- Regular penetration testing

### Incident Response
- Security team on-call 24/7
- Incident classification and escalation
- Root cause analysis within 48 hours
- User notification within 72 hours of confirmed breach

## Third-Party Processors

We use the following vendors; all have Data Processing Agreements:

| Vendor | Purpose | Jurisdiction |
|--------|---------|---------------|
| AWS | Cloud hosting, storage | US |
| Stripe | Payment processing | US |
| DataDog | Monitoring/logging | US |

## Data Retention Schedule

| Data Type | Retention | Reason |
|-----------|-----------|--------|
| User prompts/completions | 30 days | Debugging, billing |
| API usage logs | 12 months | Analytics, audits |
| Error logs | 7 days | Troubleshooting |
| Billing records | 7 years | Tax/legal compliance |
| Account data | Until deletion | Active account management |

## Deletion & Export

### Right to Deletion
- Users can delete all personal data via dashboard
- Hard deletion within 30 days
- Backup copies deleted within 90 days

### Right to Data Portability
- Export account data as JSON
- Available from dashboard

## Audit & Compliance

- **Annual SOC 2 audit:** Security posture assessment
- **Quarterly risk assessment:** Identify new threats
- **Monthly access reviews:** Verify proper authorization
- **Vulnerability scans:** Weekly automated scans + monthly manual assessment

## Contact

- **Data Protection Officer (DPO):** dpo@codeai.example.com
- **Privacy Requests:** privacy@codeai.example.com
- **Security Incidents:** security@codeai.example.com (PGP key available on website)
