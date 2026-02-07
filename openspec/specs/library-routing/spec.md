# Spec: Library Routing

Navigation structure for design library with main → library → component → back flow.

## Purpose

Define Next.js App Router routes for design library system, enabling navigation from main app to library index to individual component demo pages with proper back button behavior.

---

## How it LOOKS (Visual)

### Requirement: URL structure clarity

The system SHALL use clear, human-readable URLs that reflect navigation hierarchy.

#### Scenario: Main page URL

- **WHEN** user is on main page
- **THEN** URL is `https://domain.com/` or `https://domain.com`
- **AND** no additional path segments

#### Scenario: Library index URL

- **WHEN** user navigates to library
- **THEN** URL is `https://domain.com/library`
- **AND** URL is short and memorable

#### Scenario: Component demo URL

- **WHEN** user views component demo
- **THEN** URL is `https://domain.com/library/physics-cells`
- **AND** component name is clear and descriptive

---

### Requirement: Browser navigation support

The system SHALL support browser back/forward buttons for navigation.

#### Scenario: Back button from component to library

- **WHEN** user clicks browser back button on component page
- **THEN** navigation returns to library index
- **AND** scroll position is preserved if possible

#### Scenario: Forward button re-navigates

- **WHEN** user clicks browser forward button after going back
- **THEN** navigation returns to previous page
- **AND** page state is restored

#### Scenario: URL bar navigation

- **WHEN** user types `/library/physics-cells` directly in URL bar
- **THEN** component demo page loads correctly
- **AND** no navigation errors occur

---

## How it WORKS (Behavioral)

### Requirement: Next.js App Router structure

The system SHALL use Next.js 14+ App Router with file-based routing.

#### Scenario: Library index route

- **WHEN** user navigates to `/library`
- **THEN** Next.js serves `frontend/src/app/library/page.tsx`
- **AND** page renders as full-page component

#### Scenario: Component demo route

- **WHEN** user navigates to `/library/physics-cells`
- **THEN** Next.js serves `frontend/src/app/library/physics-cells/page.tsx`
- **AND** page renders as full-page component

#### Scenario: Route matching

- **WHEN** URL doesn't match any library route
- **THEN** Next.js 404 page is shown
- **AND** user can navigate back to library index

---

### Requirement: Client-side navigation

The system SHALL use Next.js Link component for client-side navigation (no page reload).

#### Scenario: Link click navigates client-side

- **WHEN** user clicks "Design Library" button in header
- **THEN** navigation occurs without page reload
- **AND** URL updates in browser bar
- **AND** page content updates smoothly

#### Scenario: Navigation preserves app state

- **WHEN** navigating between library pages
- **THEN** React state is preserved where possible
- **AND** no full re-render of root layout occurs

---

### Requirement: Programmatic navigation

The system SHALL support programmatic navigation via Next.js useRouter hook.

#### Scenario: Back button in header

- **WHEN** user clicks "← Back to Library" button
- **THEN** router.back() or router.push('/library') executes
- **AND** navigation occurs programmatically

#### Scenario: Redirect after demo completion

- **WHEN** demo component signals completion
- **THEN** system can programmatically navigate to related page
- **AND** navigation is controlled via code

---

## How it INTERACTS (Integration)

### Requirement: Header navigation integration

The system SHALL integrate navigation buttons into shared LibraryHeader component.

#### Scenario: Header on library index

- **WHEN** user is on `/library`
- **THEN** header shows "← Back to AGENTX" button
- **AND** click navigates to `/`

#### Scenario: Header on component page

- **WHEN** user is on `/library/physics-cells`
- **THEN** header shows "← Back to Library" button
- **AND** click navigates to `/library`

#### Scenario: Main page header

- **WHEN** user is on main page `/`
- **THEN** header shows "Design Library" button
- **AND** click navigates to `/library`

---

### Requirement: Route metadata

The system SHALL export route constants for type-safe navigation.

#### Scenario: Route constant definitions

- **WHEN** code imports route constants
- **THEN** system provides: `ROUTES.LIBRARY = '/library'`
- **AND** `ROUTES.COMPONENT_DEMO = '/library/physics-cells'`
- **AND** constants are used throughout codebase

#### Scenario: Type-safe navigation

- **WHEN** component navigates using router.push()
- **THEN** TypeScript validates route strings
- **AND** typos in routes are caught at compile time
