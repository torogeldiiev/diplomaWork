import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'server')))

from models.cluster import Cluster
from models.config import Config
from models.platform import Platform
from database_handler import db_session_maker

session = db_session_maker()

def database_is_empty():
    return session.query(Cluster).count() == 0

def populate_db():
    """Populate the database with test data if empty."""
    print("Starting to populate the database...")

    if not database_is_empty():
        print("Database already contains data. Skipping population.")
        return

    cluster_a = Cluster(name="prod-cluster-01", release_version="7.1.7")
    cluster_b = Cluster(name="staging-cluster-02", release_version="7.1.9")
    session.add_all([cluster_a, cluster_b])
    session.commit()

    cluster_a_id, cluster_b_id = cluster_a.id, cluster_b.id

    configs = [
        Config(cluster_id=cluster_a_id, config_type="environment",       config_value="production"),
        Config(cluster_id=cluster_b_id, config_type="environment",       config_value="staging"),
        Config(cluster_id=cluster_a_id, config_type="region",            config_value="us-east-1"),
        Config(cluster_id=cluster_b_id, config_type="region",            config_value="eu-central-1"),
        Config(cluster_id=cluster_a_id, config_type="node_count",        config_value="10"),
        Config(cluster_id=cluster_b_id, config_type="node_count",        config_value="8"),
        Config(cluster_id=cluster_a_id, config_type="node_types",        config_value="m5.large,r6g.xlarge"),
        Config(cluster_id=cluster_b_id, config_type="node_types",        config_value="m5.large,r6g.2xlarge"),
        Config(cluster_id=cluster_a_id, config_type="installed_services",config_value="Spark=3.1.2,Kafka=2.8.0"),
        Config(cluster_id=cluster_b_id, config_type="installed_services",config_value="Spark=3.1.1,Kafka=2.8.0"),
        Config(cluster_id=cluster_a_id, config_type="authentication",     config_value="LDAP"),
        Config(cluster_id=cluster_b_id, config_type="authentication",     config_value="OAuth"),
        Config(cluster_id=cluster_a_id, config_type="allowed_ips",        config_value="192.168.1.0/24,10.0.0.0/16"),
        Config(cluster_id=cluster_b_id, config_type="allowed_ips",        config_value="192.168.1.0/24,172.16.0.0/16"),
        Config(cluster_id=cluster_a_id, config_type="cpu_limit",         config_value="16 vCPUs"),
        Config(cluster_id=cluster_b_id, config_type="cpu_limit",         config_value="8 vCPUs"),
        Config(cluster_id=cluster_a_id, config_type="memory_limit",      config_value="64GB"),
        Config(cluster_id=cluster_b_id, config_type="memory_limit",      config_value="32GB"),
        Config(cluster_id=cluster_a_id, config_type="log_level",         config_value="INFO"),
        Config(cluster_id=cluster_b_id, config_type="log_level",         config_value="DEBUG"),
        Config(cluster_id=cluster_a_id, config_type="monitoring_service",config_value="Prometheus"),
        Config(cluster_id=cluster_b_id, config_type="monitoring_service",config_value="Datadog"),
        Config(cluster_id=cluster_a_id, config_type="load_balancer",      config_value="HAProxy"),
        Config(cluster_id=cluster_b_id, config_type="load_balancer",      config_value="NGINX"),
        Config(cluster_id=cluster_a_id, config_type="routing_policy",    config_value="Round Robin"),
        Config(cluster_id=cluster_b_id, config_type="routing_policy",    config_value="Least Connections"),
        Config(cluster_id=cluster_a_id, config_type="backup_frequency",  config_value="Daily"),
        Config(cluster_id=cluster_b_id, config_type="backup_frequency",  config_value="Weekly"),
        Config(cluster_id=cluster_a_id, config_type="replication_factor",config_value="3"),
        Config(cluster_id=cluster_b_id, config_type="replication_factor",config_value="2"),
        Config(cluster_id=cluster_a_id, config_type="gc_settings",       config_value="G1GC"),
        Config(cluster_id=cluster_b_id, config_type="gc_settings",       config_value="ParallelGC"),
        Config(cluster_id=cluster_a_id, config_type="thread_pool_size",  config_value="50"),
        Config(cluster_id=cluster_b_id, config_type="thread_pool_size",  config_value="40"),
    ]
    session.add_all(configs)
    session.commit()

    platforms = [
        Platform(cluster_id=cluster_a_id, name="Ubuntu",   version="20.04"),
        Platform(cluster_id=cluster_a_id, name="CentOS",   version="7"),
        Platform(cluster_id=cluster_b_id, name="Ubuntu",   version="22.04"),
        Platform(cluster_id=cluster_b_id, name="Windows",  version="10"),
    ]
    session.add_all(platforms)
    session.commit()

    print("Database populated with clusters, configs, and platforms.")


if __name__ == "__main__":
    populate_db()
