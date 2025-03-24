import os

from flask import Flask

from models.cluster import Cluster
from service_factory import ServiceFactory
from flask import Flask, Response, jsonify, request, send_from_directory
from flask_restx import Api, Resource, Namespace, fields
from config import FLASK_APP_DEBUG, JENKINS_PROJECT_NAMES
from flask_cors import CORS
import logging
from log_utils import init_logger

init_logger()
app = Flask(__name__, static_folder="../client/build")
CORS(app, resources={r"/api/*": {"origins": "*"}})
service_factory = ServiceFactory()
cluster_handler_service = service_factory.get_clusters_handler_service()
jenkins_submitter_service = service_factory.get_jenkins_submitter_service()

api = Api(app, version="1.0", title="Backend API", doc="/api/docs")


@app.route("/", defaults={"path": ""}, strict_slashes=False)
@app.route("/<path:path>", strict_slashes=False)
def catch_all(path):
    # Serve the index.html if path is empty or if the file exists in the build directory
    if path == "" or os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path or "index.html")
    return send_from_directory(app.static_folder, "index.html")


@api.route("/api/clusters/add")
class ClusterHandler(Resource):
    def post(self) -> Response:
        name = request.json["name"]
        source_version = request.json["source_version"]
        target_version = request.json["target_version"]
        cluster = Cluster(name=name, source_version=source_version, target_version=target_version)
        return cluster_handler_service.add_cluster(cluster)


@api.route("/api/clusters/get_by/<cluster_id>")
class ClusterHandler(Resource):
    def get(self, cluster_id) -> Response:
        cluster = cluster_handler_service.get_cluster_by_id(cluster_id)
        return cluster


@api.route("/api/clusters/delete/<cluster_id>")
class ClusterHandler(Resource):
    def delete(self, cluster_id) -> Response:
        msg = cluster_handler_service.delete_cluster(cluster_id)
        return msg


@api.route("/api/jenkins/trigger")
class JenkinsTrigger(Resource):
    def post(self) -> Response:
        job_type = request.json["job_type"]
        parameters = request.json["parameters"]
        return jenkins_submitter_service.trigger_job(job_type, parameters)


@api.route("/api/jobs")
class JobsList(Resource):
    def get(self) -> Response:
        jobs = [
            {
                "id": "Configdiff",
                "name": "cdpd-trigger-confdiff-test",
                "parameters": {
                    "source": "",
                    "target": "",
                    "dry_run": "true",
                    "launch_multiplier": "1"
                }
            },
            {
                "id": "Platform",
                "name": "cdpd-trigger-platform-tests",
                "parameters": {
                    "source": "",
                    "target": "",
                    "dry_run": "true",
                    "launch_multiplier": "1"
                }
            }
        ]
        return jsonify(jobs)


@api.route("/api/clusters")
class ClustersList(Resource):
    def get(self) -> Response:
        """Get all clusters"""
        clusters = cluster_handler_service.get_all_clusters()
        return jsonify(clusters)


if __name__ == "__main__":
    app.run(debug=FLASK_APP_DEBUG)
