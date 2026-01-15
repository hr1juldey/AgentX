"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

interface Item {
  id: number;
  name: string;
  description?: string;
  created_at: string;
}

export default function HomePage() {
  const [items, setItems] = useState<Item[]>([]);
  const [itemName, setItemName] = useState("");
  const [itemDescription, setItemDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState<string>("checking...");

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";
  const appName = process.env.NEXT_PUBLIC_APP_NAME || "Prototype";

  // Fetch health status
  useEffect(() => {
    fetch(`${apiUrl}/health`)
      .then((res) => res.json())
      .then((data) => setHealth(data.status))
      .catch(() => setHealth("disconnected"));
  }, [apiUrl]);

  // Fetch items
  const fetchItems = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${apiUrl}/api/v1/items`);
      const data = await res.json();
      setItems(data);
    } catch (error) {
      console.error("Failed to fetch items:", error);
    }
    setLoading(false);
  };

  // Create item
  const createItem = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!itemName.trim()) return;

    try {
      const res = await fetch(`${apiUrl}/api/v1/items`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: itemName,
          description: itemDescription || undefined,
        }),
      });
      const newItem = await res.json();
      setItems([newItem, ...items]);
      setItemName("");
      setItemDescription("");
    } catch (error) {
      console.error("Failed to create item:", error);
    }
  };

  // Delete item
  const deleteItem = async (id: number) => {
    try {
      await fetch(`${apiUrl}/api/v1/items/${id}`, {
        method: "DELETE",
      });
      setItems(items.filter((item) => item.id !== id));
    } catch (error) {
      console.error("Failed to delete item:", error);
    }
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
                    ? "bg-green-100 text-green-800"
                    : "bg-red-100 text-red-800"
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
        <div className="grid gap-6 md:grid-cols-2">
          {/* Create Item Form */}
          <Card>
            <CardHeader>
              <CardTitle>Create Item</CardTitle>
              <CardDescription>Add a new item to the list</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={createItem} className="space-y-4">
                <div>
                  <Input
                    placeholder="Item name"
                    value={itemName}
                    onChange={(e) => setItemName(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <Input
                    placeholder="Description (optional)"
                    value={itemDescription}
                    onChange={(e) => setItemDescription(e.target.value)}
                  />
                </div>
                <Button type="submit" className="w-full">
                  Create Item
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Items List */}
          <Card>
            <CardHeader>
              <CardTitle>Items ({items.length})</CardTitle>
              <CardDescription>
                <Button variant="outline" size="sm" onClick={fetchItems} disabled={loading}>
                  {loading ? "Loading..." : "Refresh"}
                </Button>
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {items.length === 0 ? (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    No items yet. Create one to get started.
                  </p>
                ) : (
                  items.map((item) => (
                    <div
                      key={item.id}
                      className="flex items-start justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex-1">
                        <h3 className="font-medium">{item.name}</h3>
                        {item.description && (
                          <p className="text-sm text-muted-foreground">{item.description}</p>
                        )}
                        <p className="text-xs text-muted-foreground mt-1">ID: {item.id}</p>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => deleteItem(item.id)}
                        className="text-destructive hover:text-destructive"
                      >
                        Delete
                      </Button>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
