import json
import pytest
from services.jenkins_checker import JenkinsCheckerService
from models.execution import TestResult, Execution

class FakeBuild:
    def __init__(self, running, report):
        self._running = running
        self._report = report

    def is_running(self): return self._running
    def get_artifact_dict(self):
        class A:
            def __init__(self, data): self.data = data
            def get_data(self): return json.dumps(self.data).encode()
        return {"report.json": A(self._report)}

class FakeClient:
    def __init__(self, build):
        self._build = build
    def get_job(self, name):
        class J:
            def __init__(self, b): self._b = b
            def get_build(self, num): return self._b
        return J(self._build)

@pytest.fixture(autouse=True)
def fresh_db(db_session_maker):
    from database_handler import Base, db_engine
    Base.metadata.drop_all(db_engine)
    Base.metadata.create_all(db_engine)
    yield
    Base.metadata.drop_all(db_engine)

def test_store_tests_results_success(db_session_maker, monkeypatch):
    report = {"tests":[{"nodeid":"t1","call":{"outcome":"passed","duration":0.15}},
                       {"nodeid":"t2","call":{"outcome":"failed","duration":0.05}}]}
    fake_build = FakeBuild(running=False, report=report)
    client = FakeClient(fake_build)
    svc = JenkinsCheckerService(client, db_session_maker)

    # pre-create execution row:
    from db_utils.execution_utils import create_execution_entry
    with db_session_maker() as session:
        create_execution_entry(session, "jobX", 99, {})

    # should not raise
    svc.store_tests_results("jobX", 99)

    # validate DB:
    with db_session_maker() as session:
        rows = session.query(TestResult).filter_by(execution_id=1).all()
        names = {r.name for r in rows}
        assert names == {"t1", "t2"}

def test_no_store_while_running(db_session_maker, monkeypatch):
    fake_build = FakeBuild(running=True, report={})
    client = FakeClient(fake_build)
    svc = JenkinsCheckerService(client, db_session_maker)

    # create execution:
    from db_utils.execution_utils import create_execution_entry
    with db_session_maker() as session:
        create_execution_entry(session, "jobY", 55, {})

    # should bail silently
    svc.store_tests_results("jobY", 55)

    with db_session_maker() as session:
        cnt = session.query(TestResult).count()
        assert cnt == 0
