/**
 * LangGraph component registry for Real AgentX v0.1 (C007).
 *
 * Colocated with graph.py for industry-standard LangSmith/LangChain integration.
 * Export default maps widget types to React components.
 *
 * @see docs.langchain.com/langsmith/generative-ui-react
 * @see c007-frontend-architecture/design.md
 */

// NOTE: Using absolute imports (CLAUDE_POLICY.md requirement)
// Update import paths based on your frontend structure
import MarkdownWidget from '@components/ui/widgets/MarkdownWidget';
import CardWidget from '@components/ui/widgets/CardWidget';
import FormWidget from '@components/ui/widgets/FormWidget';
import ProgressWidget from '@components/ui/widgets/ProgressWidget';
import ActionWidget from '@components/ui/widgets/ActionWidget';
import ConfirmationWidget from '@components/ui/widgets/ConfirmationWidget';
import VoiceWidget from '@components/ui/widgets/VoiceWidget';
import ImageWidget from '@components/ui/widgets/ImageWidget';
import GalleryWidget from '@components/ui/widgets/GalleryWidget';
import ChartWidget from '@components/ui/widgets/ChartWidget';
import SearchResultWidget from '@components/ui/widgets/SearchResultWidget';
import HopProgressWidget from '@components/ui/widgets/HopProgressWidget';
import CitationCardWidget from '@components/ui/widgets/CitationCardWidget';

/**
 * Widget registry for LangGraph server-driven UI.
 *
 * Maps backend widget types to frontend React components.
 * The LoadExternalComponent uses this registry to render widgets.
 */
export default {
  markdown: MarkdownWidget,
  card: CardWidget,
  form: FormWidget,
  progress: ProgressWidget,
  action: ActionWidget,
  confirmation: ConfirmationWidget,
  voice: VoiceWidget,
  image: ImageWidget,
  gallery: GalleryWidget,
  chart: ChartWidget,
  searchResult: SearchResultWidget,
  hopProgress: HopProgressWidget,
  citationCard: CitationCardWidget,
} as const;
