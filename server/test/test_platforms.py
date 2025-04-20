import re
import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'server')))

from server.models.platform import Platform
from server.models.cluster import Cluster
from server.database_handler import db_session_maker


@pytest.fixture(scope="module")
def db_session():
    session = db_session_maker()
    yield session
    session.close()


@pytest.fixture
def get_platforms(db_session):
    return db_session.query(Platform).all()


@pytest.fixture
def get_clusters(db_session):
    return {c.id: c.name for c in db_session.query(Cluster).all()}


def test_every_cluster_has_platform(get_platforms, get_clusters):
    by_cluster = {}
    for p in get_platforms:
        by_cluster.setdefault(p.cluster_id, []).append(p)
    for cid, cname in get_clusters.items():
        assert by_cluster.get(cid), f"No platforms found for cluster '{cname}'"


def test_unique_platform_entries(get_platforms):
    seen = set()
    for p in get_platforms:
        key = (p.cluster_id, p.name, p.version)
        assert key not in seen, f"Duplicate platform entry: {key}"
        seen.add(key)


def test_platform_name_not_empty(get_platforms):
    for p in get_platforms:
        assert isinstance(p.name, str) and p.name.strip(), f"Empty or invalid name on id={p.id}"


def test_platform_version_format(get_platforms):
    semver = re.compile(r'^\d+(\.\d+)*$')
    for p in get_platforms:
        assert semver.match(p.version), f"Version '{p.version}' on '{p.name}' is not semver‑like"


def test_shared_platforms_between_clusters(get_platforms):
    name_to_clusters = {}
    for p in get_platforms:
        name_to_clusters.setdefault(p.name, set()).add(p.cluster_id)
    shared = [n for n, cls in name_to_clusters.items() if len(cls) > 1]
    assert shared, "No platform is shared between multiple clusters"


def test_cluster_platform_sets_differ(get_platforms):
    cluster_sets = {}
    for p in get_platforms:
        cluster_sets.setdefault(p.cluster_id, set()).add((p.name, p.version))
    sets = list(cluster_sets.values())
    for i in range(len(sets)):
        for j in range(i + 1, len(sets)):
            assert sets[i] != sets[j], "Two clusters share an identical platform set"


def test_max_platforms_per_cluster(get_platforms, get_clusters):
    by_cluster = {}
    for p in get_platforms:
        by_cluster.setdefault(p.cluster_id, []).append(p)
    for cid, plats in by_cluster.items():
        assert len(plats) <= 10, f"Cluster '{get_clusters[cid]}' has too many platforms ({len(plats)})"
