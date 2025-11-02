"""
Schedule manager for cron-like and event-based pipeline execution.

Supports:
- Cron expressions (standard 5-field format)
- Time-based intervals
- Event-driven triggers (file arrival, API events)
- Hybrid scheduling (time + event conditions)
"""

import logging
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import glob
import re

logger = logging.getLogger(__name__)


class ScheduleMode(str, Enum):
    """Schedule execution modes."""

    CRON = "cron"  # Cron expression
    INTERVAL = "interval"  # Fixed time interval
    FILE_WATCH = "file_watch"  # Triggered by file arrival
    HYBRID = "hybrid"  # Combination of time and event


@dataclass
class Schedule:
    """
    Represents a scheduled task.

    Attributes:
        name: Schedule identifier
        mode: Schedule mode
        expression: Cron expression or interval specification
        function: Function to execute
        args: Positional arguments for function
        kwargs: Keyword arguments for function
        watch_path: Path to watch for file arrivals (FILE_WATCH mode)
        file_pattern: File pattern to match (FILE_WATCH mode)
        last_run: Timestamp of last execution
        next_run: Timestamp of next scheduled execution
        is_active: Whether schedule is active
        run_count: Number of times executed
    """

    name: str
    mode: ScheduleMode
    expression: str
    function: Callable
    args: Tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    watch_path: Optional[str] = None
    file_pattern: str = "*.*"
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    is_active: bool = True
    run_count: int = 0


