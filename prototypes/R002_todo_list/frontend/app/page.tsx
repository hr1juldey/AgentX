"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Trash2, Edit2, Plus, Calendar } from "lucide-react";

type Priority = "low" | "medium" | "high";
type Status = "todo" | "in_progress" | "done";

interface Todo {
  id: number;
  title: string;
  description: string;
  due_date: string | null;
  priority: Priority;
  status: Status;
  created_at: string;
  updated_at: string;
}

const PRIORITY_COLORS: Record<Priority, string> = {
  low: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100",
  medium: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100",
  high: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100",
};

const STATUS_LABELS: Record<Status, string> = {
  todo: "Todo",
  in_progress: "In Progress",
  done: "Done",
};

export default function HomePage() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState<string>("checking...");

  // Create form state
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [priority, setPriority] = useState<Priority>("medium");

  // Edit dialog state
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingTodo, setEditingTodo] = useState<Todo | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [editDueDate, setEditDueDate] = useState("");
  const [editPriority, setEditPriority] = useState<Priority>("medium");

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";
  const appName = process.env.NEXT_PUBLIC_APP_NAME || "Todo List";

  // Fetch health status
  useEffect(() => {
    fetch(`${apiUrl}/health`)
      .then((res) => res.json())
      .then((data) => setHealth(data.status))
      .catch(() => setHealth("disconnected"));
  }, [apiUrl]);

  // Fetch todos on mount
  useEffect(() => {
    fetchTodos();
  }, []);

  // Fetch todos from API
  const fetchTodos = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${apiUrl}/api/v1/todos`);
      const data = await res.json();
      setTodos(data.todos || []);
    } catch (error) {
      console.error("Failed to fetch todos:", error);
    }
    setLoading(false);
  };

  // Create todo
  const createTodo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    try {
      const res = await fetch(`${apiUrl}/api/v1/todos`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title,
          description,
          due_date: dueDate || null,
          priority,
        }),
      });
      const newTodo = await res.json();
      setTodos([newTodo, ...todos]);
      setTitle("");
      setDescription("");
      setDueDate("");
      setPriority("medium");
    } catch (error) {
      console.error("Failed to create todo:", error);
    }
  };

  // Delete todo
  const deleteTodo = async (id: number) => {
    try {
      await fetch(`${apiUrl}/api/v1/todos/${id}`, {
        method: "DELETE",
      });
      setTodos(todos.filter((todo) => todo.id !== id));
    } catch (error) {
      console.error("Failed to delete todo:", error);
    }
  };

  // Update todo status
  const updateStatus = async (todo: Todo, newStatus: Status) => {
    try {
      const res = await fetch(`${apiUrl}/api/v1/todos/${todo.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: todo.title,
          description: todo.description,
          due_date: todo.due_date,
          priority: todo.priority,
          status: newStatus,
        }),
      });
      const updatedTodo = await res.json();
      setTodos(todos.map((t) => (t.id === todo.id ? updatedTodo : t)));
    } catch (error) {
      console.error("Failed to update todo status:", error);
    }
  };

  // Open edit dialog
  const openEditDialog = (todo: Todo) => {
    setEditingTodo(todo);
    setEditTitle(todo.title);
    setEditDescription(todo.description);
    setEditDueDate(todo.due_date || "");
    setEditPriority(todo.priority);
    setEditDialogOpen(true);
  };

  // Update todo
  const updateTodo = async () => {
    if (!editingTodo || !editTitle.trim()) return;

    try {
      const res = await fetch(`${apiUrl}/api/v1/todos/${editingTodo.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: editTitle,
          description: editDescription,
          due_date: editDueDate || null,
          priority: editPriority,
          status: editingTodo.status,
        }),
      });
      const updatedTodo = await res.json();
      setTodos(todos.map((t) => (t.id === editingTodo.id ? updatedTodo : t)));
      setEditDialogOpen(false);
      setEditingTodo(null);
    } catch (error) {
      console.error("Failed to update todo:", error);
    }
  };

  // Format date for display
  const formatDate = (dateString: string | null) => {
    if (!dateString) return null;
    return new Date(dateString).toLocaleDateString();
  };

  // Filter todos by status
  const todosByStatus = (status: Status) => {
    return todos.filter((todo) => todo.status === status);
  };

  // Render todo card
  const renderTodoCard = (todo: Todo) => (
    <div
      key={todo.id}
      className="group p-4 bg-background border rounded-lg hover:shadow-md transition-all"
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <h4 className="font-semibold text-base flex-1">{todo.title}</h4>
        <div className="flex gap-1">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={() => openEditDialog(todo)}
          >
            <Edit2 className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-destructive hover:text-destructive"
            onClick={() => deleteTodo(todo.id)}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>
      {todo.description && (
        <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
          {todo.description}
        </p>
      )}
      <div className="flex items-center gap-2 flex-wrap">
        <Badge className={PRIORITY_COLORS[todo.priority]}>
          {todo.priority}
        </Badge>
        {todo.due_date && (
          <div className="flex items-center gap-1 text-xs text-muted-foreground">
            <Calendar className="h-3 w-3" />
            {formatDate(todo.due_date)}
          </div>
        )}
      </div>
      {/* Move buttons for quick status change */}
      <div className="flex gap-2 mt-3 pt-3 border-t">
        {todo.status !== "todo" && (
          <Button
            variant="outline"
            size="sm"
            className="text-xs flex-1"
            onClick={() => updateStatus(todo, "todo")}
          >
            ← Todo
          </Button>
        )}
        {todo.status === "todo" && (
          <Button
            variant="outline"
            size="sm"
            className="text-xs flex-1"
            onClick={() => updateStatus(todo, "in_progress")}
          >
            → In Progress
          </Button>
        )}
        {todo.status === "in_progress" && (
          <>
            <Button
              variant="outline"
              size="sm"
              className="text-xs flex-1"
              onClick={() => updateStatus(todo, "todo")}
            >
              ← Todo
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="text-xs flex-1"
              onClick={() => updateStatus(todo, "done")}
            >
              → Done
            </Button>
          </>
        )}
        {todo.status === "done" && (
          <Button
            variant="outline"
            size="sm"
            className="text-xs flex-1"
            onClick={() => updateStatus(todo, "in_progress")}
          >
            ← In Progress
          </Button>
        )}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold">{appName}</h1>
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">Backend:</span>
              <span
                className={`px-2 py-1 rounded text-xs font-medium ${
                  health === "healthy"
                    ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100"
                    : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100"
                }`}
              >
                {health}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="grid gap-6 lg:grid-cols-4">
          {/* Create Todo Form */}
          <Card className="lg:col-span-1 h-fit">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Plus className="h-5 w-5" />
                New Todo
              </CardTitle>
              <CardDescription>Create a new todo item</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={createTodo} className="space-y-4">
                <div>
                  <Input
                    placeholder="Todo title"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <Textarea
                    placeholder="Description (optional)"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    rows={3}
                  />
                </div>
                <div>
                  <Input
                    type="date"
                    value={dueDate}
                    onChange={(e) => setDueDate(e.target.value)}
                  />
                </div>
                <div>
                  <Select value={priority} onValueChange={(v: Priority) => setPriority(v)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Priority" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button type="submit" className="w-full">
                  Create Todo
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Kanban Board */}
          <div className="lg:col-span-3 grid grid-cols-1 md:grid-cols-3 gap-4">
            {(["todo", "in_progress", "done"] as Status[]).map((status) => (
              <Card key={status} className="h-fit">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg">
                    {STATUS_LABELS[status]}
                    <Badge variant="secondary" className="ml-2">
                      {todosByStatus(status).length}
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 max-h-[600px] overflow-y-auto">
                    {todosByStatus(status).length === 0 ? (
                      <p className="text-sm text-muted-foreground text-center py-4">
                        No todos
                      </p>
                    ) : (
                      todosByStatus(status).map((todo) => renderTodoCard(todo))
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </main>

      {/* Edit Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Edit Todo</DialogTitle>
            <DialogDescription>
              Make changes to your todo. Click save when you're done.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Input
                placeholder="Todo title"
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                required
              />
            </div>
            <div>
              <Textarea
                placeholder="Description"
                value={editDescription}
                onChange={(e) => setEditDescription(e.target.value)}
                rows={4}
              />
            </div>
            <div>
              <Input
                type="date"
                value={editDueDate}
                onChange={(e) => setEditDueDate(e.target.value)}
              />
            </div>
            <div>
              <Select value={editPriority} onValueChange={(v: Priority) => setEditPriority(v)}>
                <SelectTrigger>
                  <SelectValue placeholder="Priority" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={updateTodo}>Save Changes</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
