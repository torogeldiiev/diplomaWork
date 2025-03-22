from flask import Blueprint, jsonify, request
from service_factory import ServiceFactory
from models.cluster import Cluster

# Create the blueprint
cluster_bp = Blueprint('cluster', __name__)
# Initialize the service
service_factory = ServiceFactory()
cluster_handler_service = service_factory.get_clusters_handler_service()

# Define the routes for clusters
@cluster_bp.route("", methods=['GET'])
def get_clusters():
    clusters = cluster_handler_service.get_all_clusters()
    return jsonify([cluster.as_dict() for cluster in clusters])


@cluster_bp.route("/<cluster_id>", methods=['GET'])
def get_cluster_by_id(cluster_id):
    cluster = cluster_handler_service.get_cluster_by_id(cluster_id)
    if not cluster:
        return jsonify({"message": "Cluster not found"}), 404
    return jsonify(cluster.as_dict())


@cluster_bp.route("", methods=['POST'])
def add_cluster():
    data = request.json
    cluster = Cluster(name=data["name"], source_version=data["source_version"], target_version=data["target_version"])
    result = cluster_handler_service.add_cluster(cluster)
    return jsonify(result), 201


@cluster_bp.route("/<cluster_id>", methods=['DELETE'])
def delete_cluster(cluster_id):
    result = cluster_handler_service.delete_cluster(cluster_id)
    if not result:
        return jsonify({"message": "Cluster not found"}), 404
    return jsonify({"message": "Cluster deleted successfully"})
