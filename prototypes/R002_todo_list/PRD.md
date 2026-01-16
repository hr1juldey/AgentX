# R002 Todo List - Product Requirements Document

## Overview

A Kanban-style todo management application with priority tracking and due dates.

## User Story

As a user, I want to organize my tasks into a Kanban board with priorities and due dates, so that I can track my work more effectively.

## Features

### Core Features
1. **Create todos** with title, description, due date, and priority
2. **Kanban board** with 3 columns: Todo, In Progress, Done
3. **Priority levels**: Low (green), Medium (yellow), High (red)
4. **Move todos** between columns with quick action buttons
5. **Edit todos** via modal dialog
6. **Delete todos** with confirmation
7. **Filter todos** by status and priority

### Backend API (FastAPI)
- Port: 8002
- Endpoints:
  - POST /api/v1/todos - Create todo
  - GET /api/v1/todos - List todos (with ?status= and ?priority= filters)
  - GET /api/v1/todos/{id} - Get single todo
  - PUT /api/v1/todos/{id} - Update todo
  - DELETE /api/v1/todos/{id} - Delete todo

### Frontend (Next.js + shadcn/ui)
- Port: 3000 (same as R001)
- Kanban board layout with 3 columns
- Create todo form in sidebar
- Priority badges with color coding
- Due date picker and display
- Edit dialog modal
- Backend health indicator

## Data Model

### Todo Object
```typescript
{
  id: number
  title: string
  description: string | null
  due_date: string | null  // ISO datetime
  priority: "low" | "medium" | "high"
  status: "todo" | "in_progress" | "done"
  created_at: string  // ISO datetime
  updated_at: string  // ISO datetime
}
```

## Success Criteria

- [x] Users can create todos with all attributes
- [x] Users can view todos in Kanban columns
- [x] Users can move todos between columns
- [x] Priority badges display with correct colors
- [x] Due dates display correctly
- [x] Edit and delete functionality works
- [ ] Backend tests pass (16 tests)
- [ ] Frontend builds without errors
- [ ] Integration works end-to-end

## Level 1 Status

**Prototype Time**: ~1.5 hours
**Difficulty**: Basic CRUD + Kanban UI
**Status**: Complete (pending integration testing)
