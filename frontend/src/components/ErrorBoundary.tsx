import { Component, type ErrorInfo, type ReactNode } from "react";
import { AlertCircle, RefreshCw } from "lucide-react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
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
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.href = "/dashboard";
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen bg-[#1a1a1a] flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-gray-800 p-8 rounded-2xl shadow-xl border border-gray-700 text-center">
            <div className="flex justify-center mb-6">
              <div className="p-3 bg-red-600 rounded-full">
                <AlertCircle className="h-8 w-8 text-white" />
              </div>
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">
              Oops! Something went wrong
            </h2>
            <p className="text-gray-400 mb-6">
              We encountered an unexpected error. Don't worry, your data is safe.
            </p>
            {this.state.error && (
              <div className="mb-6 p-4 bg-gray-900 rounded-lg text-left">
                <p className="text-sm text-gray-300 font-mono break-all">
                  {this.state.error.message}
                </p>
              </div>
            )}
            <button
              onClick={this.handleReset}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-4 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all flex items-center justify-center gap-2"
            >
              <RefreshCw className="h-5 w-5" />
              <span>Go to Dashboard</span>
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
