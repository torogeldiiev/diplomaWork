import pytest
import json
from services.jenkins_submitter import JenkinsSubmitterService
from db_utils.execution_utils import get_execution_by_build_number, create_execution_entry
from models.execution import Execution

class FakeQueue:
    def __init__(self, build_number):
        self._build_number = build_number
    def block_until_building(self):
        class B:
            def get_number(self_inner): return self._build_number
        return B()

class FakeClient:
    def __init__(self, raise_error=False, build_number=123):
        self.raise_error = raise_error
        self._build_number = build_number

    def invoke(self, job_name, params):
        if self.raise_error:
            raise RuntimeError("Jenkins down")
        return FakeQueue(self._build_number)

@pytest.fixture(autouse=True)
def fresh_db(db_session_maker):
    # wipe & recreate tables
    from database_handler import Base, db_engine
    Base.metadata.drop_all(db_engine)
    Base.metadata.create_all(db_engine)
    yield
    Base.metadata.drop_all(db_engine)

def test_trigger_creates_execution_row(db_session_maker, monkeypatch):
    client = FakeClient(build_number=42)
    svc = JenkinsSubmitterService(client, db_session_maker)
    # no exception => success
    resp = svc.trigger_job("myjob", {"foo":"bar"})
    assert resp["success"] is True
    assert resp["data"]["queue_number"] == 42

    # now there should be an Execution in DB
    with db_session_maker() as session:
        exec = get_execution_by_build_number(session, 42)
        assert isinstance(exec, Execution)
        assert exec.job_name == "myjob"
        assert exec.status == "IN_PROGRESS"

def test_trigger_propagates_failure(db_session_maker):
    client = FakeClient(raise_error=True)
    svc = JenkinsSubmitterService(client, db_session_maker)
    resp = svc.trigger_job("myjob", {})
    assert resp["success"] is False
    assert "Jenkins down" in resp["message"]
