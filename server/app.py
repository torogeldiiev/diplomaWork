import os

from flask import Flask

from models.cluster import Cluster
from service_factory import ServiceFactory
from flask import Flask, Response, jsonify, request, send_from_directory
from flask_restx import Api, Resource
from config import FLASK_APP_DEBUG
from flask_cors import CORS
import logging
import time
from log_utils import init_logger

init_logger()

logger = logging.getLogger(__name__)
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
        result = jenkins_submitter_service.trigger_job(job_type, parameters)
        logger.info(f"Jenkins trigger result: {result}")
        if isinstance(result, dict) and result.get("success"):
            build_number = result.get('data', {}).get('queue_number')
            logger.info(f"Jenkins build number {build_number}")
            job_type = result.get('data', {}).get('job_name')
            created_execution = jenkins_submitter_service.create_execution_entry(job_type, build_number, parameters)

            while True:
                status = jenkins_submitter_service.get_job_status(job_type, build_number)
                if status != "IN_PROGRESS":
                    break
                time.sleep(15)
            jenkins_submitter_service.update_running_execution(created_execution, status)
            return jsonify(result)
        else:
            return jsonify({
                "success": False,
                "message": "Invalid response from Jenkins service"
            })


@api.route("/api/jobs")
class JobsList(Resource):
    def get(self) -> Response:
        jobs = jenkins_submitter_service.list_jobs_with_parameters()
        return jsonify(jobs)


@api.route("/api/clusters")
class ClustersList(Resource):
    def get(self) -> Response:
        """Get all clusters"""
        clusters = cluster_handler_service.get_all_clusters()
        return jsonify(clusters)


@api.route("/api/jenkins/job-results/<string:job_type>/<int:build_number>")
class JenkinsJobResults(Resource):
    def get(self, job_type: str, build_number: int) -> Response:
        result = jenkins_submitter_service.get_test_results_for_build(job_type, build_number)
        logger.info("Jenkins job results: %s", result)
        return jsonify(result)


@api.route("/api/executions/recent")
class RecentExecutions(Resource):
    def get(self):
        res = jenkins_submitter_service.get_recent_executions()
        logger.info("Jenkins recent executions: %s", res)
        return jsonify(res)


@app.route('/api/job-history', methods=['GET'])
def job_history():
    job_name = request.args.get('jobId')
    days = int(request.args.get('days', 7))
    if not job_name:
        return jsonify(success=False, message="Missing jobId"), 400

    stats = jenkins_submitter_service.get_job_statistics(job_name, days)
    return jsonify(stats)



if __name__ == "__main__":
    app.run(debug=FLASK_APP_DEBUG)
