import { Component } from 'react'
import ServerError from '../../pages/ServerError.jsx'

/**
 * Top-level render-error safety net. React Router's Suspense fallback
 * already handles loading states; this catches actual thrown errors during
 * render (a bad API payload shape, a null-reference bug, etc.) so the user
 * sees a recoverable error page instead of a blank white screen.
 */
export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {
    // eslint-disable-next-line no-console
    console.error('Unhandled UI error:', error, errorInfo)
  }

  handleRetry = () => {
    this.setState({ hasError: false })
  }

  render() {
    if (this.state.hasError) {
      return <ServerError onRetry={this.handleRetry} />
    }
    return this.props.children
  }
}
