"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { Upload, FileText, Loader2, Sparkles, X, Download, Copy } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
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
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { formatFileSize } from "@/lib/utils";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8007";

interface Document {
  id: string;
  filename: string;
  size: number;
  status: "uploading" | "processing" | "ready" | "error";
  uploadProgress?: number;
  error?: string;
  summary?: string;
  tokenCount?: number;
  summaryType?: "short" | "medium" | "detailed";
}

type SummaryType = "short" | "medium" | "detailed";

export default function Home() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [summaryDialogOpen, setSummaryDialogOpen] = useState(false);
  const [currentDocument, setCurrentDocument] = useState<Document | null>(null);
  const [streamingSummary, setStreamingSummary] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [selectedSummaryType, setSelectedSummaryType] = useState<SummaryType>("medium");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files).filter(
      (file) => file.type === "application/pdf"
    );

    for (const file of files) {
      await uploadDocument(file);
    }
  }, []);

  const handleFileSelect = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    for (const file of Array.from(files)) {
      await uploadDocument(file);
    }

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }, []);

  const uploadDocument = async (file: File) => {
    const docId = Date.now().toString() + Math.random().toString(36).substr(2, 9);
    const newDoc: Document = {
      id: docId,
      filename: file.name,
      size: file.size,
      status: "uploading",
      uploadProgress: 0,
    };

    setDocuments((prev) => [...prev, newDoc]);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const xhr = new XMLHttpRequest();

      xhr.upload.addEventListener("progress", (e) => {
        if (e.lengthComputable) {
          const progress = Math.round((e.loaded / e.total) * 100);
          setDocuments((prev) =>
            prev.map((doc) =>
              doc.id === docId ? { ...doc, uploadProgress: progress } : doc
            )
          );
        }
      });

      xhr.addEventListener("load", () => {
        if (xhr.status === 200) {
          const response = JSON.parse(xhr.responseText);
          setDocuments((prev) =>
            prev.map((doc) =>
              doc.id === docId
                ? { ...doc, status: "ready", uploadProgress: 100 }
                : doc
            )
          );
        } else {
          throw new Error("Upload failed");
        }
      });

      xhr.addEventListener("error", () => {
        setDocuments((prev) =>
          prev.map((doc) =>
            doc.id === docId
              ? { ...doc, status: "error", error: "Upload failed" }
              : doc
          )
        );
      });

      xhr.open("POST", `${API_URL}/upload`);
      xhr.send(formData);
    } catch (error) {
      setDocuments((prev) =>
        prev.map((doc) =>
          doc.id === docId
            ? { ...doc, status: "error", error: "Upload failed" }
            : doc
        )
      );
    }
  };

  const generateSummary = async (docId: string) => {
    const doc = documents.find((d) => d.id === docId);
    if (!doc || doc.status !== "ready") return;

    setIsGenerating(true);
    setStreamingSummary("");
    setCurrentDocument(doc);
    setSummaryDialogOpen(true);

    try {
      const response = await fetch(`${API_URL}/summarize`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          document_id: docId,
          summary_type: selectedSummaryType,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate summary");
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error("No reader available");
      }

      let accumulatedSummary = "";

      while (true) {
        const { done, value } = await reader.read();

        if (done) break;

        const chunk = decoder.decode(value);
        accumulatedSummary += chunk;
        setStreamingSummary(accumulatedSummary);
      }

      // Update document with summary
      setDocuments((prev) =>
        prev.map((d) =>
          d.id === docId
            ? {
                ...d,
                summary: accumulatedSummary,
                tokenCount: accumulatedSummary.split(/\s+/).length,
                summaryType: selectedSummaryType,
              }
            : d
        )
      );
    } catch (error) {
      console.error("Error generating summary:", error);
      setStreamingSummary("Error generating summary. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  const deleteDocument = (docId: string) => {
    setDocuments((prev) => prev.filter((doc) => doc.id !== docId));
  };

  const openSummaryDialog = (doc: Document) => {
    setCurrentDocument(doc);
    setStreamingSummary(doc.summary || "");
    setSummaryDialogOpen(true);
  };

  const copySummary = () => {
    const textToCopy = streamingSummary;
    navigator.clipboard.writeText(textToCopy);
  };

  const downloadSummary = () => {
    if (!currentDocument) return;

    const content = streamingSummary;
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${currentDocument.filename.replace(".pdf", "")}_summary.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <div className="bg-primary text-primary-foreground p-3 rounded-xl">
              <FileText className="h-8 w-8" />
            </div>
          </div>
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
            PDF Summarizer
          </h1>
          <p className="text-muted-foreground text-lg">
            Upload your PDFs and get AI-powered summaries in seconds
          </p>
        </div>

        {/* Summary Type Selector */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg">Summary Settings</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <label className="text-sm font-medium whitespace-nowrap">
                Summary Type:
              </label>
              <Select value={selectedSummaryType} onValueChange={(v: any) => setSelectedSummaryType(v)}>
                <SelectTrigger className="w-full max-w-xs">
                  <SelectValue placeholder="Select summary type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="short">Short (2-3 sentences)</SelectItem>
                  <SelectItem value="medium">Medium (1 paragraph)</SelectItem>
                  <SelectItem value="detailed">Detailed (multiple paragraphs)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Upload Area */}
        <Card
          className={`mb-8 transition-all duration-200 ${
            isDragging
              ? "border-primary border-2 bg-primary/5"
              : "border-dashed border-2"
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <CardContent className="p-12">
            <div className="flex flex-col items-center justify-center text-center">
              <div className="bg-primary/10 p-4 rounded-full mb-4">
                <Upload className="h-8 w-8 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">
                Drop your PDF files here
              </h3>
              <p className="text-muted-foreground mb-6">
                or click to browse from your computer
              </p>
              <Button
                size="lg"
                onClick={() => fileInputRef.current?.click()}
                className="gap-2"
              >
                <Upload className="h-4 w-4" />
                Select PDF Files
              </Button>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,application/pdf"
                multiple
                className="hidden"
                onChange={handleFileSelect}
              />
              <p className="text-xs text-muted-foreground mt-4">
                Maximum file size: 10MB. Only PDF files are supported.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Documents List */}
        {documents.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-2xl font-semibold mb-4">Uploaded Documents</h2>
            {documents.map((doc) => (
              <Card key={doc.id} className="overflow-hidden">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-start gap-4 flex-1">
                      <div className="bg-red-100 dark:bg-red-900/20 p-3 rounded-lg">
                        <FileText className="h-6 w-6 text-red-600 dark:text-red-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-lg mb-1 truncate">
                          {doc.filename}
                        </h3>
                        <p className="text-sm text-muted-foreground mb-3">
                          {formatFileSize(doc.size)}
                        </p>

                        {/* Status Badge */}
                        <div className="flex items-center gap-2 mb-3">
                          {doc.status === "uploading" && (
                            <Badge variant="secondary">
                              <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                              Uploading {doc.uploadProgress}%
                            </Badge>
                          )}
                          {doc.status === "processing" && (
                            <Badge variant="secondary">
                              <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                              Processing
                            </Badge>
                          )}
                          {doc.status === "ready" && (
                            <Badge variant="success">Ready</Badge>
                          )}
                          {doc.status === "error" && (
                            <Badge variant="destructive">Error</Badge>
                          )}
                        </div>

                        {/* Upload Progress */}
                        {doc.status === "uploading" && (
                          <Progress value={doc.uploadProgress || 0} className="mb-3" />
                        )}

                        {/* Summary Info */}
                        {doc.summary && (
                          <div className="bg-muted/50 p-3 rounded-lg mb-3">
                            <div className="flex items-center gap-2 text-sm mb-2">
                              <Sparkles className="h-4 w-4 text-primary" />
                              <span className="font-medium">Summary Available</span>
                              <Badge variant="outline" className="ml-auto">
                                {doc.tokenCount} words
                              </Badge>
                              <Badge variant="outline">{doc.summaryType}</Badge>
                            </div>
                            <p className="text-sm text-muted-foreground line-clamp-2">
                              {doc.summary}
                            </p>
                          </div>
                        )}

                        {/* Actions */}
                        <div className="flex flex-wrap gap-2">
                          {doc.status === "ready" && !doc.summary && (
                            <Button
                              size="sm"
                              onClick={() => generateSummary(doc.id)}
                              disabled={isGenerating}
                              className="gap-2"
                            >
                              <Sparkles className="h-4 w-4" />
                              Generate Summary
                            </Button>
                          )}
                          {doc.summary && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => openSummaryDialog(doc)}
                              className="gap-2"
                            >
                              <FileText className="h-4 w-4" />
                              View Summary
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Delete Button */}
                    <Button
                      size="icon"
                      variant="ghost"
                      onClick={() => deleteDocument(doc.id)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Empty State */}
        {documents.length === 0 && (
          <Card className="text-center py-12">
            <CardContent>
              <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4 opacity-50" />
              <p className="text-muted-foreground">
                No documents uploaded yet. Upload a PDF to get started.
              </p>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Summary Dialog */}
      <Dialog open={summaryDialogOpen} onOpenChange={setSummaryDialogOpen}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-hidden flex flex-col">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              Summary
            </DialogTitle>
            <DialogDescription>
              {currentDocument?.filename} • {selectedSummaryType} summary
            </DialogDescription>
          </DialogHeader>

          <div className="flex-1 overflow-y-auto">
            {isGenerating ? (
              <div className="flex items-center justify-center py-8">
                <div className="text-center">
                  <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto mb-4" />
                  <p className="text-muted-foreground">Generating summary...</p>
                </div>
              </div>
            ) : (
              <div className="prose dark:prose-invert max-w-none">
                <div className={`type-writer-cursor ${isGenerating ? "" : ""}`}>
                  {streamingSummary.split("\n").map((paragraph, idx) => (
                    <p key={idx} className="mb-4">
                      {paragraph}
                    </p>
                  ))}
                </div>
                {streamingSummary && (
                  <div className="mt-6 pt-4 border-t">
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <span>Words: {streamingSummary.split(/\s+/).length}</span>
                      <span>Characters: {streamingSummary.length}</span>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="flex justify-end gap-2 pt-4 border-t">
            <Button variant="outline" onClick={copySummary} className="gap-2">
              <Copy className="h-4 w-4" />
              Copy
            </Button>
            <Button onClick={downloadSummary} className="gap-2">
              <Download className="h-4 w-4" />
              Download
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </main>
  );
}
