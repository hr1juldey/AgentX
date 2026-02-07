# Spec: Library Header

Shared header component for library pages with navigation buttons and theme toggle.

## Purpose

Provide consistent header across all library pages with back-button navigation (context-aware) and theme toggle for accessibility.

---

## How it LOOKS (Visual)

### Requirement: Header layout

The system SHALL render header with left-aligned back button, center title, and right-aligned theme toggle.

#### Scenario: Library index header

- **WHEN** user is on `/library`
- **THEN** header shows: "[← Back to AGENTX]  Design Library  [◑ Theme]"
- **AND** elements are evenly spaced
- **AND** header height is approximately 60px

#### Scenario: Component demo header

- **WHEN** user is on `/library/physics-cells`
- **THEN** header shows: "[← Back to Library]  Physics Cells Demo  [◑ Theme]"
- **AND** back button context changes based on route

#### Scenario: Responsive header on mobile

- **WHEN** viewport width < 768px
- **THEN** header elements stack or compress
- **AND** back button remains easily tappable (44px min)

---

### Requirement: Button styling

The system SHALL style navigation buttons consistently with app design tokens.

#### Scenario: Back button appearance

- **WHEN** back button is rendered
- **THEN** button uses secondary styling (outlined or ghost)
- **AND** chevron "←" icon precedes text
- **AND** hover state shows background color change

#### Scenario: Theme toggle appearance

- **WHEN** theme toggle is rendered
- **THEN** button shows sun/moon icon based on current theme
- **AND** button is circular or icon-only
- **AND** toggle state is visually clear

---

## How it WORKS (Behavioral)

### Requirement: Context-aware back button

The system SHALL display appropriate back button text and destination based on current route.

#### Scenario: Back to main from library

- **WHEN** current route is `/library`
- **THEN** back button shows "← Back to AGENTX"
- **AND** click navigates to `/`

#### Scenario: Back to library from component

- **WHEN** current route is `/library/physics-cells`
- **THEN** back button shows "← Back to Library"
- **AND** click navigates to `/library`

#### Scenario: Future component pages

- **WHEN** new component demo pages are added
- **THEN** back button logic applies to all library routes
- **AND** pattern scales without code changes

---

### Requirement: Theme toggle functionality

The system SHALL toggle between light and dark themes with preference persistence.

#### Scenario: Toggle to dark mode

- **WHEN** user clicks theme toggle in light mode
- **THEN** theme switches to dark mode
- **AND** preference saves to localStorage
- **AND** entire app updates to dark theme

#### Scenario: Toggle to light mode

- **WHEN** user clicks theme toggle in dark mode
- **THEN** theme switches to light mode
- **AND** preference saves to localStorage
- **AND** entire app updates to light theme

#### Scenario: Respect system preference on first visit

- **WHEN** user visits site for first time
- **THEN** system detects OS theme preference
- **AND** default theme matches system setting
- **AND** localStorage saves initial preference

---

### Requirement: Header stickiness

The system SHALL keep header fixed at top of page with shadow for depth.

#### Scenario: Fixed header on scroll

- **WHEN** user scrolls down library page
- **THEN** header remains fixed at top
- **AND** content scrolls behind header
- **AND** header shows subtle box shadow

#### Scenario: Header z-index layering

- **WHEN** header is fixed
- **THEN** header z-index is higher than page content
- **AND** header always appears above other elements
- **AND** dropdowns/modals can layer above header if needed

---

## How it INTERACTS (Integration)

### Requirement: Route detection

The system SHALL detect current route to determine header behavior.

#### Scenario: Use Next.js usePathname hook

- **WHEN** header component renders
- **THEN** system uses `usePathname()` to detect route
- **AND** back button text and destination update accordingly

#### Scenario: Route-based header variants

- **WHEN** header is on main app page (not library)
- **THEN** different header variant may be used
- **AND** library header only appears on library routes

---

### Requirement: Theme context integration

The system SHALL integrate with app-wide theme context/provider.

#### Scenario: Consume theme context

- **WHEN** header component mounts
- **THEN** system consumes theme from context provider
- **AND** theme toggle calls context's toggle function

#### Scenario: Theme changes propagate

- **WHEN** user toggles theme from header
- **THEN** entire page tree receives theme update
- **AND** all themed components update colors

---

### Requirement: Navigation integration

The system SHALL integrate with Next.js router for button navigation.

#### Scenario: Use Next.js Link for navigation

- **WHEN** back button is clicked
- **THEN** system uses `router.push()` or `<Link>` component
- **AND** navigation is client-side (no page reload)

#### Scenario: Keyboard navigation support

- **WHEN** user tabs to back button and presses Enter
- **THEN** navigation executes
- **AND** button is accessible via keyboard
