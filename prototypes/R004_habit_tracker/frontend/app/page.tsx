"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Flame, Plus, Check, Calendar, Trash2 } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8004";

// Types
interface Habit {
  id: string;
  name: string;
  description: string;
  frequency: "daily" | "weekly";
  streak: number;
  created_at: string;
  last_completed?: string;
}

interface Completion {
  id: string;
  habit_id: string;
  completed_at: string;
}

export default function Home() {
  const [habits, setHabits] = useState<Habit[]>([]);
  const [completions, setCompletions] = useState<Completion[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    frequency: "daily" as "daily" | "weekly",
  });

  // Fetch habits and completions on mount
  useEffect(() => {
    fetchHabits();
    fetchCompletions();
  }, []);

  const fetchHabits = async () => {
    try {
      const response = await fetch(`${API_URL}/habits`);
      if (response.ok) {
        const data = await response.json();
        setHabits(data);
      }
    } catch (error) {
      console.error("Failed to fetch habits:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchCompletions = async () => {
    try {
      const response = await fetch(`${API_URL}/completions`);
      if (response.ok) {
        const data = await response.json();
        setCompletions(data);
      }
    } catch (error) {
      console.error("Failed to fetch completions:", error);
    }
  };

  const createHabit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim()) return;

    try {
      const response = await fetch(`${API_URL}/habits`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const newHabit = await response.json();
        setHabits([...habits, newHabit]);
        setFormData({ name: "", description: "", frequency: "daily" });
        setShowCreateForm(false);
      }
    } catch (error) {
      console.error("Failed to create habit:", error);
    }
  };

  const completeHabit = async (habitId: string) => {
    try {
      const response = await fetch(`${API_URL}/habits/${habitId}/complete`, {
        method: "POST",
      });

      if (response.ok) {
        const completion = await response.json();
        setCompletions([...completions, completion]);

        // Update habit streak and last_completed
        setHabits(habits.map(habit => {
          if (habit.id === habitId) {
            return {
              ...habit,
              streak: habit.streak + 1,
              last_completed: completion.completed_at,
            };
          }
          return habit;
        }));
      }
    } catch (error) {
      console.error("Failed to complete habit:", error);
    }
  };

  const deleteHabit = async (habitId: string) => {
    try {
      const response = await fetch(`${API_URL}/habits/${habitId}`, {
        method: "DELETE",
      });

      if (response.ok) {
        setHabits(habits.filter(h => h.id !== habitId));
      }
    } catch (error) {
      console.error("Failed to delete habit:", error);
    }
  };

  const isCompletedToday = (habitId: string): boolean => {
    const today = new Date().toISOString().split("T")[0];
    return completions.some(
      c => c.habit_id === habitId && c.completed_at.startsWith(today)
    );
  };

  const getHabitCompletions = (habitId: string): Completion[] => {
    return completions.filter(c => c.habit_id === habitId);
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  const getStreakColor = (streak: number): string => {
    if (streak === 0) return "default";
    if (streak < 7) return "secondary";
    if (streak < 14) return "warning";
    return "success";
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900 dark:text-white mb-2">
            {process.env.NEXT_PUBLIC_APP_NAME || "Habit Tracker"}
          </h1>
          <p className="text-slate-600 dark:text-slate-400">
            Build better habits, one day at a time
          </p>
        </div>

        {/* Create Habit Section */}
        <Card className="mb-8 border-2 border-slate-200 dark:border-slate-700">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Create New Habit</CardTitle>
                <CardDescription>Start tracking a new habit today</CardDescription>
              </div>
              <Button
                onClick={() => setShowCreateForm(!showCreateForm)}
                variant={showCreateForm ? "outline" : "default"}
              >
                {showCreateForm ? "Cancel" : <><Plus className="mr-2 h-4 w-4" /> New Habit</>}
              </Button>
            </div>
          </CardHeader>
          {showCreateForm && (
            <CardContent>
              <form onSubmit={createHabit} className="space-y-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Habit Name</label>
                  <Input
                    placeholder="e.g., Morning meditation"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Description</label>
                  <Textarea
                    placeholder="Describe your habit goal..."
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    rows={3}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Frequency</label>
                  <div className="flex gap-2">
                    <Button
                      type="button"
                      variant={formData.frequency === "daily" ? "default" : "outline"}
                      onClick={() => setFormData({ ...formData, frequency: "daily" })}
                    >
                      Daily
                    </Button>
                    <Button
                      type="button"
                      variant={formData.frequency === "weekly" ? "default" : "outline"}
                      onClick={() => setFormData({ ...formData, frequency: "weekly" })}
                    >
                      Weekly
                    </Button>
                  </div>
                </div>
                <Button type="submit" className="w-full">
                  Create Habit
                </Button>
              </form>
            </CardContent>
          )}
        </Card>

        {/* Habits List */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-semibold text-slate-900 dark:text-white">
              Your Habits
            </h2>
            <Badge variant="secondary" className="text-sm">
              {habits.length} {habits.length === 1 ? "habit" : "habits"}
            </Badge>
          </div>

          {isLoading ? (
            <div className="text-center py-12 text-slate-500">
              Loading habits...
            </div>
          ) : habits.length === 0 ? (
            <Card className="border-dashed border-2 border-slate-300 dark:border-slate-600">
              <CardContent className="py-12 text-center">
                <p className="text-slate-500 dark:text-slate-400 mb-4">
                  No habits yet. Create your first habit to get started!
                </p>
                <Button onClick={() => setShowCreateForm(true)}>
                  <Plus className="mr-2 h-4 w-4" /> Create Habit
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {habits.map((habit) => {
                const completedToday = isCompletedToday(habit.id);
                const habitCompletions = getHabitCompletions(habit.id);
                const streakColor = getStreakColor(habit.streak);

                return (
                  <Card
                    key={habit.id}
                    className={`transition-all hover:shadow-lg ${
                      completedToday ? "border-green-500 dark:border-green-400" : ""
                    }`}
                  >
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <CardTitle className="text-lg">{habit.name}</CardTitle>
                          <CardDescription className="mt-1">
                            {habit.description || "No description"}
                          </CardDescription>
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => deleteHabit(habit.id)}
                          className="h-8 w-8 text-slate-400 hover:text-destructive"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {/* Streak Badge */}
                      <div className="flex items-center justify-between">
                        <Badge variant={streakColor as any} className="text-sm">
                          <Flame className="mr-1 h-3 w-3" />
                          {habit.streak} day streak
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          {habit.frequency}
                        </Badge>
                      </div>

                      {/* Last Completion */}
                      {habit.last_completed && (
                        <div className="flex items-center text-sm text-slate-600 dark:text-slate-400">
                          <Calendar className="mr-2 h-4 w-4" />
                          Last: {formatDate(habit.last_completed)}
                        </div>
                      )}

                      {/* Completion Button */}
                      <Button
                        onClick={() => completeHabit(habit.id)}
                        disabled={completedToday}
                        className={`w-full ${
                          completedToday
                            ? "bg-green-500 hover:bg-green-600"
                            : ""
                        }`}
                      >
                        {completedToday ? (
                          <>
                            <Check className="mr-2 h-4 w-4" /> Completed Today
                          </>
                        ) : (
                          <>
                            <Check className="mr-2 h-4 w-4" /> Mark Complete
                          </>
                        )}
                      </Button>

                      {/* Completion History Progress */}
                      {habitCompletions.length > 0 && (
                        <div className="space-y-2">
                          <div className="flex items-center justify-between text-xs text-slate-600 dark:text-slate-400">
                            <span>Progress</span>
                            <span>{habitCompletions.length} completions</span>
                          </div>
                          <Progress value={Math.min(habit.streak * 5, 100)} className="h-2" />
                        </div>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </div>

        {/* Completion History Section */}
        {completions.length > 0 && (
          <Card className="mt-8">
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>Your latest habit completions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {completions
                  .sort((a, b) => new Date(b.completed_at).getTime() - new Date(a.completed_at).getTime())
                  .slice(0, 10)
                  .map((completion) => {
                    const habit = habits.find(h => h.id === completion.habit_id);
                    return (
                      <div
                        key={completion.id}
                        className="flex items-center justify-between py-2 px-3 rounded-lg bg-slate-50 dark:bg-slate-800"
                      >
                        <span className="font-medium">
                          {habit?.name || "Unknown habit"}
                        </span>
                        <span className="text-sm text-slate-600 dark:text-slate-400">
                          {formatDate(completion.completed_at)}
                        </span>
                      </div>
                    );
                  })}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </main>
  );
}
