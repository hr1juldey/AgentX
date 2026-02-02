/** ProgressiveDisclosure component.
 *
 * Shows 3 widgets initially with "Show More" button to reveal remaining widgets.
 * Widgets are sorted by priority (highest first).
 */

import React, { useState, useMemo } from 'react';
import { WidgetCard } from './WidgetCard';
import { ShowMoreButton } from './ShowMoreButton';
import { WidgetSpecification } from '../types/widgets';

interface ProgressiveDisclosureProps {
  widgets: WidgetSpecification[];
  maxInitial?: number;
}

const INITIAL_WIDGET_COUNT = 3;

export const ProgressiveDisclosure: React.FC<ProgressiveDisclosureProps> = ({
  widgets,
  maxInitial = INITIAL_WIDGET_COUNT,
}) => {
  const [showAll, setShowAll] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Sort widgets by priority (highest first) and limit to maxInitial
  const sortedWidgets = useMemo(() => {
    return [...widgets].sort((a, b) => b.priority - a.priority);
  }, [widgets]);

  const visibleWidgets = showAll ? sortedWidgets : sortedWidgets.slice(0, maxInitial);
  const hiddenCount = showAll ? 0 : sortedWidgets.length - maxInitial;

  const handleShowMore = () => {
    setIsLoading(true);
    // Simulate async reveal for smooth UX
    setTimeout(() => {
      setShowAll(true);
      setIsLoading(false);
    }, 300);
  };

  if (sortedWidgets.length === 0) {
    return null;
  }

  return (
    <div className="progressive-disclosure">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {sortedWidgets.map((widget, index) => (
          <WidgetCard
            key={`${widget.widget_type}-${index}`}
            widget={widget}
            index={index}
            visible={index < maxInitial || showAll}
          />
        ))}
      </div>

      <ShowMoreButton
        hiddenCount={hiddenCount}
        onShowMore={handleShowMore}
        isLoading={isLoading}
      />
    </div>
  );
};
