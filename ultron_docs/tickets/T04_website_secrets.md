# T4 — Website Master Control Panel + Secrets Management

## Context
The website is Ghost's visual control panel. Most critically, it's where ALL secrets (API keys) are managed. Ghost pastes keys here. Zero technical knowledge required. A 5-year-old could do it.

**Dependencies:** T1, T2  
**Blocks:** T5 (secrets needed to connect services)

## Files to Create
| File | Purpose |
|---|---|
| `website/src/App.tsx` | Root app with routing |
| `website/src/pages/Settings.tsx` | Secrets management UI |
| `website/src/pages/Dashboard.tsx` | System status dashboard |
| `website/src/pages/Chat.tsx` | Conversation interface |
| `website/src/components/SecretField.tsx` | Paste-and-save component |
| `website/src/components/KeyPoolStatus.tsx` | API key health display |
| `website/vite.config.ts` | Build configuration |
| `website/package.json` | React dependencies |

## Implementation Plan

### Settings Page Design
```
ULTRON SETTINGS
═══════════════════════════════════════

📡 GEMINI API KEYS
┌─────────────────────────────────────────┐
│ Key 1:  AIza...xxxx  ✅ Active          │
│ Key 2:  [paste here and press enter]    │
│ Key 3:  [paste here and press enter]    │
│         [+ Add Another Gemini Key]      │
└─────────────────────────────────────────┘

🤖 GROQ API KEYS  
┌─────────────────────────────────────────┐
│ Key 1:  gsk_...xxxx  ✅ Active          │
│         [+ Add Another Groq Key]        │
└─────────────────────────────────────────┘

[SAVE ALL]  ← One click saves everything
```

### SecretField Component
```tsx
// Paste key → immediate save → show checkmark
// Never shows full key after saving (security)
// Shows last 4 chars only: "...xxxx"
// Delete button to remove a key
// No forms, no submit buttons - auto-saves on blur
```

## Acceptance Criteria
- [ ] Paste API key → auto-saved within 200ms
- [ ] Keys never shown in full after saving
- [ ] Adding 20 Gemini keys takes under 5 minutes
- [ ] Dashboard shows real-time system health
- [ ] Works on mobile browser (Ghost uses phone)
- [ ] No technical knowledge required

## Edge Cases
- Save fails: show red error, key not lost (stays in field)
- Duplicate key: show warning "This key already exists"
- Invalid format: basic validation before saving
