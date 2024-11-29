# app.py

from flask import Flask, jsonify
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import os

app = Flask(__name__)

# Initialize Kubernetes client based on the environment
def init_kubernetes():
    try:
        # Try to load in-cluster config (service account)
        config.load_incluster_config()
    except config.ConfigException:
        # Fallback to kubeconfig file for local development
        config.load_kube_config()
    return client.AppsV1Api()

# Initialize the K8s client
k8s_client = init_kubernetes()

@app.route('/deployment-status', methods=['GET'])
def get_deployment_status():
    try:
        deployments = k8s_client.list_deployment_for_all_namespaces(watch=False)
        deployment_statuses = []

        for deployment in deployments.items:
            available_replicas = deployment.status.available_replicas or 0
            desired_replicas = deployment.status.replicas or 0
            status = "Healthy" if available_replicas == desired_replicas else "Degraded"
            
            deployment_statuses.append({
                "deployment_name": deployment.metadata.name,
                "namespace": deployment.metadata.namespace,
                "desired_replicas": desired_replicas,
                "available_replicas": available_replicas,
                "status": status
            })

        return jsonify(deployment_statuses)

    except ApiException as e:
        return jsonify({
            "error": "Failed to connect to the Kubernetes cluster.",
            "details": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)