"use client";

import { useState } from "react";
import { Search, Plus, FileText, Trash2, Loader2, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8008";

interface SearchResult {
  id: string;
  content: string;
  score: number;
  metadata?: Record<string, unknown>;
}

interface IndexedDocument {
  content: string;
  timestamp: number;
}

export default function Home() {
  const [query, setQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [newDocument, setNewDocument] = useState("");
  const [isIndexing, setIsIndexing] = useState(false);
  const [indexedDocs, setIndexedDocs] = useState<IndexedDocument[]>([]);
  const [showAddDocument, setShowAddDocument] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setIsSearching(true);
    try {
      const response = await fetch(`${API_URL}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.results || []);
      }
    } catch (error) {
      console.error("Search failed:", error);
    } finally {
      setIsSearching(false);
    }
  };

  const handleAddDocument = async () => {
    if (!newDocument.trim()) return;

    setIsIndexing(true);
    try {
      const response = await fetch(`${API_URL}/documents`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: newDocument }),
      });

      if (response.ok) {
        const doc = await response.json();
        setIndexedDocs((prev) => [
          { content: doc.content, timestamp: Date.now() },
          ...prev,
        ]);
        setNewDocument("");
        setShowAddDocument(false);
      }
    } catch (error) {
      console.error("Failed to add document:", error);
    } finally {
      setIsIndexing(false);
    }
  };

  const handleDeleteDoc = (timestamp: number) => {
    setIndexedDocs((prev) => prev.filter((doc) => doc.timestamp !== timestamp));
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <div className="bg-primary text-primary-foreground p-3 rounded-xl">
              <Sparkles className="h-8 w-8" />
            </div>
          </div>
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
            Smart Search
          </h1>
          <p className="text-muted-foreground text-lg">
            Semantic search powered by vector embeddings
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Panel - Index Documents */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Documents
                </CardTitle>
                <CardDescription>Index documents for search</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button
                  onClick={() => setShowAddDocument(!showAddDocument)}
                  className="w-full gap-2"
                >
                  <Plus className="h-4 w-4" />
                  Add Document
                </Button>

                {showAddDocument && (
                  <div className="space-y-3 border rounded-lg p-4">
                    <Textarea
                      placeholder="Enter document content..."
                      value={newDocument}
                      onChange={(e) => setNewDocument(e.target.value)}
                      rows={6}
                    />
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        onClick={handleAddDocument}
                        disabled={isIndexing || !newDocument.trim()}
                        className="flex-1"
                      >
                        {isIndexing ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          "Index"
                        )}
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setShowAddDocument(false)}
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                )}

                <div className="space-y-2 max-h-[400px] overflow-y-auto">
                  {indexedDocs.length === 0 ? (
                    <p className="text-sm text-muted-foreground text-center py-8">
                      No documents indexed yet
                    </p>
                  ) : (
                    indexedDocs.map((doc, idx) => (
                      <div
                        key={doc.timestamp}
                        className="text-sm p-3 border rounded-lg bg-muted/30 group"
                      >
                        <p className="line-clamp-3 mb-2">{doc.content}</p>
                        <div className="flex justify-between items-center">
                          <span className="text-xs text-muted-foreground">
                            {new Date(doc.timestamp).toLocaleTimeString()}
                          </span>
                          <Button
                            size="icon"
                            variant="ghost"
                            className="h-6 w-6 opacity-0 group-hover:opacity-100"
                            onClick={() => handleDeleteDoc(doc.timestamp)}
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Panel - Search */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Search className="h-5 w-5" />
                  Search
                </CardTitle>
                <CardDescription>
                  Find similar documents using semantic search
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex gap-2">
                  <Input
                    placeholder="What are you looking for?"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                    className="flex-1"
                  />
                  <Button onClick={handleSearch} disabled={isSearching}>
                    {isSearching ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Search className="h-4 w-4" />
                    )}
                  </Button>
                </div>

                <div className="space-y-3">
                  {searchResults.length === 0 && !isSearching && query && (
                    <p className="text-center text-muted-foreground py-8">
                      No results found. Try adding more documents.
                    </p>
                  )}

                  {searchResults.map((result) => (
                    <div
                      key={result.id}
                      className="border rounded-lg p-4 bg-muted/30 hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <p className="text-sm flex-1">{result.content}</p>
                        <Badge variant="secondary">
                          {(result.score * 100).toFixed(0)}%
                        </Badge>
                      </div>
                      <div className="text-xs text-muted-foreground">
                        ID: {result.id.slice(0, 8)}
                      </div>
                    </div>
                  ))}

                  {searchResults.length === 0 && !query && (
                    <div className="text-center py-12 text-muted-foreground">
                      <Search className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>Enter a search query to find similar documents</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </main>
  );
}
