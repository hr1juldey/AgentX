# Computer Vision Integration Guide

## Overview

Computer vision enables AGENTX to see and understand visual content, including images, screenshots, documents, video streams, and real-world environments through camera input.

## Use Cases

### 1. Document Analysis
- Extract text from PDFs, images, screenshots
- Parse tables, charts, graphs
- Understand document structure

### 2. UI/UX Analysis
- Analyze interface screenshots
- Detect accessibility issues
- Provide design feedback

### 3. Real-World Understanding
- Object detection and recognition
- Scene understanding
- Image captioning and description

### 4. Video Processing
- Frame-by-frame analysis
- Action recognition
- Temporal reasoning

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Input     │────▶│   Vision    │────▶│   AgentX    │
│  (Image)    │     │   Model     │     │   Core      │
└─────────────┘     └─────────────┘     └─────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │  Embedded   │
                     │  Vectors    │
                     └─────────────┘
```

## Technology Choices

### Vision Models

| Model | Type | Size | Best For |
|-------|------|------|----------|
| LLaVA | Multimodal LLM | 7B/13B | General understanding |
| Fuyu-8B | Native multimodal | 8B | UI/Screen analysis |
| CLIP | Image-text | ~400M | Similarity search |
| ColPali | Late interaction | - | Document retrieval |
| YOLO | Object detection | Various | Real-time detection |

### Deployment Options

- **Ollama** - Local LLaVA, LLaVA-NeXt
- **Transformers** - Direct model loading
- **vLLM** - Fast inference
- **APIs** - OpenAI GPT-4V, Claude 3.5 Sonnet

## Implementation

### 1. Ollama Vision Model Setup

```python
# plugins/vision_ollama.py
import base64
from typing import List, Dict
import dspy

class OllamaVision:
    """Vision using Ollama multimodal models."""

    def __init__(
        self,
        model: str = "llava:latest",
        api_base: str = "http://localhost:11434"
    ):
        self.model = model
        self.api_base = api_base

    def encode_image(self, image_path: str) -> str:
        """Encode image to base64."""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    def analyze(
        self,
        image_path: str,
        prompt: str = "Describe this image in detail."
    ) -> str:
        """Analyze image with vision model."""
        import requests

        image_base64 = self.encode_image(image_path)

        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": [image_base64],
            "stream": False
        }

        response = requests.post(
            f"{self.api_base}/api/generate",
            json=payload,
            timeout=60
        )

        result = response.json()
        return result.get("response", "")

    def chat(
        self,
        image_path: str,
        message: str,
        history: List[Dict] = None
    ) -> str:
        """Chat with image context."""
        import requests

        image_base64 = self.encode_image(image_path)

        payload = {
            "model": self.model,
            "prompt": message,
            "images": [image_base64],
            "stream": False
        }

        if history:
            payload["context"] = history

        response = requests.post(
            f"{self.api_base}/api/chat",
            json=payload,
            timeout=60
        )

        result = response.json()
        return result.get("message", {}).get("content", "")
```

### 2. DSPy Integration

```python
# core/vision_tools.py
import dspy
from typing import List

class AnalyzeImage(dspy.Signature):
    """Image analysis signature."""
    image_description: str = dspy.InputField(desc="Visual content")
    question: str = dspy.InputField(desc="What to analyze")
    analysis: str = dspy.OutputField(desc="Detailed answer")


class VisionAgent(dspy.Module):
    """Agent with vision capabilities."""

    def __init__(self, vision_model: OllamaVision):
        super().__init__()
        self.vision = vision_model

        # Create analyzer
        self.analyzer = dspy.Predict(AnalyzeImage)

    def forward(
        self,
        image_path: str,
        question: str
    ) -> str:
        """Analyze image and answer question."""
        # First, get image description
        description = self.vision.analyze(
            image_path,
            "Provide a detailed visual description of this image."
        )

        # Then, answer question using DSPy
        result = self.analyzer(
            image_description=description,
            question=question
        )

        return result.analysis
