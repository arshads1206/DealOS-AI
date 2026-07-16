import React, { Component, type ErrorInfo, type ReactNode } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";
import { Button } from "./Button";
import { GlassCard } from "./GlassCard";

interface Props {
  children?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error in component tree:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen items-center justify-center p-6 bg-[var(--color-surface-0)]">
          <GlassCard className="max-w-md w-full p-8 text-center" raised>
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[var(--color-crimson)]/[0.1] text-[var(--color-crimson)] mb-4">
              <AlertTriangle size={24} />
            </div>
            <h2 className="font-display text-xl text-[var(--color-ink-0)] mb-2">Something went wrong</h2>
            <p className="text-sm text-[var(--color-ink-3)] mb-6">
              An unexpected error occurred in the application. The engineering team has been notified.
            </p>
            <Button
              variant="secondary"
              className="w-full justify-center"
              onClick={() => {
                this.setState({ hasError: false });
                window.location.reload();
              }}
            >
              <RefreshCw size={14} />
              Reload Application
            </Button>
          </GlassCard>
        </div>
      );
    }

    return this.props.children;
  }
}
