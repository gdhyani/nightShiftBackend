from app.services.scheduler import NightShiftScheduler


def test_scheduler_creates():
    scheduler = NightShiftScheduler(
        session_factory=None, upstox=None,
        token_manager=None, instrument_service=None,
    )
    assert scheduler is not None
    assert len(scheduler.get_job_list()) >= 3


def test_scheduler_job_names():
    scheduler = NightShiftScheduler(
        session_factory=None, upstox=None,
        token_manager=None, instrument_service=None,
    )
    names = scheduler.get_job_list()
    assert "morning_token_request" in names
    assert "instrument_refresh" in names
    assert "eod_cleanup" in names
