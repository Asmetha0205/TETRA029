"""
Refresh Manager for CurricuAlign AI.

Manages background thread execution, scheduled cron/interval refresh runs,
status tracking, manual triggers, and execution history.
"""

import datetime
import logging
import threading
import time
from typing import Any, Dict, List, Optional

from backend.industry_engine.scheduler.jobs import RefreshJobConfig, RefreshJobState, RefreshStatus
from backend.industry_engine.scheduler.refresh_pipeline import RefreshPipeline, RefreshSummaryReport

logger = logging.getLogger("industry_engine.scheduler.refresh_manager")


class RefreshManager:
    """
    Manages background refresh scheduling and manual refresh triggers.
    """

    def __init__(self, pipeline: RefreshPipeline) -> None:
        """
        Initialize RefreshManager.

        Args:
            pipeline: RefreshPipeline instance.
        """
        self.pipeline = pipeline
        self._state = RefreshJobState()
        self._history: List[Dict[str, Any]] = []
        self._lock = threading.RLock()
        self._scheduler_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def trigger_refresh(
        self,
        raw_jobs: Optional[List[Any]] = None,
        config: Optional[RefreshJobConfig] = None,
    ) -> RefreshSummaryReport:
        """
        Trigger an immediate synchronous refresh run.

        Args:
            raw_jobs: Optional custom job dataset.
            config: Optional RefreshJobConfig override.

        Returns:
            RefreshSummaryReport detailing run metrics.
        """
        cfg = config or RefreshJobConfig()
        with self._lock:
            if self._state.status == RefreshStatus.RUNNING:
                logger.warning("[Industry] Refresh trigger ignored: pipeline already running.")
                return RefreshSummaryReport(
                    run_id="rejected",
                    success=False,
                    error_message="Refresh pipeline is already running.",
                )
            self._state.status = RefreshStatus.RUNNING
            self._state.last_run_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

        try:
            report = self.pipeline.run_refresh(
                raw_jobs=raw_jobs,
                source_name=cfg.source_name,
                dry_run=cfg.dry_run,
            )

            with self._lock:
                self._state.total_runs += 1
                if report.success:
                    self._state.status = RefreshStatus.SUCCESS
                else:
                    self._state.status = RefreshStatus.FAILED
                    self._state.failed_runs += 1

                summary_dict = report.to_dict()
                self._state.last_run_summary = summary_dict
                self._history.append(summary_dict)

            return report
        except Exception as exc:
            with self._lock:
                self._state.status = RefreshStatus.FAILED
                self._state.failed_runs += 1
            logger.error("[Industry] Refresh execution error: %s", exc)
            return RefreshSummaryReport(
                run_id="error",
                success=False,
                error_message=str(exc),
            )

    def trigger_async_refresh(
        self,
        raw_jobs: Optional[List[Any]] = None,
        config: Optional[RefreshJobConfig] = None,
    ) -> bool:
        """
        Trigger an asynchronous refresh run in a daemon thread.

        Returns:
            True if started, False if already running.
        """
        with self._lock:
            if self._state.status == RefreshStatus.RUNNING:
                return False

        t = threading.Thread(
            target=self.trigger_refresh,
            kwargs={"raw_jobs": raw_jobs, "config": config},
            daemon=True,
        )
        t.start()
        logger.info("[Industry] Asynchronous refresh task dispatched.")
        return True

    def start_scheduler(self, interval_hours: float = 24.0) -> None:
        """Start recurring background scheduler thread."""
        with self._lock:
            if self._scheduler_thread and self._scheduler_thread.is_alive():
                logger.info("[Industry] Scheduler thread is already running.")
                return
            self._stop_event.clear()
            self._scheduler_thread = threading.Thread(
                target=self._scheduler_loop,
                args=(interval_hours,),
                daemon=True,
            )
            self._scheduler_thread.start()
            logger.info("[Industry] Background Refresh Scheduler started (interval=%.1fh).", interval_hours)

    def stop_scheduler(self) -> None:
        """Stop recurring background scheduler thread."""
        with self._lock:
            self._stop_event.set()
            logger.info("[Industry] Background Refresh Scheduler stop signal sent.")

    def get_state(self) -> RefreshJobState:
        """Get current state model."""
        with self._lock:
            return self._state.model_copy(deep=True)

    def get_history(self) -> List[Dict[str, Any]]:
        """Get list of past refresh execution summaries."""
        with self._lock:
            return list(self._history)

    def _scheduler_loop(self, interval_hours: float) -> None:
        """Internal loop for recurring scheduled refresh."""
        interval_seconds = interval_hours * 3600.0
        while not self._stop_event.is_set():
            logger.info("[Industry] Scheduled refresh loop executing...")
            self.trigger_refresh(config=RefreshJobConfig(source_name="cron_scheduler"))

            next_ts = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=interval_hours)
            with self._lock:
                self._state.next_run_time = next_ts.isoformat()

            # Sleep in short checks to respond quickly to stop_event
            sleep_step = 1.0
            slept = 0.0
            while slept < interval_seconds and not self._stop_event.is_set():
                time.sleep(sleep_step)
                slept += sleep_step
