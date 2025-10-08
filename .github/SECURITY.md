# Security Policy

## Reporting Security Vulnerabilities

I take security seriously and appreciate your help in responsibly disclosing vulnerabilities.

### How to Report

**DO NOT** create public GitHub issues for security vulnerabilities.

Instead, please report security issues privately by:

1. **GitHub Private Report**: Use GitHub's private vulnerability reporting feature

### What to Include

When reporting a vulnerability, please provide:

- **Description**: Clear description of the vulnerability
- **Impact**: Potential impact and attack scenarios
- **Reproduction**: Steps to reproduce the issue
- **Affected Versions**: Which versions are affected
- **Environment**: OS, Python version, dependencies used
- **Proof of Concept**: If possible, without exploiting in production

### Response Process

1. **Acknowledgment**: I will acknowledge your report within 48 hours
2. **Investigation**: I'll investigate the issue
3. **Fix Development**: If confirmed, I'll develop a fix
4. **Disclosure**: I'll coordinate disclosure timing with you
5. **Release**: Security patches will be released promptly

### Security Measures

This project implements several security measures:

- **Input Validation**: All user inputs are validated and sanitized
- **File Size Limits**: Maximum file sizes prevent memory exhaustion
- **Path Traversal Protection**: Prevents directory traversal attacks
- **Rate Limiting**: API endpoints have rate limiting to prevent abuse
- **Error Handling**: Comprehensive error handling prevents information leakage
- **Dependency Scanning**: Regular security scans of dependencies

### Scope

This security policy covers:
- The main application code in the `app/` directory
- CLI tools (`cli_crack.py`, `cli_unlock.py`)
- API endpoints and middleware
- Test files and scripts

It does NOT cover:
- User-generated content or data
- Third-party dependencies (report to upstream projects)
- Operating system or infrastructure issues

### Responsible Disclosure

I follow responsible disclosure practices:

- I will not take legal action against researchers who report vulnerabilities in good faith
- I'll credit researchers who help improve security (with permission)
- I'll provide clear timelines for fixes and disclosures
- I'll coordinate disclosure timing to minimize risk to users

### Contact

For security-related questions or reports:
- **GitHub**: Use private vulnerability reporting
- **Response Time**: Within 48 hours for initial acknowledgment

Thank you for helping keep users safe!