```

### 3. Document Analysis with ColPali

```python
# plugins/document_vision.py
from fastembed import LateInteractionMultimodalEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from PIL import Image
import io

class DocumentVisionRetriever:
    """Document retrieval using ColPali."""

    def __init__(self):
        # Initialize ColPali
        self.model = LateInteractionMultimodalEmbedding(
            model_name="vidore/colpali-v1.3"
        )

        # Initialize Qdrant
        self.client = QdrantClient(url="http://localhost:6333")

        # Create collection
        self.client.create_collection(
            collection_name="documents",
            vectors_config=models.VectorParams(
                size=128,  # ColPali dimension
                distance=models.Distance.COSINE,
                multivector_config=models.MultiVectorConfig(
                    comparator=models.MultiVectorComparator.MAX_SIM
                )
            )
        )

    def index_document(
        self,
        pdf_path: str,
        doc_id: str,
        metadata: dict = None
    ):
        """Index document pages for retrieval."""
        from pdf2image import convert_from_path

        # Convert PDF to images
        pages = convert_from_path(pdf_path)

        for page_num, page_image in enumerate(pages):
            # Save page to temp buffer
            img_byte_arr = io.BytesIO()
            page_image.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()

            # Generate embedding
            embedding = next(self.model.embed(img_bytes))

            # Store in Qdrant
            self.client.upsert(
                collection_name="documents",
                points=[
                    PointStruct(
                        id=f"{doc_id}_{page_num}",
                        vector=embedding,
                        payload={
                            "doc_id": doc_id,
                            "page_num": page_num,
                            "total_pages": len(pages),
                            **(metadata or {})
                        }
                    )
                ]
            )

    def search(
        self,
        query_image: str,
        top_k: int = 5
    ) -> List[dict]:
        """Search for similar document pages."""
        # Load query image
        with open(query_image, "rb") as f:
            query_bytes = f.read()

        # Generate query embedding
        query_embedding = next(self.model.embed(query_bytes))

        # Search
        results = self.client.query_points(
            collection_name="documents",
            query=query_embedding,
            limit=top_k,
            with_payload=True
        )

        return [
            {
                "score": r.score,
                "doc_id": r.payload["doc_id"],
                "page_num": r.payload["page_num"],
                "total_pages": r.payload["total_pages"]
            }
            for r in results.results
        ]
```

### 4. Real-Time Object Detection

```python
# plugins/object_detection.py
from ultralytics import YOLO
import cv2
import numpy as np

