from __future__ import annotations
import logging
import sched
import threading
import time

logger = logging.getLogger(__name__)


class AbstractJob:
    def execute(self) -> None:
        raise NotImplementedError()


def _dispatch(scheduler: sched.scheduler, job: AbstractJob, interval: int) -> None:
    try:
        logger.debug("Running scheduled job: %s", job.__class__.__name__)
        job.execute()
    except Exception:
        logger.error("Exception caught during scheduled job execution", exc_info=True)
    finally:
        scheduler.enter(interval, 1, _dispatch, (scheduler, job, interval))


class Scheduler:
    """
    A simple scheduler that runs scheduled jobs in the background.
    """

    def __init__(self) -> None:
        self._sched = sched.scheduler(time.time, time.sleep)
        self._thread: threading.Thread | None = None

    def schedule(self, job: AbstractJob, seconds: int = 15) -> None:
        self._sched.enter(seconds, 1, _dispatch, (self._sched, job, seconds))
        logger.info("Scheduled job %s every %s seconds", job.__class__.__name__, seconds)

    def _run_loop(self) -> None:
        while True:
            self._sched.run(blocking=False)
            time.sleep(1)

    def start(self) -> None:
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()
            logger.info("Scheduler background thread started: %s", self._thread.is_alive())
