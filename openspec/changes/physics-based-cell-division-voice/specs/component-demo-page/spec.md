# Spec: Component Demo Page

Isolated full-page demo for individual library components with description and controls.

## Purpose

Provide dedicated page for each library component to run in isolation with full viewport space, descriptive documentation, and interactive controls.

---

## How it LOOKS (Visual)

### Requirement: Full-viewport demo area

The system SHALL allocate majority of viewport space to component demo.

#### Scenario: Demo takes primary space

- **WHEN** component demo page loads
- **THEN** demo area occupies ~70-80% of viewport height
- **AND** component renders centered in demo area
- **AND** background contrasts with component for visibility

#### Scenario: Responsive demo sizing

- **WHEN** viewport size changes
- **THEN** demo area resizes proportionally
- **AND** component scales appropriately
- **AND** no overflow or clipping occurs

---

### Requirement: Description section

The system SHALL display component description above or below demo area.

#### Scenario: Description header

- **WHEN** demo page loads
- **THEN** page shows component title as heading
- **AND** brief description explains component purpose
- **AND** description is 1-3 paragraphs

#### Scenario: Usage documentation

- **WHEN** component has API or props
- **THEN** documentation shows prop types and descriptions
- **AND** code examples demonstrate usage
- **AND** examples are syntax-highlighted

---

### Requirement: Control panel

The system SHALL provide interactive controls for component configuration.

#### Scenario: Component-specific controls

- **WHEN** component has configurable parameters
- **THEN** control panel shows sliders/toggles for each parameter
- **AND** changing control immediately updates component
- **AND** control shows current value

#### Scenario: Audio controls for voice components

- **WHEN** component uses microphone input
- **THEN** control panel shows "Enable Mic" button
- **AND** button shows current mic state (on/off)
- **AND** permission error shows if denied

---

## How it WORKS (Behavioral)

### Requirement: Component isolation

The system SHALL render component in isolation from main app context.

#### Scenario: Fresh component mount

- **WHEN** demo page loads
- **THEN** component mounts as new React instance
- **AND** component has fresh internal state
- **AND** no shared state with other pages

#### Scenario: Unmount on navigation

- **WHEN** user navigates away from demo page
- **THEN** component unmounts completely
- **AND** all timers/listeners are cleaned up
- **AND** no memory leaks occur

---

### Requirement: Component props configuration

The system SHALL pass configurable props to component based on control panel state.

#### Scenario: Default props on load

- **WHEN** demo page first loads
- **THEN** component receives default prop values
- **AND** defaults are chosen for good demonstration

#### Scenario: Props update from controls

- **WHEN** user adjusts control panel
- **THEN** component props update via state
- **AND** component re-renders with new props
- **AND** transition is smooth (no jarring resets)

---

### Requirement: Error boundary

The system SHALL wrap component in error boundary for graceful error handling.

#### Scenario: Component throws error

- **WHEN** component crashes during render or interaction
- **THEN** error boundary catches error
- **AND** friendly error message displays
- **AND** page doesn't crash (white screen avoided)

#### Scenario: Error recovery

- **WHEN** error is displayed
- **THEN** user can click "Retry" button
- **AND** component remounts with fresh state
- **AND** error clears if issue was transient

---

## How it INTERACTS (Integration)

### Requirement: Route parameter handling

The system SHALL use route parameters to determine which component to display.

#### Scenario: Parse component slug from URL

- **WHEN** user visits `/library/physics-cells`
- **THEN** system extracts "physics-cells" from path
- **AND** system looks up component in catalog
- **AND** appropriate component renders

#### Scenario: Invalid component slug

- **WHEN** user visits `/library/nonexistent-component`
- **THEN** system shows "Component not found" message
- **AND** user can navigate back to library index
- **AND** no 404 page (graceful degradation)

---

### Requirement: Header integration

The system SHALL use LibraryHeader component with appropriate back button.

#### Scenario: Header with back button

- **WHEN** demo page renders
- **THEN** LibraryHeader shows "← Back to Library"
- **AND** click navigates to `/library`
- **AND** header is consistent across all demo pages

---

### Requirement: Component import

The system SHALL dynamically import component based on route.

#### Scenario: Static import for known components

- **WHEN** component is one of known set (e.g., physics-cells)
- **THEN** system uses static import for performance
- **AND** component is included in initial bundle

#### Scenario: Dynamic import for extensibility

- **WHEN** new components are added in future
- **THEN** system can use dynamic import
- **AND** component loads on-demand
- **AND** code splitting reduces initial bundle size
