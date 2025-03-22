from flask import Flask

from models.cluster import Cluster
from service_factory import ServiceFactory
from flask import Flask, Response, jsonify, request, send_from_directory
from flask_restx import Api, Resource, Namespace, fields
from routes.cluster_routes import cluster_bp

app = Flask(__name__)

service_factory = ServiceFactory()
cluster_handler_service = service_factory.get_clusters_handler_service()
jenkins_submitter_service = service_factory.get_jenkins_submitter_service()

api = Api(app, version="1.0", title="Backend API", doc="/api/docs")
# api.add_namespace(cluster_bp)
# app.register_blueprint(cluster_bp)

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


# @api.route("/api/jenkins/trigger")
# class JenkinsTrigger:
#     def post(self) -> Response:
#         job_type = request.json["job_type"]
#         parameters = request.json["parameters"]
#         return jenkins_submitter_service.trigger_job(job_type, parameters)


if __name__ == "__main__":
    app.run(debug=True)
