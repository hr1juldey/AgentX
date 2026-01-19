# AGENTX Threat Model

**Version**: 1.0.0
**Date**: 2026-01-19
**Status**: Draft
**Part of**: AGENTX HLD v1.0

---

## Executive Summary

This document provides a comprehensive threat model for AGENTX, identifying potential security threats, their impact, mitigation strategies, detection methods, and recovery procedures.

**Threat Model Methodology**: STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege)

---

## Table of Contents

1. [Threat Matrix](#1-threat-matrix)
2. [Asset Inventory](#2-asset-inventory)
3. [Threat Analysis](#3-threat-analysis)
4. [Mitigation Strategies](#4-mitigation-strategies)
5. [Detection & Monitoring](#5-detection--monitoring)
6. [Incident Response](#6-incident-response)

---

## 1. Threat Matrix

### Overview

| Threat Category | Impact | Likelihood | Risk Level | Mitigation Priority |
|-----------------|--------|------------|------------|---------------------|
| **Data Exfiltration** | Critical | Low | **High** | P1 |
| **Plugin Compromise** | High | Medium | **High** | P1 |
| **PII Leakage** | Critical | Low | **High** | P1 |
| **Lateral Movement** | High | Low | **Medium** | P2 |
| **Supply-Chain Attack** | High | Low | **Medium** | P2 |
| **LLM Jailbreak** | Medium | Medium | **Medium** | P2 |
| **DoS Attack** | Medium | Low | **Low** | P3 |
| **Unauthorized Access** | High | Low | **Medium** | P2 |

### Risk Assessment

**Risk Level Calculation**: Impact × Likelihood

- **High (P1)**: Critical + Medium, or High + High
- **Medium (P2)**: High + Low, or Medium + Medium
- **Low (P3)**: Medium + Low, or Low + Any

---

## 2. Asset Inventory

### Critical Assets

| Asset | Type | Value | Sensitivity |
|-------|------|-------|------------|
| **User Memory** | Data | High | PII, preferences, history |
| **Conversation History** | Data | High | Personal information |
| **Plugin API Keys** | Secret | Medium | Authentication |
| **LLM Responses** | Data | Medium | Generated content |
| **System Configuration** | Config | Low | Settings, preferences |

### System Boundaries

| Boundary | Trust Level | Controls |
|----------|-------------|----------|
| **User → PWA** | Low | HTTPS, JWT auth |
| **PWA → Core** | Medium | mTLS, rate limiting |
| **Core → Qdrant** | High | mTLS, network isolation |
| **Core → Plugins** | Low | Resource quotas, sandboxing |
| **Core → Ollama** | High | mTLS, network isolation |

---

## 3. Threat Analysis

### T1: Data Exfiltration

**Description**: Unauthorized transfer of data from AGENTX to external systems.

**Attack Vectors**:
1. Plugin with network access sends data externally
2. Compromised plugin exfiltrates via covert channels
3. Malicious user exports another user's data
4. Backup files accessed by unauthorized parties

**Impact**:
- Privacy violation
- Legal liability (GDPR/CCPA)
- Reputation damage
- User trust loss

**Affected Assets**: User Memory, Conversation History

**Likelihood**: Low (local-only, no external network by default)

### T2: Plugin Compromise

**Description**: Malicious or compromised plugin executes unauthorized actions.

**Attack Vectors**:
1. Plugin from untrusted source contains backdoor
2. Supply-chain attack in plugin dependencies
3. Plugin vulnerability exploited
4. Signature verification bypass

**Impact**:
- Unauthorized data access
- System instability
- Resource abuse
- Lateral movement to other components

**Affected Assets**: Plugin API Keys, System Configuration

**Likelihood**: Medium (plugin system allows third-party code)

### T3: PII Leakage

**Description**: PII exposed in logs, error messages, or debug output.

**Attack Vectors**:
1. PII not redacted before logging
2. Stack traces containing sensitive data
3. Debug mode enabled in production
4. Plugin accesses PII without permission

**Impact**:
- Privacy violation
- Compliance violations (GDPR/CCPA)
- Legal liability

**Affected Assets**: User Memory, Conversation History, Logs

**Likelihood**: Low (PII detection at all entry points)

### T4: Lateral Movement

**Description**: Attacker moves from compromised component to other systems.

**Attack Vectors**:
1. Plugin escape via vulnerability
2. Shared resources exploited
3. IPC channels abused
4. Authentication bypass

**Impact**:
- Multi-component compromise
- Data breach expansion
- System-wide takeover

**Affected Assets**: All system components

**Likelihood**: Low (strong isolation between components)

### T5: Supply-Chain Attack

**Description**: Malicious code introduced via dependency update.

**Attack Vectors**:
1. Compromised PyPI package
2. Malicious Docker image
3. Backdoored dependency
4. Typo-squatting attack

**Impact**:
- System compromise
- Data exfiltration
- Supply-chain contamination

**Affected Assets**: All system components

**Likelihood**: Low (pinned dependencies, signature verification)

### T6: LLM Jailbreak

**Description**: Adversarial prompts cause LLM to ignore safety constraints.

**Attack Vectors**:
1. Prompt injection via user input
2. Jailbreak prompts from plugins
3. Context manipulation
4. Adversarial examples

**Impact**:
- Unauthorized actions
- Information disclosure
- System misuse

**Affected Assets**: LLM Responses

**Likelihood**: Medium (LLMs inherently vulnerable to jailbreaks)

### T7: Denial of Service

**Description**: System resources exhausted, preventing legitimate use.

**Attack Vectors**:
1. Resource exhaustion (CPU, RAM)
2. API flooding
3. Large input processing
4. Plugin abuse

**Impact**:
- Service unavailability
- Poor user experience
- Data processing delays

**Affected Assets**: All system components

**Likelihood**: Low (local deployment, single user)

### T8: Unauthorized Access

**Description**: Attacker gains access to system without authentication.

**Attack Vectors**:
1. Weak password brute-forcing
2. JWT token theft
3. Session hijacking
4. Authentication bypass

**Impact**:
- Data breach
- Privacy violation
- System misuse

**Affected Assets**: User Memory, Conversation History, Configuration

**Likelihood**: Low (strong authentication, local-only access)

---

## 4. Mitigation Strategies

### Defense in Depth

| Layer | Controls |
|-------|----------|
| **Perimeter** | Local-only, no external network, air-gapped capable |
| **Network** | mTLS, network isolation, VLAN separation |
| **Process** | Plugin sandboxing, resource quotas, process isolation |
| **Data** | Encryption at rest, PII redaction, per-user isolation |
| **Access** | RBAC, JWT auth, permission checks |
| **Audit** | Immutable logs, tamper-evident, regular review |

### Threat-Specific Mitigations

#### T1: Data Exfiltration

| Mitigation | Implementation |
|------------|----------------|
| **Network isolation** | No external network access (local-only) |
| **Plugin permissions** | Explicit data scope, RBAC enforcement |
| **Egress monitoring** | Audit all plugin operations |
| **Opt-in telemetry** | Disabled by default, user consent required |

#### T2: Plugin Compromise

| Mitigation | Implementation |
|------------|----------------|
| **Code signing** | GPG signature verification, trusted CAs only |
| **Sandboxing** | Resource quotas, process isolation, no network |
| **Health checks** | Periodic health monitoring, crash detection |
| **Review process** | Manual security review before installation |

#### T3: PII Leakage

| Mitigation | Implementation |
|------------|----------------|
| **PII detection** | Scan at ingest, pre-plugin, pre-model, pre-output |
| **Redaction** | Automatic redaction of detected PII patterns |
| **Logging policy** | No PII in logs, hash user IDs only |
| **Audit** | Regular log scans for PII patterns |

#### T4: Lateral Movement

| Mitigation | Implementation |
|------------|----------------|
| **Per-user isolation** | SHA-256 user ID hashing, no cross-user access |
| **RBAC** | Permission checks at all boundaries |
| **IPC security** | mTLS for inter-service communication |
| **Resource quotas** | Limit plugin CPU/RAM, prevent abuse |

#### T5: Supply-Chain Attack

| Mitigation | Implementation |
|------------|----------------|
| **Pinned dependencies** | Pin versions in requirements.txt |
| **Signature verification** | Verify all plugin signatures |
| **Integrity checks** | Hash verification on startup |
| **Update policy** | Manual review before dependency updates |

#### T6: LLM Jailbreak

| Mitigation | Implementation |
|------------|----------------|
| **Input validation** | Validate all user inputs, reject suspicious patterns |
| **Output filtering** | Scan responses for policy violations |
| **Confidence thresholds** | Reject low-confidence responses |
| **Jailbreak detection** | Pattern matching for known jailbreaks |

#### T7: Denial of Service

| Mitigation | Implementation |
|------------|----------------|
| **Resource quotas** | Per-user and per-plugin limits |
| **Rate limiting** | 100 req/min per user, 10 concurrent connections |
| **Timeouts** | 30s default, 60s for long-running operations |
| **Monitoring** | Alert on unusual resource usage |

#### T8: Unauthorized Access

| Mitigation | Implementation |
|------------|----------------|
| **Strong authentication** | Argon2 password hashing, JWT tokens |
| **Secure session** | 24-hour expiration, refresh tokens |
| **HTTPS only** | TLS 1.3, certificate validation |
| **Brute-force protection** | Account lockout after 5 failed attempts |

---

## 5. Detection & Monitoring

### Monitoring Dashboard

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| **Failed auth attempts** | Login failures per user | >5 in 5min |
| **Plugin crashes** | Plugin process exits | >3 in 1hour |
| **PII in logs** | PII patterns detected | Any occurrence |
| **Resource usage** | CPU/RAM per component | >90% for 5min |
| **Egress attempts** | External network attempts | Any occurrence |
| **Jailbreak patterns** | Known jailbreak prompts | Any occurrence |

### Audit Log Review

**Review Cadence**: Daily automated, weekly manual

**Key Events to Review**:
- Failed authentication attempts
- Plugin installations/activations
- Data export requests
- Failed PII redactions
- Resource quota violations
- Unusual error patterns

### Automated Detection

```python
# PII Detection Example
PII_PATTERNS = {
    "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "api_key": r"\b[A-Za-z0-9]{20,}\b",
}

def scan_for_pii(log_entry: str) -> list[str]:
    """Scan log entry for PII patterns."""
    detected = []
    for pii_type, pattern in PII_PATTERNS.items():
        if re.search(pattern, log_entry):
            detected.append(pii_type)
    return detected

# Jailbreak Detection Example
JAILBREAK_PATTERNS = [
    r"ignore (previous|above) instructions",
    r"forget (everything|all constraints)",
    r"pretend you are (not|unconstrained)",
    r"override (safety|security) (protocol|measures)",
]

def detect_jailbreak(prompt: str) -> bool:
    """Detect jailbreak attempt in prompt."""
    for pattern in JAILBREAK_PATTERNS:
        if re.search(pattern, prompt, re.IGNORECASE):
            return True
    return False
```

---

## 6. Incident Response

### Incident Categories

| Category | Examples | Response Time |
|----------|----------|---------------|
| **Critical** | Data breach, PII leak, system compromise | Immediate (15min) |
| **High** | Plugin crash, DoS, unauthorized access | Urgent (1hour) |
| **Medium** | Resource quota, performance degradation | Normal (4hours) |
| **Low** | Documentation, minor bugs | Scheduled (1week) |

### Response Procedures

#### Critical Incident (Data Breach/PII Leak)

1. **Immediate (0-15min)**:
   - Stop all services: `docker-compose down`
   - Preserve evidence: Copy logs, memory dumps
   - Notify stakeholders: Security lead, legal, management

2. **Investigation (15min-1hour)**:
   - Analyze logs for breach scope
   - Identify affected users/data
   - Determine root cause

3. **Containment (1-4hours)**:
   - Isolate affected systems
   - Revoke compromised credentials
   - Patch vulnerabilities

4. **Recovery (4-24hours)**:
   - Restore from clean backup
   - Verify system integrity
   - Resume operations

5. **Post-Incident**:
   - Document lessons learned
   - Update threat model
   - Implement additional controls

#### High Incident (Plugin Crash/DoS)

1. **Immediate (0-5min)**:
   - Isolate affected plugin
   - Check system health
   - Log incident

2. **Investigation (5min-1hour)**:
   - Analyze crash logs
   - Identify root cause
   - Assess impact

3. **Resolution (1-4hours)**:
   - Fix or remove problematic plugin
   - Restore service
   - Verify stability

### Recovery Time Objectives (RTO/RPO)

| Incident Type | RTO | RPO |
|--------------|-----|-----|
| **Data breach** | 15min | 5min |
| **PII leak** | 15min | 0 (prevent further) |
| **Plugin crash** | 1hour | Data preserved |
| **DoS** | 4hours | No data loss |
| **Full system** | 24hours | Manual reentry |

---

## Appendix: Security Checklist

### Pre-Deployment

- [ ] All dependencies pinned to specific versions
- [ ] All plugins signed and verified
- [ ] PII detection tested with sample data
- [ ] Authentication flows tested
- [ ] Encryption at rest verified
- [ ] Audit logging enabled and tested
- [ ] Rate limiting configured
- [ ] Resource quotas enforced
- [ ] Network isolation verified
- [ ] Incident response procedures documented

### Post-Deployment

- [ ] Daily automated log review
- [ ] Weekly security log review
- [ ] Monthly penetration testing
- [ ] Quarterly threat model update
- [ ] Annual security audit

---

**This threat model is part of AGENTX HLD v1.0. See [HLD.md](HLD.md) for complete architecture.**
