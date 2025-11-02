"""
Event system for pipeline execution hooks.

Enables observability and custom logic at key pipeline lifecycle points.
"""

from typing import Any, Callable, Dict, List, Optional


class EventEmitter:
    """
    Event emitter for pipeline execution hooks.

    Supports registering listeners for pipeline events:
    - on_pipeline_start: Before pipeline execution begins
    - on_pipeline_complete: After pipeline completes successfully
    - on_pipeline_error: When pipeline fails
    - on_step_start: Before each step executes
    - on_step_complete: After each step completes
    - on_step_error: When a step fails

    Example:
        >>> events = EventEmitter()
        >>> events.on("step_complete", lambda step, duration: print(f"{step.name}: {duration}ms"))
        >>> events.emit("step_complete", step=my_step, duration=123)
    """

    def __init__(self) -> None:
        """Initialize event emitter with empty listener registry."""
        self._listeners: Dict[str, List[Callable[..., None]]] = {}

    def on(self, event_name: str, callback: Callable[..., None]) -> None:
        """
        Register an event listener.

        Args:
            event_name: Name of the event (e.g., "step_complete")
            callback: Function to call when event is emitted

        Example:
            >>> events.on("pipeline_start", lambda config: logger.info(f"Starting {config}"))
        """
        # TODO Phase 2: Implement listener registration
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)

    def emit(self, event_name: str, **kwargs: Any) -> None:
        """
        Emit an event to all registered listeners.

        Args:
            event_name: Name of the event
            **kwargs: Event data to pass to listeners

        Example:
            >>> events.emit("step_complete", step=step, duration_ms=45)
        """
        # TODO Phase 2: Implement event emission with error handling
        if event_name in self._listeners:
            for callback in self._listeners[event_name]:
                try:
                    callback(**kwargs)
                except Exception as e:
                    # Log but don't fail pipeline on listener error
                    print(f"Event listener error for {event_name}: {e}")

    def clear(self, event_name: Optional[str] = None) -> None:
        """
        Clear event listeners.

        Args:
            event_name: Specific event to clear, or None to clear all

        Example:
            >>> events.clear("step_complete")  # Clear specific event
            >>> events.clear()  # Clear all events
        """
        # TODO Phase 2: Implement listener cleanup
        if event_name is None:
            self._listeners.clear()
        elif event_name in self._listeners:
            del self._listeners[event_name]
