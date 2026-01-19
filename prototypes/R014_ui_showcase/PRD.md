# PRD - R014: Generative UI Showcase

## Product Overview

**Name**: R014 UI Showcase
**Level**: Frontend-Focused (Weak Backend, Strong Frontend)
**Category**: UI/UX Design System
**Estimated Time**: 8 hours

## User Utility

R014 serves as a **visual reference and interactive demo** for the AGENTX generative UI system. It answers the question: "How will AGENTX actually look and feel?"

**Target Users**:
- **Developers**: Need to see widget examples before implementing backend
- **Designers**: Need to review animation timing, colors, layouts
- **Stakeholders**: Need to demo the UI without complex backend setup

**Key Value**:
- See all 7 generative UI widgets in one place
- Test animations and interactions without agent context
- Validate design system before full implementation
- Quick visual feedback for design iterations

## Requirements

### Functional Requirements

#### UI Widgets (FR-1)
- **Markdown Block**: Display formatted text with fade-in animation
- **Card**: Show structured info with slide-up animation and action buttons
- **Form**: Multi-field input with scale-in animation
- **Progress**: Task completion with expand animation
- **Action**: Single button with bounce-hover animation
- **Confirmation**: Yes/No dialog with scale-fade animation
- **Voice**: Waveform visualizer with pulse animation

#### Interactions (FR-2)
- Dark/light mode toggle
- Widget dismissible by X button
- Form validation feedback
- Button hover states
- Click-to-copy for code blocks

#### Layout (FR-3)
- Fixed FAB button (bottom-right)
- Collapsible sidebar (history)
- Central widget display area
- Responsive (mobile + desktop)

#### Background Animation (FR-4)
- Subtle particle/wave effect
- Non-distracting
- Performance optimized (60fps)

### Non-Functional Requirements

- **Performance**: Animations at 60fps, page load <2s
- **Usability**: Intuitive navigation, clear visual hierarchy
- **Accessibility**: WCAG AA compliant, keyboard navigation
- **Reliability**: Graceful degradation without JS

## Technical Specification

### Backend (FastAPI - Mock Data Only)

#### Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/health | Health check |
| GET | /api/v1/mock/descriptors | All mock UI descriptors |
| GET | /api/v1/mock/descriptors/{type} | Descriptors by type |
| GET | /api/v1/mock/stream | SSE stream simulation |

#### Data Models
```python
class UIDescriptor(BaseModel):
    id: str
    type: Literal["markdown", "card", "form", "progress", "action", "confirmation", "voice"]
    content: Optional[str] = None
    title: Optional[str] = None
    metadata: Dict[str, Any] = {}
    dismissible: bool = True
```

### Frontend (Next.js + shadcn/ui + Framer Motion)

#### Pages
- `/` - Main showcase with interactive demos
- `/gallery` - Widget gallery (all widgets in isolation)

#### Components
```
components/
├── showcase/
│   ├── widget-display.tsx       # Renders individual widgets
│   ├── background-animation.tsx # Particle/wave effect
│   └── theme-toggle.tsx         # Dark/light mode
├── widgets/
│   ├── markdown-widget.tsx      # Text/Markdown display
│   ├── card-widget.tsx          # Info cards with actions
│   ├── form-widget.tsx          # Multi-field forms
│   ├── progress-widget.tsx      # Progress indicators
│   ├── action-widget.tsx        # Action buttons
│   ├── confirmation-widget.tsx  # Yes/No dialogs
│   └── voice-widget.tsx         # Voice waveform
└── ui/                           # shadcn/ui components
```

#### Animation System (Framer Motion)
```typescript
export const widgetVariants = {
  markdown: { initial: { opacity: 0 }, animate: { opacity: 1 }, exit: { opacity: 0 } },
  card: { initial: { opacity: 0, y: 20 }, animate: { opacity: 1, y: 0 }, exit: { opacity: 0, y: -20 } },
  form: { initial: { opacity: 0, scale: 0.9 }, animate: { opacity: 1, scale: 1 }, exit: { opacity: 0, scale: 0.9 } },
  // ... etc
};
```

#### Color Scheme (shadcn/ui CSS Variables)
```css
:root {
  --primary: 222.2 47.4% 11.2%;
  --background: 0 0% 100%;
  --foreground: 222.2 84% 5%;
}
.dark {
  --background: 222.2 84% 5%;
  --foreground: 210 40% 98%;
}
```

## Success Criteria

1. ✅ All 7 widgets render correctly with animations
2. ✅ Dark/light mode toggle works
3. ✅ Widget gallery page shows all components
4. ✅ Background animation runs smoothly (60fps)
5. ✅ Responsive on mobile and desktop
6. ✅ Mock API returns valid descriptors
7. ✅ Page load time <2s

## Dependencies

### Backend
- fastapi>=0.115.0
- pydantic>=2.0.0
- uvicorn>=0.24.0
- pydantic-settings>=2.0.0

### Frontend
- next@^15.1.0
- react@^19.0.0
- framer-motion@^11.0.0
- lucide-react@^0.468.0
- tailwindcss@^3.4.0
- @radix-ui/react-slot@^1.1.0

## Out of Scope

- **No real LLM integration**: All content is pre-written mock data
- **No DSPy agents**: No tool use, no ReAct loops
- **No memory system**: No Qdrant, no Mem0AI
- **No WebSocket**: Simulated streaming with SSE only
- **No real voice**: Voice widget is visual only (no STT/TTS)
- **No backend business logic**: API serves static JSON only

## Design References

- **Design Philosophy**: "Sexy but Minimal" from `docs/engineering/generative_ui_design_plan.md`
- **Color Palette**: shadcn/ui default (Section 5.3)
- **Typography**: Inter font (Section 5.4)
- **Animation Timing**: 200-300ms transitions (Section 5.5)
- **Layout Model**: FAB + Sidebar + Widget Area (Section 5.6)

## Next Steps After R014

1. **R011 Integration**: Connect R014 UI to R011 backend agents
2. **R013 Integration**: Add WebSocket streaming from R013
3. **Phase 3 Implementation**: Build real UI DSPy agent (T301-T302)
4. **Phase 4 Implementation**: Add LangGraph state machines (T400-T402)
