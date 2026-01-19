# AGENTX Privacy Impact Assessment

**Version**: 1.0.0
**Date**: 2026-01-19
**Status**: Draft
**Part of**: AGENTX HLD v1.0

---

## Executive Summary

This document provides a comprehensive privacy impact assessment (PIA) for AGENTX, analyzing PII handling, GDPR/CCPA compliance, data residency, and privacy controls.

**Assessment Scope**: AGENTX v1.0 - Local-first AI personal assistant with temporal memory, voice interface, and extensible plugins.

**Privacy Posture**: **MINIMAL RISK** - Local-only processing, no cloud data transmission, user-controlled data retention, full GDPR/CCPA compliance.

---

## Table of Contents

1. [PII Detection & Classification](#1-pii-detection--classification)
2. [Redaction Strategy](#2-redaction-strategy)
3. [GDPR Compliance Analysis](#3-gdpr-compliance-analysis)
4. [CCPA Compliance Analysis](#4-ccpa-compliance-analysis)
5. [Data Residency Proofs](#5-data-residency-proofs)
6. [Retention & Erasure Workflows](#6-retention--erasure-workflows)
7. [Privacy Controls](#7-privacy-controls)
8. [Risk Assessment](#8-risk-assessment)

---

## 1. PII Detection & Classification

### PII Detection Points

| Detection Point | Location | PII Types | Action | Latency Impact |
|-----------------|----------|-----------|--------|----------------|
| **Ingest** | Ingest Service | All PII types | Scan and redact | <10ms |
| **Pre-Plugin** | Plugin Boundary | All PII types | Redact before transmission | <5ms |
| **Pre-Model** | LLM Boundary | All PII types | Redact before inference | <5ms |
| **Pre-Output** | Response Formatter | All PII types | Redact in responses | <5ms |
| **Logging** | Audit Service | All PII types | Block PII from logs | <1ms |

### PII Classification

| PII Type | Pattern | Sensitivity | Retention | Redaction Required |
|----------|---------|-------------|-----------|-------------------|
| **Credit Card** | `\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b` | Critical | Session | ✅ Yes |
| **SSN** | `\b\d{3}-\d{2}-\d{4}\b` | Critical | 90 days | ✅ Yes |
| **Email** | `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b` | High | 90 days | ✅ Yes |
| **Phone** | `\b\d{3}[-.]?\d{3}[-.]?\d{4}\b` | High | 90 days | ✅ Yes |
| **API Key** | `\b[A-Za-z0-9]{20,}\b` | Critical | Session | ✅ Yes |
| **IP Address** | `\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b` | Medium | 30 days | ✅ Yes |
| **Address** | Multi-line pattern | High | 90 days | ✅ Yes |
| **Name** | Context-based | Low | 365 days | ⚠️ Optional |

### Contextual PII Detection

```python
# Names require context-aware detection
NAME_PATTERNS = {
    "my_name_is": r"(?i)my name is (\w+)",
    "i_am": r"(?i)i am (\w+)",
    "call_me": r"(?i)call me (\w+)",
    "this_is": r"(?i)this is (\w+)",
}

# Only redact if user opts in (default: off)
```

---

## 2. Redaction Strategy

### Redaction Rules

| Rule | Implementation | Override |
|------|----------------|----------|
| **Credit Card** | Always redact, replace with `[REDACTED:CC]` | No override |
| **SSN** | Always redact, replace with `[REDACTED:SSN]` | No override |
| **API Key** | Always redact, replace with `[REDACTED:KEY]` | No override |
| **Email** | Default redact, user opt-out available | User preference |
| **Phone** | Default redact, user opt-out available | User preference |
| **Name** | Opt-in redaction only | User preference |

### Redaction Markers

```python
class RedactionMarker(BaseModel):
    """PII redaction marker for audit trail."""

    type: str = Field(
        ...,
        description="Type of PII (credit_card, ssn, email, phone, api_key, custom)"
    )
    start_index: int = Field(..., ge=0, description="Start index in text")
    end_index: int = Field(..., gt=lambda self: self.start_index, description="End index in text")
    replacement: str = Field(default="[REDACTED]", description="Replacement text")
    reason: str = Field(..., description="Reason for redaction (policy, user_request, legal)")
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    detection_method: str = Field(default="regex", description="regex, ml, manual")
```

### Redaction Pipeline

```python
# Multi-stage redaction with validation
def redact_pii(text: str, user_preferences: UserPrivacyPrefs) -> tuple[str, list[RedactionMarker]]:
    """Redact PII from text based on user preferences."""
    markers = []

    # Stage 1: Pattern-based detection (always required)
    for pii_type, pattern in MANDATORY_PATTERNS.items():
        for match in re.finditer(pattern, text):
            markers.append(RedactionMarker(
                type=pii_type,
                start_index=match.start(),
                end_index=match.end(),
                reason="policy"
            ))

    # Stage 2: Optional PII (user opt-in)
    if user_preferences.redact_email:
        for match in re.finditer(EMAIL_PATTERN, text):
            markers.append(RedactionMarker(
                type="email",
                start_index=match.start(),
                end_index=match.end(),
                reason="user_request"
            ))

    # Stage 3: Apply redactions (right-to-left to preserve indices)
    markers.sort(key=lambda m: m.start_index, reverse=True)
    redacted_text = text
    for marker in markers:
        redacted_text = (
            redacted_text[:marker.start_index] +
            marker.replacement +
            redacted_text[marker.end_index:]
        )

    return redacted_text, markers
```

---

## 3. GDPR Compliance Analysis

### GDPR Principles Compliance

| GDPR Principle | AGENTX Implementation | Evidence |
|----------------|---------------------|----------|
| **Lawfulness, Fairness, Transparency** | ✅ Explicit user consent, transparent privacy policy | Privacy policy, consent dialogs |
| **Purpose Limitation** | ✅ Data used only for AI assistant functionality | System design docs |
| **Data Minimization** | ✅ Only store user preferences and conversation history | Retention policies |
| **Accuracy** | ✅ Temporal RAG with fact invalidation | HLD temporal requirements |
| **Storage Limitation** | ✅ TTL-based expiration (30/90/365 days) | Retention policies |
| **Integrity & Confidentiality** | ✅ Encryption at rest, PII redaction, local-only | Threat model, encryption docs |
| **Accountability** | ✅ Audit logs, PIA documentation, compliance review | This document |

### GDPR Individual Rights

| Right | Implementation | API Endpoint | Response Time |
|------|----------------|--------------|---------------|
| **Right to Access** | Full data export in JSON | `GET /api/memory/export` | <30s |
| **Right to Rectification** | Edit memory entries via API | `PUT /api/memory/{id}` | Immediate |
| **Right to Erasure** | Delete all user data | `POST /api/memory/forget-me` | <60s |
| **Right to Portability** | Export in standard JSON format | `GET /api/memory/export` | <30s |
| **Right to Object** | Disable data collection | Opt-out in settings | Immediate |
| **Right to Restrict Processing** | Pause AI processing | Settings: pause mode | Immediate |

### Data Controller/Processor

**Controller**: User (data owner)
**Processor**: AGENTX (local processing)

**Legal Basis**: Explicit consent (Article 6(1)(a))
- User must accept privacy policy on first launch
- User can withdraw consent at any time
- No processing without consent

### Special Category Data

**Status**: AGENTX does NOT process special category data (Article 9):
- No health data
- No biometric data (voice audio deleted after processing)
- No political/religious/philosophical opinions
- No trade union membership
- No genetic data
- No sexual orientation data

**Exception**: User may voluntarily share health information in conversation, but this is not systematically processed or stored.

### Data Protection Impact Assessment (DPIA)

**Required**: No - GDPR Article 35 DPIA not required because:
- Local-only processing (no cross-border transfers)
- No systematic monitoring of individuals
- No large-scale processing of special category data
- Minimal risk to individuals' rights and freedoms

---

## 4. CCPA Compliance Analysis

### CCPA Rights Compliance

| CCPA Right | AGENTX Implementation | API Endpoint |
|------------|---------------------|--------------|
| **Right to Know** | Full data disclosure | `GET /api/memory/export` |
| **Right to Delete** | Delete all user data | `POST /api/memory/forget-me` |
| **Right to Opt-Out** | Opt-out of data collection | Settings: disable collection |
| **Right to Non-Discrimination** | No penalty for exercising rights | N/A (no service changes) |

### Data Categories Sold

**Status**: AGENTX does NOT sell personal information (CCPA 1798.140(t))
- No data sold to third parties
- No data shared for monetary consideration
- No data shared for advertising purposes

### Data Categories Collected

| Category | Collected | Purpose | Retention |
|----------|-----------|---------|-----------|
| **Identifiers** | ✅ User ID (hashed) | User isolation | Forever |
| **Preferences** | ✅ User preferences | AI assistant functionality | 365 days |
| **Conversation History** | ✅ Chat transcripts | Context for AI responses | 90 days |
| **Voice Audio** | ⚠️ Temporary | STT processing (deleted immediately) | Session |
| **Search History** | ✅ Search queries | Context for AI responses | 90 days |

**Note**: Voice audio is deleted immediately after STT processing (not stored long-term).

### "Do Not Sell My Information" Compliance

**Status**: N/A - AGENTX does not sell personal information.

**Implementation**: If AGENTX ever adds data sharing, a prominent "Do Not Sell My Information" link would be added to the UI footer.

---

## 5. Data Residency Proofs

### Local-Only Architecture

**Claim**: All AGENTX data remains on user's hardware.

**Evidence**:

| Component | Data Location | Network Access | Proof |
|-----------|---------------|----------------|-------|
| **Qdrant Vector Store** | `/data/qdrant/` | Local only | Docker compose config |
| **Mem0AI Memory** | `/data/memory/` | Local only | Mem0AI config |
| **Ollama LLM** | `/data/ollama/` | Local only | Ollama config |
| **Plugin Data** | `/data/plugins/{name}/` | Local only | Plugin manifest |
| **User Settings** | `/data/settings/` | Local only | Settings schema |

### Network Traffic Analysis

**Outbound Connections** (User-Initiated Only):

| Destination | Purpose | User Control | Opt-Out |
|-------------|---------|--------------|---------|
| **None by default** | N/A | N/A | N/A |
| **SearXNG (optional)** | Web search plugin | User-enabled | Yes |
| **Company MIS (optional)** | Corporate data plugin | User-enabled | Yes |

**Audit Trail**:
```bash
# Verify no outbound connections
docker network inspect agentx_default
# Shows only local bridge network connections

# Monitor network traffic
tcpdump -i any -n host not 192.168.1.4 and not 127.0.0.1
# Should show zero traffic (except user-enabled plugins)
```

### Encryption at Rest

| Data Store | Encryption | Implementation | Key Management |
|------------|------------|----------------|----------------|
| **Qdrant** | ⚠️ Optional | Docker volume encryption | User-controlled |
| **Mem0AI** | ⚠️ Optional | Filesystem encryption | User-controlled |
| **Settings** | ✅ Yes | Encrypted config file | Local KMS |

**Recommendation**: Users should enable full-disk encryption (BitLocker/FileVault/LUKS) for maximum privacy.

---

## 6. Retention & Erasure Workflows

### TTL-Based Retention

| Data Type | TTL Policy | Retention Period | Expiration Action |
|-----------|------------|------------------|-------------------|
| **User Preferences** | `ttl_policy: "365d"` | 365 days | Auto-delete |
| **Conversation History** | `ttl_policy: "90d"` | 90 days | Auto-delete |
| **Temporary Data** | `ttl_policy: "30d"` | 30 days | Auto-delete |
| **User Identity** | `ttl_policy: "forever"` | Forever | Manual delete only |
| **Plugin Data** | Plugin-defined | Per-plugin policy | Plugin-specific |

### Erasure Workflows

#### User-Initiated Erasure

**Endpoint**: `POST /api/memory/forget-me`

**Process**:
1. Validate JWT token (authentication)
2. Hash user ID (verification)
3. Delete all Qdrant vectors (filter by user_id)
4. Delete all Mem0AI memories (filter by user_id)
5. Delete plugin data (iterate all plugins)
6. Delete audit logs (filter by user_id)
7. Delete user settings (preserve identity)
8. Generate erasure certificate

**Response Time**: <60s for 10k memories

#### Automatic Expiration

**Process**:
1. Nightly cron job (2 AM UTC)
2. Scan Qdrant for expired vectors (`expires_at < now`)
3. Batch delete expired vectors
4. Scan Mem0AI for expired memories
5. Batch delete expired memories
6. Log deletion summary

**Audit Trail**: All deletions logged with timestamp, reason, and count.

#### Plugin Data Erasure

**Process**:
1. Plugin uninstall triggered
2. Send erasure signal to plugin
3. Plugin deletes all data from `/data/plugins/{name}/`
4. Verify deletion (directory empty)
5. Log plugin erasure

**Fallback**: If plugin fails to delete, force-delete plugin directory.

### Data Recovery

**Status**: No backup/restore for deleted data (privacy requirement).

**Exception**: System backups (snapshots) are retained for 30 days, then securely deleted.

---

## 7. Privacy Controls

### User Privacy Preferences

```python
class UserPrivacyPrefs(BaseModel):
    """User-configurable privacy settings."""

    # PII Redaction
    redact_email: bool = True
    redact_phone: bool = True
    redact_name: bool = False  # Opt-in only
    redact_address: bool = True

    # Data Collection
    enable_voice_audio_storage: bool = False  # Delete after STT
    enable_conversation_history: bool = True
    enable_search_history: bool = True

    # Data Sharing
    allow_anonymous_telemetry: bool = False  # Opt-in only
    allow_plugin_data_sharing: bool = False  # Per-plugin

    # Retention
    retention_period: Literal["30d", "90d", "365d", "forever"] = "90d"

    # Data Processing
    allow_temporal_indexing: bool = True
    allow_memory_consolidation: bool = True
```

### Privacy Settings UI

**Settings Pages**:

1. **PII Redaction**
   - Checkbox: Redact email addresses
   - Checkbox: Redact phone numbers
   - Checkbox: Redact names (opt-in)
   - Link: View redaction rules

2. **Data Collection**
   - Checkbox: Save conversation history
   - Checkbox: Save search history
   - Checkbox: Store voice audio (not recommended)
   - Link: View data stores

3. **Data Sharing**
   - Checkbox: Anonymous telemetry (help improve AGENTX)
   - Checkbox: Allow plugins to access data
   - Link: View plugin permissions

4. **Data Management**
   - Button: Export all data (GDPR/CCPA right to access)
   - Button: Delete all data (GDPR/CCPA right to erasure)
   - Dropdown: Retention period (30/90/365/forever)
   - Link: View retention policy

### Audit Trail

**Privacy Events Logged**:
- PII detected and redacted (with type and count)
- User consent granted/revoked
- Privacy settings changed
- Data export requested
- Data deletion requested/completed
- Plugin data access granted/denied

**Log Format**:
```json
{
  "timestamp": "2026-01-19T12:34:56Z",
  "event_type": "pii_redacted",
  "user_id": "<SHA-256 hash>",
  "details": {
    "pii_types": ["email", "phone"],
    "count": 3,
    "detection_method": "regex"
  }
}
```

---

## 8. Risk Assessment

### Privacy Risks

| Risk | Likelihood | Impact | Mitigation | Residual Risk |
|------|------------|--------|------------|---------------|
| **PII in logs** | Low | High | Pre-logging PII scan | Low |
| **Plugin data exfiltration** | Low | Critical | Sandboxing, no network | Low |
| **Unintended PII storage** | Low | Medium | PII detection at all entry points | Low |
| **Data recovery after deletion** | Very Low | High | Secure deletion, no backups | Very Low |
| **User profiling** | Very Low | Medium | Local-only, no profiling | Very Low |
| **Voice audio storage** | Low | Medium | Delete after STT (default) | Low |

### Privacy Risk Matrix

```
           Low Impact    Medium Impact    High Impact    Critical Impact
High Likelihood     Low              Medium           High           Critical
Medium Likelihood   Low              Medium           Medium         High
Low Likelihood      Very Low         Low              Low            Medium
Very Low Likelihood Very Low         Very Low         Very Low       Low
```

**AGENTX Privacy Posture**: All risks in **Low** or **Very Low** categories.

### Compliance Risks

| Compliance Requirement | Risk | Mitigation |
|------------------------|------|------------|
| **GDPR Article 25 (Privacy by Design)** | Low | PIA documented, privacy controls built-in |
| **GDPR Article 17 (Right to Erasure)** | Low | Forget-me endpoint, <60s deletion |
| **CCPA 1798.100 (Right to Delete)** | Low | Forget-me endpoint, verified deletion |
| **CCPA 1798.120 (Right to Opt-Out)** | N/A | No data sale, N/A |

### Third-Party Risks

| Third Party | Risk Type | Mitigation |
|-------------|-----------|------------|
| **Ollama** | Local LLM inference | No risk (local only) |
| **Qdrant** | Local vector store | No risk (local only) |
| **FastMCP Plugins** | Third-party code | Sandboxing, code signing, permissions |
| **SearXNG (optional)** | Web search queries | User-enabled, opt-out, PII redacted |

**Supply Chain Protection**:
- All dependencies pinned to specific versions
- Signature verification for plugins
- Regular security audits
- No external network by default

---

## Appendix: Privacy Checklist

### Pre-Deployment

- [ ] PII detection tested with sample data
- [ ] Redaction rules verified for all PII types
- [ ] GDPR rights tested (access, erasure, portability)
- [ ] CCPA rights tested (know, delete, opt-out)
- [ ] Data residency verified (local-only)
- [ ] Retention policies configured
- [ ] Privacy settings UI implemented
- [ ] User consent flow implemented
- [ ] Audit logging for privacy events
- [ ] Privacy policy written and reviewed

### Post-Deployment

- [ ] Monthly privacy log review
- [ ] Quarterly PIA update
- [ ] Annual GDPR compliance audit
- [ ] Annual CCPA compliance audit
- [ ] User privacy feedback review

---

## Sign-Off

**Privacy Impact Assessment Completed By**: _________________ Date: _______

**Legal Review**: _________________ Date: _______

**Security Review**: _________________ Date: _______

**Approved By**: _________________ Date: _______

---

**This privacy impact assessment is part of AGENTX HLD v1.0. See [HLD.md](HLD.md) for complete architecture.**