class ScheduleManager:
    """
    Manages scheduled execution of pipelines and tasks.

    Features:
    - Cron-style scheduling (e.g., "0 * * * *" = hourly)
    - Interval-based scheduling (e.g., every 5 minutes)
    - File-watch triggers (execute when files arrive)
    - Hybrid mode (time + event conditions)
    - Thread-based execution (non-blocking)

    Args:
        check_interval: How often to check schedules (seconds)

    Example:
        >>> manager = ScheduleManager()
        >>>
        >>> # Hourly execution
        >>> manager.schedule("0 * * * *", run_pipeline, name="hourly_job")
        >>>
        >>> # Every 5 minutes
        >>> manager.schedule_interval(300, run_pipeline, name="frequent_job")
        >>>
        >>> # File arrival trigger
        >>> manager.schedule_file_watch("data/incoming/", process_file, pattern="*.csv")
        >>>
        >>> manager.start()
    """

    def __init__(self, check_interval: float = 10.0):
        """Initialize schedule manager."""
        self.check_interval = check_interval
        self.schedules: Dict[str, Schedule] = {}
        self.is_running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        logger.info(f"ScheduleManager initialized (check_interval={check_interval}s)")

    def schedule(
        self,
        expression: str,
        function: Callable,
        args: Tuple = (),
        kwargs: Dict[str, Any] = None,
        name: Optional[str] = None,
    ) -> str:
        """
        Schedule function with cron expression.

        Args:
            expression: Cron expression (5 fields: minute hour day month weekday)
            function: Function to execute
            args: Positional arguments
            kwargs: Keyword arguments
            name: Schedule name (auto-generated if None)

        Returns:
            Schedule name

        Example:
            >>> # Run at minute 0 of every hour
            >>> manager.schedule("0 * * * *", run_dag)
            >>>
            >>> # Run at 2:30 AM every day
            >>> manager.schedule("30 2 * * *", run_dag)
            >>>
            >>> # Run every 15 minutes
            >>> manager.schedule("*/15 * * * *", run_dag)
        """
        if not self._validate_cron(expression):
            raise ValueError(f"Invalid cron expression: {expression}")

        schedule_name = name or f"cron_{len(self.schedules)}"

        schedule = Schedule(
            name=schedule_name,
            mode=ScheduleMode.CRON,
            expression=expression,
            function=function,
            args=args,
            kwargs=kwargs or {},
            next_run=self._calculate_next_cron(expression),
        )

        with self._lock:
            self.schedules[schedule_name] = schedule

        logger.info(f"Scheduled (cron): {schedule_name} with '{expression}'")
        return schedule_name

    def schedule_interval(
        self,
        seconds: int,
        function: Callable,
        args: Tuple = (),
        kwargs: Dict[str, Any] = None,
        name: Optional[str] = None,
    ) -> str:
        """
        Schedule function at fixed intervals.

        Args:
            seconds: Interval in seconds
            function: Function to execute
            args: Positional arguments
            kwargs: Keyword arguments
            name: Schedule name

        Returns:
            Schedule name
        """
        schedule_name = name or f"interval_{len(self.schedules)}"

        schedule = Schedule(
            name=schedule_name,
            mode=ScheduleMode.INTERVAL,
            expression=str(seconds),
            function=function,
            args=args,
            kwargs=kwargs or {},
            next_run=datetime.now() + timedelta(seconds=seconds),
        )

        with self._lock:
            self.schedules[schedule_name] = schedule

        logger.info(f"Scheduled (interval): {schedule_name} every {seconds}s")
        return schedule_name

    def schedule_file_watch(
        self,
        watch_path: str,
        function: Callable,
        pattern: str = "*.*",
        args: Tuple = (),
        kwargs: Dict[str, Any] = None,
        name: Optional[str] = None,
    ) -> str:
        """
        Schedule function to run when files arrive.

        Args:
            watch_path: Directory to watch
            function: Function to execute (receives file_path as first argument)
            pattern: File pattern to match
            args: Additional positional arguments
            kwargs: Keyword arguments
            name: Schedule name

        Returns:
            Schedule name
        """
        schedule_name = name or f"file_watch_{len(self.schedules)}"

        schedule = Schedule(
            name=schedule_name,
            mode=ScheduleMode.FILE_WATCH,
            expression=pattern,
            function=function,
            args=args,
            kwargs=kwargs or {},
            watch_path=watch_path,
            file_pattern=pattern,
        )

        with self._lock:
            self.schedules[schedule_name] = schedule

        logger.info(
            f"Scheduled (file_watch): {schedule_name} at {watch_path}/{pattern}"
        )
        return schedule_name

    def unschedule(self, name: str) -> bool:
        """
        Remove a schedule.

        Args:
            name: Schedule name

        Returns:
            True if removed, False if not found
        """
        with self._lock:
            if name in self.schedules:
                del self.schedules[name]
                logger.info(f"Unscheduled: {name}")
                return True
        return False

    def start(self, daemon: bool = True) -> None:
        """
        Start schedule processing.

        Args:
            daemon: Run as daemon thread
        """
        if self.is_running:
            logger.warning("Scheduler already running")
            return

        self.is_running = True
        self.scheduler_thread = threading.Thread(
            target=self._run_scheduler, daemon=daemon
        )
        self.scheduler_thread.start()
        logger.info("Scheduler started")

    def stop(self) -> None:
        """Stop schedule processing."""
        if not self.is_running:
            return

        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Scheduler stopped")

    def _run_scheduler(self) -> None:
        """Main scheduler loop."""
        processed_files: Dict[str, set] = {}

        while self.is_running:
            try:
                current_time = datetime.now()

                with self._lock:
                    schedules_to_run = []

                    for schedule in self.schedules.values():
                        if not schedule.is_active:
                            continue

                        should_run = False
                        run_args = schedule.args

                        if schedule.mode == ScheduleMode.CRON:
                            if schedule.next_run and current_time >= schedule.next_run:
                                should_run = True
                                schedule.next_run = self._calculate_next_cron(
                                    schedule.expression
                                )

                        elif schedule.mode == ScheduleMode.INTERVAL:
                            if schedule.next_run and current_time >= schedule.next_run:
                                should_run = True
                                interval = int(schedule.expression)
                                schedule.next_run = current_time + timedelta(
                                    seconds=interval
                                )

                        elif schedule.mode == ScheduleMode.FILE_WATCH:
                            new_files = self._check_new_files(
                                schedule, processed_files.get(schedule.name, set())
                            )
                            if new_files:
                                for file_path in new_files:
                                    schedules_to_run.append(
                                        (schedule, (file_path,) + schedule.args)
                                    )

                                if schedule.name not in processed_files:
                                    processed_files[schedule.name] = set()
                                processed_files[schedule.name].update(new_files)
                                continue

                        if should_run:
                            schedules_to_run.append((schedule, run_args))

                for schedule, run_args in schedules_to_run:
                    self._execute_schedule(schedule, run_args)

                time.sleep(self.check_interval)

            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(self.check_interval)

    def _execute_schedule(self, schedule: Schedule, args: Tuple) -> None:
        """Execute a scheduled task in a separate thread."""

        def run_task():
            try:
                logger.info(f"Executing schedule: {schedule.name}")
                schedule.function(*args, **schedule.kwargs)
                schedule.last_run = datetime.now()
                schedule.run_count += 1
                logger.info(f"Completed schedule: {schedule.name}")
            except Exception as e:
                logger.error(f"Error executing {schedule.name}: {e}")

        thread = threading.Thread(target=run_task, daemon=True)
        thread.start()

    def _check_new_files(self, schedule: Schedule, processed_files: set) -> List[str]:
        """Check for new files matching pattern."""
        if not schedule.watch_path:
            return []

        watch_path = Path(schedule.watch_path)
        if not watch_path.exists() or not watch_path.is_dir():
            return []

        pattern = str(watch_path / schedule.file_pattern)
        all_files = set(glob.glob(pattern))
        new_files = all_files - processed_files

        return sorted(new_files)

    def _validate_cron(self, expression: str) -> bool:
        """Validate cron expression (5 fields)."""
        parts = expression.strip().split()

        if len(parts) != 5:
            return False

        for part in parts:
            if not re.match(r"^[\d\*\-\/,]+$", part):
                return False

        return True

    def _calculate_next_cron(self, expression: str) -> datetime:
        """
        Calculate next execution time from cron expression.

        Simplified implementation supporting:
        - * (any value)
        - */N (every N units)
        - Specific numbers
        - Comma-separated lists

        Full cron library (croniter) would be better for production.
        """
        parts = expression.strip().split()
        minute, hour, day, month, weekday = parts

        now = datetime.now()
        next_time = now.replace(second=0, microsecond=0)

        if minute == "*":
            next_time += timedelta(minutes=1)
        elif minute.startswith("*/"):
            interval = int(minute[2:])
            next_minute = ((now.minute // interval) + 1) * interval
            if next_minute >= 60:
                next_time += timedelta(hours=1)
                next_minute = 0
            next_time = next_time.replace(minute=next_minute)
        else:
            target_minute = int(minute.split(",")[0])
            next_time = next_time.replace(minute=target_minute)
            if next_time <= now:
                next_time += timedelta(hours=1)

        if hour != "*":
            if hour.startswith("*/"):
                interval = int(hour[2:])
                target_hour = ((now.hour // interval) + 1) * interval
                if target_hour >= 24:
                    target_hour = 0
                    next_time += timedelta(days=1)
                next_time = next_time.replace(hour=target_hour)
            else:
                target_hour = int(hour.split(",")[0])
                next_time = next_time.replace(hour=target_hour)
                if next_time <= now:
                    next_time += timedelta(days=1)

        logger.debug(f"Next cron run for '{expression}': {next_time}")
        return next_time

    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status."""
        with self._lock:
            schedules_info = {
                name: {
                    "mode": schedule.mode.value,
                    "expression": schedule.expression,
                    "is_active": schedule.is_active,
                    "last_run": (
                        schedule.last_run.isoformat() if schedule.last_run else None
                    ),
                    "next_run": (
                        schedule.next_run.isoformat() if schedule.next_run else None
                    ),
                    "run_count": schedule.run_count,
                }
                for name, schedule in self.schedules.items()
            }

        return {
            "is_running": self.is_running,
            "schedule_count": len(self.schedules),
            "schedules": schedules_info,
        }

    def list_schedules(self) -> List[str]:
        """List all schedule names."""
        with self._lock:
            return list(self.schedules.keys())
