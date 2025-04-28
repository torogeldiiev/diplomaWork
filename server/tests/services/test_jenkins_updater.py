import pytest
from scheduler import AbstractJob
from services.jenkins_updater import JenkinsUpdater
from services.jenkins_checker import JenkinsCheckerService
from db_utils import execution_utils
from models.execution import Execution
from notification import send_notification


class FakeClient:
    """Simulates JenkinsClient.get_job_status."""
    def __init__(self, status):
        self._status = status
        self.calls = []

    def get_job_status(self, job_name, build_number):
        self.calls.append((job_name, build_number))
        return self._status


class DummyChecker:
    """Stub for JenkinsCheckerService—just record calls."""
    def __init__(self):
        self.stored = []

    def store_tests_results(self, job_name, build_number):
        self.stored.append((job_name, build_number))


@pytest.fixture(autouse=True)
def fresh_db(db_session_maker):
    from database_handler import Base, db_engine
    Base.metadata.drop_all(db_engine)
    Base.metadata.create_all(db_engine)
    yield
    Base.metadata.drop_all(db_engine)


@pytest.fixture
def session_and_entry(db_session_maker):

    with db_session_maker() as session:
        exec = Execution(job_name="myjob", build_number=99, status="IN_PROGRESS")
        session.add(exec)
        session.commit()
        yield


@pytest.fixture(autouse=True)
def patch_notification(monkeypatch):
    sent = []
    monkeypatch.setattr(send_notification.__module__ + ".send_notification",
                        lambda subject, body: sent.append((subject, body)))
    return sent


def test_execute_in_progress_does_nothing(db_session_maker, session_and_entry):
    client = FakeClient(status="IN_PROGRESS")
    checker = DummyChecker()
    updater = JenkinsUpdater(client, checker, db_session_maker, "myjob", 99)

    assert updater.execute() is True
    assert updater.execute() is True


    with db_session_maker() as session:
        row = execution_utils.get_execution_by_build_number(session, 99)
        assert row.status == "IN_PROGRESS"
    assert not checker.stored


def test_execute_completed_triggers_all_actions(db_session_maker, session_and_entry, patch_notification):
    client = FakeClient(status="SUCCESS")
    checker = DummyChecker()
    updater = JenkinsUpdater(client, checker, db_session_maker, "myjob", 99)

    assert updater.execute() is False

    with db_session_maker() as session:
        row = execution_utils.get_execution_by_build_number(session, 99)
        assert row.status == "SUCCESS"

    assert len(patch_notification) == 1
    subject, body = patch_notification[0]
    assert "myjob" in subject and "#99" in subject and "SUCCESS" in subject

    assert checker.stored == [("myjob", 99)]
