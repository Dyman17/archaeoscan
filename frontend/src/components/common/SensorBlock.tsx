import React, { ReactNode, memo } from 'react';
import { cn } from '@/lib/utils';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';

interface SensorBlockProps {
  title: string;
  icon?: ReactNode;
  summary?: ReactNode;
  children: ReactNode;
  defaultOpen?: boolean;
  className?: string;
}

export const SensorBlock = memo(function SensorBlock({
  title,
  icon,
  summary,
  children,
  defaultOpen = true,
  className,
}: SensorBlockProps) {
  const [isOpen, setIsOpen] = React.useState(defaultOpen);

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <div className={cn('data-card', className)}>
        <CollapsibleTrigger asChild>
          <Button
            variant="ghost"
            className="w-full flex items-center justify-between p-0 h-auto hover:bg-transparent"
          >
            <div className="flex items-center gap-3">
              {icon && (
                <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                  {icon}
                </div>
              )}
              <div className="text-left">
                <h3 className="font-semibold text-lg">{title}</h3>
                {summary && (
                  <p className="text-sm text-muted-foreground">{summary}</p>
                )}
              </div>
            </div>
            {isOpen ? (
              <ChevronUp className="h-5 w-5 text-muted-foreground" />
            ) : (
              <ChevronDown className="h-5 w-5 text-muted-foreground" />
            )}
          </Button>
        </CollapsibleTrigger>

        <CollapsibleContent className="mt-4">
          <div className="space-y-2">{children}</div>
        </CollapsibleContent>
      </div>
    </Collapsible>
  );
});
