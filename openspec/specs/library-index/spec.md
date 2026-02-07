# Spec: Library Index

Component showcase grid displaying available library components as cards with thumbnails.

## Purpose

Provide browsable index of all experimental UI components in the design library, with visual cards showing thumbnails, titles, descriptions, and navigation to demo pages.

---

## How it LOOKS (Visual)

### Requirement: Grid layout

The system SHALL display component cards in responsive grid layout.

#### Scenario: Desktop grid (3 columns)

- **WHEN** viewport width >= 1024px
- **THEN** grid displays 3 columns of cards
- **AND** cards have equal width and spacing
- **AND** grid is centered with max-width constraint

#### Scenario: Tablet grid (2 columns)

- **WHEN** viewport width is 768px - 1023px
- **THEN** grid displays 2 columns of cards
- **AND** cards are larger than desktop view

#### Scenario: Mobile grid (1 column)

- **WHEN** viewport width < 768px
- **THEN** grid displays single column
- **AND** cards are full-width with comfortable padding

---

### Requirement: Component card design

The system SHALL render each component as a card with thumbnail, title, description, and action button.

#### Scenario: Card visual structure

- **WHEN** component card is rendered
- **THEN** card shows: [thumbnail image top]
- **AND** [component title below thumbnail]
- **AND** [brief description below title]
- **AND** ["View Demo →" button at bottom]

#### Scenario: Thumbnail preview

- **WHEN** card displays component thumbnail
- **THEN** thumbnail shows component in action
- **AND** thumbnail is static image or animated preview
- **AND** thumbnail aspect ratio is consistent across cards

#### Scenario: Card hover effects

- **WHEN** user hovers over component card
- **THEN** card elevates with shadow increase
- **AND** "View Demo" button shows background color change
- **AND** cursor changes to pointer

---

### Requirement: Empty state handling

The system SHALL display helpful message when no components are available.

#### Scenario: Empty library message

- **WHEN** component array is empty
- **THEN** system shows "No components yet" message
- **AND** message suggests components will be added soon
- **AND** user can navigate back to main app

---

## How it WORKS (Behavioral)

### Requirement: Component metadata

The system SHALL define component metadata array for library index.

#### Scenario: Component metadata structure

- **WHEN** component is registered in library
- **THEN** metadata includes: `{ id, title, description, thumbnail, slug }`
- **AND** `slug` determines route path
- **AND** `thumbnail` is path to image in `/public/library/thumbnails/`

#### Scenario: Add new component to library

- **WHEN** developer creates new component
- **THEN** they add metadata object to components array
- **AND** component automatically appears in library index
- **AND** no separate registration step needed

---

### Requirement: Card click navigation

The system SHALL navigate to component demo page when card is clicked.

#### Scenario: Click card body

- **WHEN** user clicks anywhere on card (except button)
- **THEN** navigation occurs to component demo page
- **AND** URL updates to `/library/[component-slug]`

#### Scenario: Click "View Demo" button

- **WHEN** user clicks "View Demo →" button
- **THEN** navigation occurs to component demo page
- **AND** same behavior as card body click

---

### Requirement: Search and filter (future)

The system SHALL support search and filter functionality for larger component libraries.

#### Scenario: Search input

- **WHEN** library has >10 components
- **THEN** search input appears above grid
- **AND** typing filters cards by title/description
- **AND** non-matching cards hide

#### Scenario: Category filter

- **WHEN** library has multiple component categories
- **THEN** category pills appear above grid
- **AND** clicking category filters to that category
- **AND** "All" option shows all components

---

## How it INTERACTS (Integration)

### Requirement: Component catalog data source

The system SHALL load component metadata from centralized configuration.

#### Scenario: Import components array

- **WHEN** library index page loads
- **THEN** system imports components from `/lib/navigation/library-routes.ts`
- **AND** array is TypeScript-typed for safety

#### Scenario: Future database migration

- **WHEN** library grows to many components
- **THEN** metadata can migrate from array to JSON file
- **AND** later to database if needed
- **AND** component registration API remains consistent

---

### Requirement: Link integration

The system SHALL use Next.js Link component for client-side navigation.

#### Scenario: Link wrapping card

- **WHEN** component card is rendered
- **THEN** `<Link href="/library/physics-cells">` wraps card
- **AND** navigation is client-side (no page reload)

---

### Requirement: Image optimization

The system SHALL use Next.js Image component for thumbnail optimization.

#### Scenario: Thumbnail loading

- **WHEN** component card mounts
- **THEN** thumbnail loads via `<Image>` component
- **AND** image is optimized (WebP, lazy loading)
- **AND** placeholder blur shown while loading
