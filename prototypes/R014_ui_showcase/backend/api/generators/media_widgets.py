# =============================================================================
# AGENTX R014 - Media Widget Generators
# =============================================================================
# Generate content for image, gallery, and chart widgets
# =============================================================================

from datetime import datetime

import dspy

from api.dspy_signatures import (
    ChartContentSignature,
    GalleryContentSignature,
    ImageContentSignature,
)
from api.models import UIDescriptor


class MediaWidgetGenerator:
    """Generate content for media-based widgets."""

    @staticmethod
    async def generate_image(prompt: str) -> UIDescriptor:
        """Generate image widget content."""
        generator = dspy.Predict(ImageContentSignature)
        result = generator(subject=prompt)
        return UIDescriptor(
            id=f"image-{datetime.now().timestamp()}",
            type="image",
            timestamp=datetime.now().isoformat(),
            title=result.title,
            content=result.caption,
            metadata={
                "image_url": f"https://picsum.photos/800/600?random={datetime.now().timestamp()}"
            },
        )

    @staticmethod
    async def generate_gallery(prompt: str) -> UIDescriptor:
        """Generate gallery widget content."""
        generator = dspy.Predict(GalleryContentSignature)
        result = generator(theme=prompt)
        return UIDescriptor(
            id=f"gallery-{datetime.now().timestamp()}",
            type="gallery",
            timestamp=datetime.now().isoformat(),
            title=result.title,
            content=result.description,
            metadata={
                "images": [
                    {
                        "url": "https://picsum.photos/seed/nature1/400/400",
                        "title": "Nature Scene",
                    },
                    {
                        "url": "https://picsum.photos/seed/nature2/400/400",
                        "title": "Landscape",
                    },
                    {
                        "url": "https://picsum.photos/seed/nature3/400/400",
                        "title": "Water View",
                    },
                    {
                        "url": "https://picsum.photos/seed/nature4/400/400",
                        "title": "Mountain",
                    },
                ]
            },
        )

    @staticmethod
    async def generate_chart(prompt: str) -> UIDescriptor:
        """Generate chart widget content."""
        generator = dspy.Predict(ChartContentSignature)
        result = generator(data_topic=prompt)
        return UIDescriptor(
            id=f"chart-{datetime.now().timestamp()}",
            type="chart",
            timestamp=datetime.now().isoformat(),
            title=result.title,
            content=result.description,
            metadata={"chart_type": "bar"},
        )
