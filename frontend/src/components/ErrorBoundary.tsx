import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
    children: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false,
        error: null,
    };

    public static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('Uncaught error:', error, errorInfo);
    }

    public render() {
        if (this.state.hasError) {
            return (
                <div className="p-8 max-w-2xl mx-auto mt-10 bg-red-50 border border-red-200 rounded-lg text-red-900">
                    <h1 className="text-2xl font-bold mb-4">Something went wrong</h1>
                    <p className="mb-4">The application crashed with the following error:</p>
                    <pre className="bg-white p-4 rounded border border-red-100 overflow-auto text-sm font-mono">
                        {this.state.error?.message}
                    </pre>
                    <pre className="mt-4 text-xs text-red-700">
                        Open developer console for more details.
                    </pre>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