class ObjectDetector:
    """Real-time object detection with YOLO."""

    def __init__(self, model_size: str = "yolov8n.pt"):
        self.model = YOLO(model_size)
        self.class_names = self.model.names

    def detect(
        self,
        image: np.ndarray,
        conf_threshold: float = 0.5,
        iou_threshold: float = 0.45
    ) -> List[dict]:
        """Detect objects in image."""
        results = self.model(
            image,
            conf=conf_threshold,
            iou=iou_threshold,
            verbose=False
        )

        detections = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                detections.append({
                    "class": self.class_names[int(box.cls)],
                    "confidence": float(box.conf),
                    "bbox": [int(x1), int(y1), int(x2), int(y2)]
                })

        return detections

    def detect_from_file(
        self,
        image_path: str
    ) -> List[dict]:
        """Detect objects from image file."""
        image = cv2.imread(image_path)
        return self.detect(image)

    def annotate(
        self,
        image: np.ndarray,
        detections: List[dict]
    ) -> np.ndarray:
        """Annotate image with detections."""
        annotated = image.copy()

        for det in detections:
            x1, y1, x2, y2 = det["bbox"]

            # Draw box
            cv2.rectangle(
                annotated,
                (int(x1), int(y1)),
                (int(x2), int(y2)),
                (0, 255, 0),
                2
            )

            # Draw label
            label = f"{det['class']}: {det['confidence']:.2f}"
            cv2.putText(
                annotated,
                label,
                (int(x1), int(y1) - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

        return annotated

    def stream_detection(
        self,
        camera_index: int = 0,
        callback = None
    ):
        """Stream detection from camera."""
        cap = cv2.VideoCapture(camera_index)

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Detect
                detections = self.detect(frame)

                # Annotate
                annotated = self.annotate(frame, detections)

                # Callback or display
                if callback:
                    callback(frame, detections)
                else:
                    cv2.imshow("Detection", annotated)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

        finally:
            cap.release()
            cv2.destroyAllWindows()
```

### 5. Scene Understanding

```python
# plugins/scene_understanding.py
from transformers import pipeline

class SceneUnderstanding:
    """Understand and describe scenes."""

    def __init__(self):
        # Image captioning
        self.captioner = pipeline(
            "image-to-text",
            model="Salesforce/blip-image-captioning-base"
        )

        # Visual question answering
        self.vqa = pipeline(
            "visual-question-answering",
            model="dandelin/vilt-b32-finetuned-vqa"
        )

    def describe_scene(self, image_path: str) -> str:
        """Generate scene description."""
        caption = self.captioner(image_path)
        return caption[0]["generated_text"]

    def answer_question(
        self,
        image_path: str,
        question: str
    ) -> str:
        """Answer visual question."""
        result = self.vqa(
            image=image_path,
            question=question
        )
        return result[0]["answer"]

    def detailed_analysis(
        self,
        image_path: str
    ) -> dict:
        """Comprehensive scene analysis."""
        # Get basic description
        description = self.describe_scene(image_path)

        # Ask specific questions
        questions = [
            "What objects are visible?",
            "What is the setting?",
            "What are the main colors?",
            "Are there people visible?",
            "What is the mood of the scene?"
        ]

        answers = {}
        for q in questions:
            answers[q] = self.answer_question(image_path, q)

        return {
            "description": description,
            "details": answers
        }
```

## Integration with AgentX

### Vision Tool

```python
# core/agentx_vision.py
from typing import Optional

class VisionEnabledAgent:
    """AgentX with vision capabilities."""

    def __init__(
        self,
        core_agent,
        vision_model: OllamaVision,
        detector: ObjectDetector = None
    ):
        self.agent = core_agent
        self.vision = vision_model
        self.detector = detector

    def chat_with_image(
        self,
        message: str,
        image_path: Optional[str] = None,
        user_id: str = "default"
    ) -> str:
        """Chat with optional image."""
        context = ""

        # Analyze image if provided
        if image_path:
            # First, detect objects
            if self.detector:
                detections = self.detector.detect_from_file(image_path)
                context += f"\nObjects detected: {', '.join([d['class'] for d in detections])}\n"

            # Then, get visual description
            description = self.vision.analyze(
                image_path,
                "Describe what you see in detail, focusing on relevant aspects for the user's question."
            )
            context += f"\nVisual description: {description}\n"

        # Add to message
        enhanced_message = f"{message}\n\n{context}".strip()

        # Get agent response
        response = self.agent.chat(
            message=enhanced_message,
            user_id=user_id
        )

        return response

    def analyze_screenshot(
        self,
        screenshot_path: str,
        question: str = "Analyze this interface"
    ) -> dict:
        """Analyze UI screenshot."""
        # Get basic analysis
        analysis = self.vision.analyze(
            screenshot_path,
            f"""
            Analyze this interface screenshot.
            {question}

            Focus on:
            - Layout and structure
            - UI components
            - Text content
            - Accessibility issues
            - Design patterns
            """
        )

        # Object detection for UI elements
        elements = []
        if self.detector:
            detections = self.detector.detect_from_file(screenshot_path)
            elements = [d["class"] for d in detections]

        return {
            "analysis": analysis,
            "detected_elements": elements
        }
```

## Advanced Features

### 1. Video Understanding

```python
import cv2

class VideoAnalyzer:
    """Analyze video content."""

    def __init__(self, vision_model):
        self.vision = vision_model

    def analyze_video(
        self,
        video_path: str,
        frame_interval: int = 30,
        max_frames: int = 10
    ) -> dict:
        """Analyze video by sampling frames."""
        cap = cv2.VideoCapture(video_path)

        frames = []
        frame_count = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        while len(frames) < max_frames and frame_count < total_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count)
            ret, frame = cap.read()

            if ret:
                # Save frame to temp file
                temp_path = f"/tmp/frame_{len(frames)}.jpg"
                cv2.imwrite(temp_path, frame)
                frames.append(temp_path)

            frame_count += frame_interval

        cap.release()

        # Analyze each frame
        descriptions = []
        for frame_path in frames:
            desc = self.vision.analyze(
                frame_path,
                "Describe what you see in this frame."
            )
            descriptions.append(desc)

        # Generate summary
        summary = " ".join(descriptions)

        return {
            "summary": summary,
            "frame_descriptions": descriptions,
            "total_frames_analyzed": len(frames)
        }
```

### 2. Image Embedding Search

```python
# plugins/image_search.py
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, models

class ImageSearch:
    """Semantic image search."""

    def __init__(self):
        self.client = QdrantClient(url="http://localhost:6333")

        # Create collection
        self.client.create_collection(
            collection_name="images",
            vectors_config=models.VectorParams(
                size=512,  # CLIP dimension
                distance=models.Distance.COSINE
            )
        )

    def index_image(
        self,
        image_path: str,
        image_id: str,
        metadata: dict = None
    ):
        """Index image for search."""
        # Generate CLIP embedding
        import clip
        import torch

        device = "cuda" if torch.cuda.is_available() else "cpu"
        model, preprocess = clip.load("ViT-B/32", device=device)

        from PIL import Image
        image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)

        with torch.no_grad():
            embedding = model.encode_image(image).cpu().numpy()[0]

        # Store in Qdrant
        self.client.upsert(
            collection_name="images",
            points=[
                PointStruct(
                    id=image_id,
                    vector=embedding.tolist(),
                    payload={
                        "path": image_path,
                        **(metadata or {})
                    }
                )
            ]
        )

    def search(
        self,
        query_text: str,
        top_k: int = 5
    ) -> list:
        """Search images by text query."""
        # Generate text embedding
        import clip
        import torch

        device = "cuda" if torch.cuda.is_available() else "cpu"
        model, _ = clip.load("ViT-B/32", device=device)

        text_tokens = clip.tokenize([query_text]).to(device)

        with torch.no_grad():
            text_embedding = model.encode_text(text_tokens).cpu().numpy()[0]

        # Search
        results = self.client.search(
            collection_name="images",
            query_vector=text_embedding.tolist(),
            limit=top_k,
            with_payload=True
        )

        return [
            {
                "score": r.score,
                "path": r.payload.get("path"),
                "metadata": r.payload
            }
            for r in results
        ]
```

## Performance Optimization

### Batch Processing

```python
def analyze_batch(
    self,
    image_paths: List[str],
    batch_size: int = 8
) -> List[str]:
    """Analyze multiple images in batches."""
    descriptions = []

    for i in range(0, len(image_paths), batch_size):
        batch = image_paths[i:i + batch_size]

        # Process batch
        batch_results = [
            self.vision.analyze(path, "Describe this image.")
            for path in batch
        ]

        descriptions.extend(batch_results)

    return descriptions
```

### GPU Acceleration

```python
# Use GPU for vision models
import torch

class GPUVisionModel:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def load_model(self):
        """Load model on GPU."""
        model = ...
        model.to(self.device)
        return model
```

## References

- [LLaVA Model](https://llava.hliu.cc/)
- [Fuyu-8B](https://www.adept.ai/blog/fuyu-8b)
- [ColPali Documentation](https://qdrant.tech/documentation/fastembed/fastembed-colbert/)
- [YOLO Detection](https://github.com/ultralytics/ultralytics)
- [NVIDIA VLM Blueprints](https://www.nvidia.com/en-us/data-center/products/vid-model/)
