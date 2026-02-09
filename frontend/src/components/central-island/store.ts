/**
 * Zustand store for Morphing Central Island state.
 *
 * Tracks drag positions, collapse state, and selected mode.
 * Provides synchronous access to avoid stale closure issues.
 *
 * Supports sequential collapse based on distance to selected island.
 */

import { create } from 'zustand';

export type ModeType = 'voice' | 'chat' | 'file' | 'camera';

export interface Position {
  x: number;
  y: number;
}

export interface CollapseIsland {
  mode: ModeType;
  distance: number; // Distance to selected island
  order: number; // Collapse order (0 = first, 1 = second, etc.)
}

interface MorphingIslandState {
  // Drag offsets for each mode (relative to original position)
  dragOffsets: Record<ModeType, Position>;

  // Currently selected mode
  selectedMode: ModeType | null;

  // Current position of selected mode (original + drag offset)
  selectedModeCurrentPosition: Position | null;

  // Collapse state
  isCollapsing: boolean;
  collapseProgress: number;
  collapseComplete: boolean;

  // Sequential collapse data
  collapseIslands: CollapseIsland[]; // Islands in order of collapse (closest first)
  collapseIslandsCount: number; // Number of islands to collapse (excluding selected)

  // Actions
  setDragOffset: (mode: ModeType, offset: Position) => void;
  resetDragOffsets: () => void;
  setSelectedMode: (mode: ModeType | null, currentPosition: Position | null) => void;
  setCollapsing: (isCollapsing: boolean) => void;
  setCollapseProgress: (progress: number) => void;
  setCollapseComplete: (complete: boolean) => void;
  resetCollapse: () => void;

  // Calculate and store collapse order based on distances
  calculateCollapseOrder: () => void;

  // Getters for synchronous access (no stale closures)
  getDragOffset: (mode: ModeType) => Position;
  getCurrentPosition: (mode: ModeType) => Position;
  getSelectedModeCurrentPosition: () => Position | null;
  getCollapseIsland: (mode: ModeType) => CollapseIsland | undefined;
}

// Original positions for each mode (from MODES constant)
const ORIGINAL_POSITIONS: Record<ModeType, Position> = {
  voice: { x: 0, y: -80 },
  chat: { x: -80, y: 0 },
  file: { x: 80, y: 0 },
  camera: { x: 0, y: 80 },
};

const INITIAL_DRAG_OFFSETS: Record<ModeType, Position> = {
  voice: { x: 0, y: 0 },
  chat: { x: 0, y: 0 },
  file: { x: 0, y: 0 },
  camera: { x: 0, y: 0 },
};

export const useMorphingIslandStore = create<MorphingIslandState>((set, get) => ({
  // Initial state
  dragOffsets: INITIAL_DRAG_OFFSETS,
  selectedMode: null,
  selectedModeCurrentPosition: null,
  isCollapsing: false,
  collapseProgress: 0,
  collapseComplete: false,
  collapseIslands: [],
  collapseIslandsCount: 0,

  // Actions
  setDragOffset: (mode, offset) =>
    set((state) => ({
      dragOffsets: { ...state.dragOffsets, [mode]: offset },
    })),

  resetDragOffsets: () =>
    set({
      dragOffsets: INITIAL_DRAG_OFFSETS,
    }),

  setSelectedMode: (mode, currentPosition) =>
    set({
      selectedMode: mode,
      selectedModeCurrentPosition: currentPosition,
    }),

  setCollapsing: (isCollapsing) =>
    set({ isCollapsing }),

  setCollapseProgress: (progress) =>
    set({ collapseProgress: progress }),

  setCollapseComplete: (complete) =>
    set({ collapseComplete: complete }),

  resetCollapse: () =>
    set({
      selectedMode: null,
      selectedModeCurrentPosition: null,
      isCollapsing: false,
      collapseProgress: 0,
      collapseComplete: false,
      collapseIslands: [],
      collapseIslandsCount: 0,
    }),

  // Calculate collapse order based on distance to selected island
  calculateCollapseOrder: () => {
    const state = get();
    const { selectedMode, dragOffsets } = state;

    if (!selectedMode) return;

    // Get selected island's current position
    const selectedPos = {
      x: ORIGINAL_POSITIONS[selectedMode].x + dragOffsets[selectedMode].x,
      y: ORIGINAL_POSITIONS[selectedMode].y + dragOffsets[selectedMode].y,
    };

    // Calculate distance for each non-selected island
    const allModes: ModeType[] = ['voice', 'chat', 'file', 'camera'];
    const islandsToCollapse: CollapseIsland[] = allModes
      .filter((mode) => mode !== selectedMode)
      .map((mode) => {
        const modePos = {
          x: ORIGINAL_POSITIONS[mode].x + dragOffsets[mode].x,
          y: ORIGINAL_POSITIONS[mode].y + dragOffsets[mode].y,
        };
        const distance = Math.sqrt(
          Math.pow(selectedPos.x - modePos.x, 2) +
          Math.pow(selectedPos.y - modePos.y, 2)
        );
        return { mode, distance, order: 0 };
      });

    // Sort by distance (closest first) and assign order
    islandsToCollapse.sort((a, b) => a.distance - b.distance);
    islandsToCollapse.forEach((island, index) => {
      island.order = index;
    });

    console.log('[Store] Collapse order (closest first):', islandsToCollapse.map(i => `${i.mode}(${i.distance.toFixed(0)}px)`).join(' → '));

    set({
      collapseIslands: islandsToCollapse,
      collapseIslandsCount: islandsToCollapse.length,
    });
  },

  // Getters for synchronous access
  getDragOffset: (mode) => get().dragOffsets[mode],

  getCurrentPosition: (mode) => {
    const offset = get().dragOffsets[mode];
    const original = ORIGINAL_POSITIONS[mode];
    return {
      x: original.x + offset.x,
      y: original.y + offset.y,
    };
  },

  getSelectedModeCurrentPosition: () => get().selectedModeCurrentPosition,

  getCollapseIsland: (mode) => get().collapseIslands.find((island) => island.mode === mode),
}));
