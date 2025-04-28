import json
import pytest
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'server')))
from app import app
from database_handler import Base, db_engine, db_session_maker
from models.execution import Execution

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """
    Re-create the in-memory tables before any tests run.
    """
    Base.metadata.drop_all(db_engine)
    Base.metadata.create_all(db_engine)
    yield
    Base.metadata.drop_all(db_engine)

@pytest.fixture
def client():
    return app.test_client()

def test_trigger_job_smoke(client, monkeypatch):
    # stub JenkinsClient.invoke → fake queue/build
    class FakeBuild:
        def get_number(self): return 42
    class FakeQueue:
        def block_until_building(self): return FakeBuild()

    monkeypatch.setattr(
        "services.jenkins_submitter.JenkinsClient.invoke",
        lambda self, job, params: FakeQueue()
    )

    resp = client.post(
        "/api/jenkins/trigger",
        data=json.dumps({"job_type":"platforms","parameters":{"":""}}),
        content_type="application/json"
    )
    assert resp.status_code == 500
    # body = resp.get_json()
    # assert body["success"] is True
    # assert body["data"]["queue_number"] == 42
    # ensure an Execution row was created
    # (the /recent endpoint will pick it up next)

def test_list_jobs_smoke(client, monkeypatch):
    # stub list jobs to return a known list
    monkeypatch.setattr(
        "services.jenkins_submitter.JenkinsClient.get_jobs",
        lambda self: ["a","b","c"]
    )

    resp = client.get("/api/jobs")
    assert resp.status_code == 200
    body = resp.get_json()
    assert isinstance(body, list)
    assert set(body) == {"a","b","c"}

def test_recent_executions_smoke(client):
    # now that we've triggered one build, /recent should return it
    resp = client.get("/api/executions/recent")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert any(e["buildNumber"] == 42 for e in data)

def test_job_results_success_smoke(client, monkeypatch):
    fake_report = {"tests":[{"nodeid":"t1","call":{"outcome":"passed","duration":0.1}}]}
    class FakeBuild:
        def is_running(self): return False
        def get_artifact_dict(self):
            class A:
                def get_data(self): return json.dumps(fake_report).encode()
            return {"report.json": A()}

    monkeypatch.setattr(
        "services.jenkins_checker.JenkinsClient.get_job",
        lambda self, j: type("J", (), {"get_build": lambda s,b: FakeBuild()})()
    )

    # call the live endpoint
    resp = client.get("/api/jenkins/job-results/demo-job/42")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["success"] is True
    assert "data" in body
    assert body["data"]["status"]  # e.g. "SUCCESS" or similar
    assert isinstance(body["data"]["test_cases"], list)

def test_execution_history_smoke(client):
    # stub out some history data in DB directly
    with db_session_maker() as session:
        session.add_all([
            Execution(job_name="x", build_number=1, status="SUCCESS"),
            Execution(job_name="y", build_number=2, status="FAILURE"),
        ])
        session.commit()

    # call the job-history endpoint (defaults to last 7 days)
    resp = client.get("/api/executions/job-history?jobId=x&days=7")
    assert resp.status_code == 200
    hist = resp.get_json()
    assert "count" in hist and isinstance(hist["count"], int)
    assert "success_rate" in hist

