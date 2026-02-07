# Spec: Component Isolation

Independent component execution ensuring no shared state or interference between demos.

## Purpose

Guarantee that each library component demo runs in complete isolation with fresh state, independent audio contexts, and no cross-component interference.

---

## How it LOOKS (Visual)

### Requirement: Visual isolation indicators

The system SHALL provide visual cues that component is running in isolated environment.

#### Scenario: Demo container boundary

- **WHEN** component demo page loads
- **THEN** demo area has visible boundary or background
- **AND** boundary distinguishes demo from page chrome
- **AND** user understands component is isolated

#### Scenario: Fresh state indicator

- **WHEN** component initializes
- **THEN** brief "Initializing..." indicator may show
- **AND** indicator disappears when component is ready
- **AND** user understands component is starting fresh

---

## How it WORKS (Behavioral)

### Requirement: Fresh React component mount

The system SHALL ensure each demo page creates a new React component instance.

#### Scenario: Component mount on navigation

- **WHEN** user navigates to demo page
- **THEN** component's useEffect() hooks run fresh
- **AND** all useState() initializers execute
- **AND** component has no memory from previous session

#### Scenario: Component unmount on navigation away

- **WHEN** user navigates away from demo page
- **THEN** component's useEffect cleanup functions run
- **AND** all timers/intervals are cleared
- **AND** event listeners are removed
- **AND** no background activity continues

---

### Requirement: Independent audio context

Each audio-reactive component SHALL create its own Web Audio API context.

#### Scenario: Separate audio context per demo

- **WHEN** physics-cells demo page loads
- **THEN** component creates new AudioContext instance
- **AND** audio context is independent of other pages
- **AND** audio context is destroyed on unmount

#### Scenario: Microphone permission per demo

- **WHEN** user enables microphone on demo page
- **THEN** permission request is specific to this page
- **AND** permission doesn't persist to other pages
- **AND** user must re-enable on revisit (fresh start)

#### Scenario: Audio cleanup on unmount

- **WHEN** user navigates away with audio active
- **THEN** audio context suspends or closes
- **AND** microphone stream is stopped
- **AND** browser indicator (red dot) disappears

---

### Requirement: No shared state storage

The system SHALL not use global state or external storage for component state.

#### Scenario: Component state is local

- **WHEN** component manages internal state
- **THEN** state is stored in React useState() hooks
- **AND** no global variables or singletons are used
- **AND** state doesn't persist across page navigations

#### Scenario: No Redux/Zustand usage

- **WHEN** component needs state management
- **THEN** local React state is preferred
- **AND** global stores are NOT used for demo components
- **AND** each demo is self-contained

---

### Requirement: Prop-based configuration

The system SHALL pass all configuration via props (no environment or config file dependencies).

#### Scenario: Props control all behavior

- **WHEN** component renders in demo
- **THEN** all configurable parameters come via props
- **AND** changing demo controls updates props
- **AND** component is deterministic based on props

#### Scenario: No hidden configuration

- **WHEN** component behaves unexpectedly
- **THEN** all behavior is traceable to props
- **AND** no environment variables affect behavior
- **AND** no external config files are read

---

## How it INTERACTS (Integration)

### Requirement: Demo container wrapper

The system SHALL provide wrapper component that enforces isolation.

#### Scenario: DemoContainer component

- **WHEN** demo page renders
- **THEN** `<DemoContainer>` wraps the component
- **AND** container manages mounting/unmounting
- **AND** container ensures cleanup on unmount

#### Scenario: Error boundary in container

- **WHEN** component throws error
- **THEN** DemoContainer's error boundary catches it
- **AND** error doesn't crash entire app
- **AND** other pages remain functional

---

### Requirement: Resource cleanup verification

The system SHALL verify all resources are released when demo unmounts.

#### Scenario: Check for memory leaks

- **WHEN** component unmounts
- **THEN** no event listeners remain attached
- **AND** no timers/intervals continue running
- **AND** no WebSockets or AudioContexts remain active

#### Scenario: Cleanup logging in development

- **WHEN** app is in development mode
- **THEN** console logs confirm cleanup actions
- **AND** warnings show if resources leak
- **AND** developers can verify isolation

---

### Requirement: Multiple demos can't interfere

The system SHALL prevent multiple demo tabs from interfering with each other.

#### Scenario: Multiple tabs open simultaneously

- **WHEN** user opens demo page in multiple tabs
- **THEN** each tab has independent component instances
- **AND** audio in one tab doesn't affect others
- **AND** state is not shared via localStorage or BroadcastChannel

#### Scenario: Background tab throttling

- **WHEN** demo tab is in background
- **THEN** component continues running but may throttle
- **AND** audio context may suspend to save resources
- **AND** foreground tab remains responsive
