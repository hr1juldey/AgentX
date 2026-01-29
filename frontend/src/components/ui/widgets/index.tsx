/**
 * Widget component exports for Real AgentX v0.1.
 *
 * Exports all 12 frozen widget types from C007.
 */

export { MarkdownWidget } from './MarkdownWidget';
export { CardWidget } from './CardWidget';

// Placeholder exports for remaining widgets
export const FormWidget = ({ fields, submitUrl, method }: any) => (
  <div className="bg-cell border border-membrane rounded-lg p-4">
    <h3 className="text-lg font-semibold mb-4">Form</h3>
    {fields.map((field: any) => (
      <div key={field.name} className="mb-4">
        <label className="block text-sm text-cytoplasm mb-1">{field.label}</label>
        <input
          type={field.type}
          name={field.name}
          placeholder={field.placeholder}
          className="w-full bg-membrane border border-membrane rounded px-3 py-2 text-nucleus"
        />
      </div>
    ))}
  </div>
);

export const ProgressWidget = ({ progress, status, indeterminate }: any) => (
  <div className="bg-cell border border-membrane rounded-lg p-4">
    <div className="flex justify-between mb-2">
      <span className="text-sm text-cytoplasm">{status}</span>
      <span className="text-sm text-cytoplasm">{indeterminate ? '...' : `${progress}%`}</span>
    </div>
    <div className="w-full bg-membrane rounded-full h-2 overflow-hidden">
      <div
        className="bg-enzyme h-full transition-all"
        style={{
          width: indeterminate ? '100%' : `${progress}%`,
          animation: indeterminate ? 'pulse 1s infinite' : 'none',
        }}
      />
    </div>
  </div>
);

export const ActionWidget = ({ label, action, primary = true }: any) => (
  <button
    className={`px-4 py-2 rounded-lg font-medium transition-opacity hover:opacity-90 ${
      primary ? 'bg-enzyme text-void' : 'bg-membrane text-nucleus'
    }`}
    onClick={() => console.log('Action:', action)}
  >
    {label}
  </button>
);

export const ConfirmationWidget = ({ title, message, confirmLabel, cancelLabel, onConfirm }: any) => (
  <div className="bg-cell border border-membrane rounded-lg p-4">
    <h3 className="text-lg font-semibold text-nucleus mb-2">{title}</h3>
    <p className="text-cytoplasm mb-4">{message}</p>
    <div className="flex gap-2">
      <button className="px-4 py-2 rounded bg-membrane text-nucleus hover:opacity-90">
        {cancelLabel}
      </button>
      <button className="px-4 py-2 rounded bg-enzyme text-void hover:opacity-90">
        {confirmLabel}
      </button>
    </div>
  </div>
);

export const VoiceWidget = ({ state, transcript }: any) => (
  <div className="bg-cell border border-membrane rounded-lg p-4">
    <div className="text-sm text-cytoplasm mb-2">Voice: {state}</div>
    {transcript && (
      <div className="text-nucleus">{transcript}</div>
    )}
  </div>
);

export const ImageWidget = ({ url, alt, caption }: any) => (
  <div className="bg-cell border border-membrane rounded-lg overflow-hidden">
    <img src={url} alt={alt} className="w-full h-auto" />
    {caption && (
      <div className="p-2 text-sm text-cytoplasm">{caption}</div>
    )}
  </div>
);

export const GalleryWidget = ({ images, columns = 3 }: any) => (
  <div
    className="grid gap-2"
    style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}
  >
    {images.map((img: any, i: number) => (
      <div key={i} className="bg-cell border border-membrane rounded overflow-hidden">
        <img src={img.url} alt={img.alt} className="w-full h-auto" />
      </div>
    ))}
  </div>
);

export const ChartWidget = ({ chartType, data, options }: any) => (
  <div className="bg-cell border border-membrane rounded-lg p-4">
    <div className="text-sm text-cytoplasm mb-2">Chart: {chartType}</div>
    <div className="text-xs text-vacuole">Chart rendering not yet implemented</div>
  </div>
);

export const SearchResultWidget = ({ query, results }: any) => (
  <div className="bg-cell border border-membrane rounded-lg p-4">
    <h3 className="text-lg font-semibold text-nucleus mb-2">Search: {query}</h3>
    <div className="space-y-2">
      {results.map((result: any, i: number) => (
        <div key={i} className="p-3 bg-membrane rounded">
          <div className="text-nucleus font-medium">{result.title}</div>
          <div className="text-sm text-cytoplasm mt-1">{result.body}</div>
          <a
            href={result.link}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-enzyme hover:underline"
          >
            {result.link}
          </a>
        </div>
      ))}
    </div>
  </div>
);

export const HopProgressWidget = ({ currentHop, totalHops, hopStatus }: any) => (
  <div className="bg-cell border border-membrane rounded-lg p-4">
    <div className="flex justify-between mb-2">
      <span className="text-sm text-cytoplasm">Multi-hop RAG Progress</span>
      <span className="text-sm text-cytoplasm">{currentHop}/{totalHops}</span>
    </div>
    <div className="flex gap-1">
      {hopStatus.map((status: any, i: number) => (
        <div
          key={i}
          className="h-2 flex-1 rounded"
          style={{
            backgroundColor:
              i < currentHop ? tokens.color.enzyme : tokens.color.membrane,
          }}
        />
      ))}
    </div>
  </div>
);

export const CitationCardWidget = ({ source, content, url, relevance }: any) => (
  <div className="bg-cell border border-membrane rounded-lg p-4">
    <div className="flex justify-between items-start mb-2">
      <span className="text-sm font-medium text-nucleus">{source}</span>
      <span
        className="text-xs px-2 py-1 rounded"
        style={{
          backgroundColor: tokens.color.membrane,
          color: tokens.color.enzyme,
        }}
      >
        {Math.round(relevance * 100)}%
      </span>
    </div>
    <p className="text-sm text-cytoplasm mb-2">{content}</p>
    {url && (
      <a
        href={url}
        target="_blank"
        rel="noopener noreferrer"
        className="text-xs text-enzyme hover:underline"
      >
        Source
      </a>
    )}
  </div>
);
