import pytest
import sys
import os
# from dotenv import load_dotenv
# load_dotenv(os.getenv("ENV_FILE", "configs/local.env"))

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'server')))
from server.models.cluster import Cluster
from server.database_handler import db_session_maker


@pytest.fixture(scope="module")
def db_session():
    """Set up a database session for testing."""
    session = db_session_maker()
    yield session
    session.close()


@pytest.fixture
def get_clusters(db_session):
    """Fetch clusters and their configurations from the database."""
    clusters = db_session.query(Cluster).all()
    cluster_data = {}

    for cluster in clusters:
        configs = {config.config_type: config.config_value for config in cluster.configs}
        cluster_data[cluster.name] = configs

    return cluster_data


def test_metadata_consistency(get_clusters):
    cluster_a = get_clusters["prod-cluster-01"]
    cluster_b = get_clusters["staging-cluster-02"]

    assert cluster_a["environment"] == cluster_b["environment"], "Environment mismatch!"
    assert cluster_a["region"] == cluster_b["region"], "Region mismatch!"


def test_node_count_and_type(get_clusters):
    cluster_a = get_clusters["prod-cluster-01"]
    cluster_b = get_clusters["staging-cluster-02"]

    assert cluster_a["node_count"] == cluster_b["node_count"], "Node count mismatch!"
    assert set(cluster_a["node_types"].split(",")) == set(cluster_b["node_types"].split(",")), "Node types mismatch!"


def test_software_versions(get_clusters):
    cluster_a = get_clusters["prod-cluster-01"]
    cluster_b = get_clusters["staging-cluster-02"]

    for service in cluster_a["installed_services"].split(","):
        name, version = service.split("=")
        cluster_b_services = dict(s.split("=") for s in cluster_b["installed_services"].split(","))
        assert version == cluster_b_services.get(name, "MISSING"), f"Version mismatch for {name}!"


def test_security_settings(get_clusters):
    cluster_a = get_clusters["prod-cluster-01"]
    cluster_b = get_clusters["staging-cluster-02"]

    assert cluster_a["authentication"] == cluster_b["authentication"], "Authentication method mismatch!"
    assert set(cluster_a["allowed_ips"].split(",")) == set(cluster_b["allowed_ips"].split(",")), "Allowed IPs mismatch!"


def test_resource_allocation(get_clusters):
    cluster_a = get_clusters["prod-cluster-01"]
    cluster_b = get_clusters["staging-cluster-02"]

    assert cluster_a["cpu_limit"] == cluster_b["cpu_limit"], "CPU allocation mismatch!"
    assert cluster_a["memory_limit"] == cluster_b["memory_limit"], "Memory allocation mismatch!"


def test_logging_and_monitoring(get_clusters):
    cluster_a = get_clusters["prod-cluster-01"]
    cluster_b = get_clusters["staging-cluster-02"]

    assert cluster_a["log_level"] == cluster_b["log_level"], "Log level mismatch!"
    assert cluster_a["monitoring_service"] == cluster_b["monitoring_service"], "Monitoring service mismatch!"


def test_load_balancer_settings(get_clusters):
    cluster_a = get_clusters["prod-cluster-01"]
    cluster_b = get_clusters["staging-cluster-02"]

    assert cluster_a["load_balancer"] == cluster_b["load_balancer"], "Load balancer mismatch!"
    assert cluster_a["routing_policy"] == cluster_b["routing_policy"], "Routing policy mismatch!"


def test_backup_policies(get_clusters):
    cluster_a = get_clusters["prod-cluster-01"]
    cluster_b = get_clusters["staging-cluster-02"]

    assert cluster_a["backup_frequency"] == cluster_b["backup_frequency"], "Backup frequency mismatch!"
    assert cluster_a["replication_factor"] == cluster_b["replication_factor"], "Replication factor mismatch!"


def test_performance_settings(get_clusters):
    cluster_a = get_clusters["prod-cluster-01"]
    cluster_b = get_clusters["staging-cluster-02"]

    assert cluster_a["gc_settings"] == cluster_b["gc_settings"], "Garbage collection settings mismatch!"
    assert cluster_a["thread_pool_size"] == cluster_b["thread_pool_size"], "Thread pool size mismatch!"


if __name__ == "__main__":
    pytest.main()
