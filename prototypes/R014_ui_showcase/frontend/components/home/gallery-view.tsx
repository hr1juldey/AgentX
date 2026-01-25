"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { DirectWidgetRenderer } from "@/components/widgets/direct-widget-renderer";
import type { UIDescriptor } from "@/types/widget-types";

// No-op function for gallery widgets (not dismissible)
const NOOP_FN = () => {};

/**
 * Gallery widget descriptors - example content for all widget types
 * Showcased in the Widget Gallery view
 */
const galleryDescriptors: UIDescriptor[] = [
  {
    descriptor_id: "gallery-markdown",
    descriptor_type: "markdown",
    title: "Markdown Widget",
    content: `# Markdown Heading

This is a **markdown block** widget that supports:

- **Bold** and *italic* text
- Lists (ordered and unordered)
- [Links](https://example.com)
- \`inline code\` and code blocks

\`\`\`javascript
const greeting = "Hello, World!";
console.log(greeting);
\`\`\`

> Blockquotes are also supported

This widget is perfect for displaying AI-generated explanations, documentation, and formatted text.`,
  },
  {
    descriptor_id: "gallery-card",
    descriptor_type: "card",
    title: "Travel Tips: Japan",
    content: "### Best Time to Visit\n\nSpring (March-May) for cherry blossoms or Autumn (November) for fall colors.\n\n### Must-Visit Places\n- Tokyo (modern culture)\n- Kyoto (temples and traditions)\n- Osaka (food capital)\n\n### Travel Tips\n- Get a JR Pass for unlimited train travel\n- Learn basic Japanese phrases\n- Cash is still king in many places",
    metadata: {
      actions: [
        { label: "View Details", action: "view-details" },
        { label: "Book Now", action: "book-now" },
      ],
    },
  },
  {
    descriptor_id: "gallery-form",
    descriptor_type: "form",
    title: "User Feedback Form",
    fields: [
      { name: "name", type: "text", label: "Your Name", required: true },
      { name: "email", type: "email", label: "Email Address", required: true },
      { name: "feedback", type: "textarea", label: "Your Feedback", required: false },
      { name: "rating", type: "select", label: "Rating", required: false, options: ["Excellent", "Good", "Fair", "Poor"] },
    ],
    submit_button_text: "Submit Feedback",
  },
  {
    descriptor_id: "gallery-progress",
    descriptor_type: "progress",
    title: "Processing Documents",
    progress_percent: 65,
    status_text: "15 of 23 documents processed",
  },
  {
    descriptor_id: "gallery-action",
    descriptor_type: "action",
    title: "Start Analysis",
    content: "Click to begin processing your data",
    button_text: "Start New Analysis",
  },
  {
    descriptor_id: "gallery-confirmation",
    descriptor_type: "confirmation",
    title: "Delete Document",
    message: "Are you sure you want to delete this document? This action cannot be undone.",
    confirm_label: "Delete",
    cancel_label: "Cancel",
  },
  {
    descriptor_id: "gallery-image",
    descriptor_type: "image",
    title: "Mountain Landscape",
    content: "A beautiful mountain landscape showcasing nature's grandeur",
    metadata: {
      caption: "Photo from Picsum Photos",
    },
  },
  {
    descriptor_id: "gallery-gallery",
    descriptor_type: "gallery",
    title: "Nature Collection",
    content: "A curated gallery of stunning nature photographs",
  },
  {
    descriptor_id: "gallery-chart",
    descriptor_type: "chart",
    title: "Monthly Sales Data",
    content: "Revenue trends over the past 6 months showing consistent growth",
    metadata: {
      chartType: "bar",
    },
  },
];

/**
 * GalleryView - Showcases all generative UI widget types with example content
 */
export function GalleryView() {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Widget Gallery</CardTitle>
          <CardDescription>
            All generative UI widget types showcased with example content
          </CardDescription>
        </CardHeader>
      </Card>

      {galleryDescriptors.map((descriptor) => (
        <DirectWidgetRenderer
          key={descriptor.descriptor_id}
          descriptor={descriptor}
          onDismiss={NOOP_FN}
          dragPosition={undefined}
          onDragEnd={NOOP_FN}
          disableDrag
        />
      ))}
    </div>
  );
}
