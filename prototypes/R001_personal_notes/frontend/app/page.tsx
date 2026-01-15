"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface Note {
  id: number;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
}

export default function HomePage() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [noteTitle, setNoteTitle] = useState("");
  const [noteContent, setNoteContent] = useState("");
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState<string>("checking...");

  // Edit dialog state
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingNote, setEditingNote] = useState<Note | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [editContent, setEditContent] = useState("");

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";
  const appName = process.env.NEXT_PUBLIC_APP_NAME || "Personal Notes";

  // Fetch health status
  useEffect(() => {
    fetch(`${apiUrl}/health`)
      .then((res) => res.json())
      .then((data) => setHealth(data.status))
      .catch(() => setHealth("disconnected"));
  }, [apiUrl]);

  // Fetch notes on mount
  useEffect(() => {
    fetchNotes();
  }, []);

  // Fetch notes from API
  const fetchNotes = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${apiUrl}/api/v1/notes`);
      const data = await res.json();
      setNotes(data.notes || []);
    } catch (error) {
      console.error("Failed to fetch notes:", error);
    }
    setLoading(false);
  };

  // Create note
  const createNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!noteTitle.trim() || !noteContent.trim()) return;

    try {
      const res = await fetch(`${apiUrl}/api/v1/notes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: noteTitle,
          content: noteContent,
        }),
      });
      const newNote = await res.json();
      setNotes([newNote, ...notes]);
      setNoteTitle("");
      setNoteContent("");
    } catch (error) {
      console.error("Failed to create note:", error);
    }
  };

  // Delete note
  const deleteNote = async (id: number) => {
    try {
      await fetch(`${apiUrl}/api/v1/notes/${id}`, {
        method: "DELETE",
      });
      setNotes(notes.filter((note) => note.id !== id));
    } catch (error) {
      console.error("Failed to delete note:", error);
    }
  };

  // Open edit dialog
  const openEditDialog = (note: Note) => {
    setEditingNote(note);
    setEditTitle(note.title);
    setEditContent(note.content);
    setEditDialogOpen(true);
  };

  // Update note
  const updateNote = async () => {
    if (!editingNote || !editTitle.trim() || !editContent.trim()) return;

    try {
      const res = await fetch(`${apiUrl}/api/v1/notes/${editingNote.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: editTitle,
          content: editContent,
        }),
      });
      const updatedNote = await res.json();
      setNotes(notes.map((n) => (n.id === editingNote.id ? updatedNote : n)));
      setEditDialogOpen(false);
      setEditingNote(null);
    } catch (error) {
      console.error("Failed to update note:", error);
    }
  };

  // Format date for display
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
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
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Create Note Form */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle>New Note</CardTitle>
              <CardDescription>Create a new note</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={createNote} className="space-y-4">
                <div>
                  <Input
                    placeholder="Note title"
                    value={noteTitle}
                    onChange={(e) => setNoteTitle(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <Textarea
                    placeholder="Write your note here..."
                    value={noteContent}
                    onChange={(e) => setNoteContent(e.target.value)}
                    required
                    rows={6}
                  />
                </div>
                <Button type="submit" className="w-full">
                  Create Note
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Notes List */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Notes ({notes.length})</CardTitle>
              <CardDescription>
                <Button variant="outline" size="sm" onClick={fetchNotes} disabled={loading}>
                  {loading ? "Loading..." : "Refresh"}
                </Button>
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 max-h-[600px] overflow-y-auto">
                {notes.length === 0 ? (
                  <p className="text-sm text-muted-foreground text-center py-8">
                    No notes yet. Create one to get started.
                  </p>
                ) : (
                  notes.map((note) => (
                    <div
                      key={note.id}
                      className="group p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          <h3 className="font-semibold text-lg truncate">{note.title}</h3>
                          <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                            {note.content}
                          </p>
                          <p className="text-xs text-muted-foreground mt-2">
                            Created: {formatDate(note.created_at)}
                            {note.updated_at !== note.created_at && (
                              <span> • Updated: {formatDate(note.updated_at)}</span>
                            )}
                          </p>
                        </div>
                        <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => openEditDialog(note)}
                          >
                            Edit
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => deleteNote(note.id)}
                            className="text-destructive hover:text-destructive"
                          >
                            Delete
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </main>

      {/* Edit Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Edit Note</DialogTitle>
            <DialogDescription>
              Make changes to your note. Click save when you're done.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Input
                placeholder="Note title"
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                required
              />
            </div>
            <div>
              <Textarea
                placeholder="Write your note here..."
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                required
                rows={8}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={updateNote}>Save Changes</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
