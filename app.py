# app.py

from flask import Flask, jsonify
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import os
import openai
import asyncio
from functools import lru_cache
import time

app = Flask(__name__)

# Initialize OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

def init_kubernetes():
    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()
    return client.AppsV1Api()

k8s_client = init_kubernetes()

@lru_cache(maxsize=128)  # Cache the results of this function
def get_deployments():
    return k8s_client.list_deployment_for_all_namespaces(watch=False)

@app.route('/deployment-status', methods=['GET'])
def get_deployment_status():
    try:
        deployments = get_deployments()
        
        total_deployments = len(deployments.items)
        healthy_count = 0
        degraded_deployments = []

        for deployment in deployments.items:
            available_replicas = deployment.status.available_replicas or 0
            desired_replicas = deployment.status.replicas or 0
            
            if available_replicas == desired_replicas:
                healthy_count += 1
            else:
                degraded_deployments.append({
                    "name": deployment.metadata.name,
                    "namespace": deployment.metadata.namespace,
                    "available": available_replicas,
                    "desired": desired_replicas
                })

        return jsonify({
            "summary": {
                "total_deployments": total_deployments,
                "healthy_deployments": healthy_count,
                "degraded_deployments": len(degraded_deployments),
                "cluster_health": "Healthy" if len(degraded_deployments) == 0 else "Degraded"
            },
            "issues": degraded_deployments if degraded_deployments else None
        })

    except ApiException as e:
        return jsonify({
            "error": "Failed to connect to the Kubernetes cluster.",
            "details": str(e)
        }), 500

@app.route('/insights', methods=['GET'])
async def get_insights():
    try:
        deployments = get_deployments()
        cluster_state = []
        
        for deployment in deployments.items:
            available_replicas = deployment.status.available_replicas or 0
            desired_replicas = deployment.status.replicas or 0
            
            if available_replicas != desired_replicas:
                cluster_state.append({
                    "deployment": deployment.metadata.name,
                    "namespace": deployment.metadata.namespace,
                    "available": available_replicas,
                    "desired": desired_replicas,
                    "conditions": [cond.to_dict() for cond in deployment.status.conditions]
                })

        if not cluster_state:
            return jsonify({
                "message": "All deployments are healthy",
                "insights": None
            })

        # Prepare prompt for GPT
        prompt = f"""
        As a Kubernetes expert, analyze this cluster state and provide actionable insights:
        {cluster_state}
        
        Please provide:
        1. A brief analysis of the issues
        2. Potential root causes
        3. Specific troubleshooting steps
        4. Recommended kubectl commands
        
        Format the response in a clear, structured way.
        """

        # Use asyncio to call OpenAI API asynchronously
        response = await asyncio.to_thread(openai.ChatCompletion.create,
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a Kubernetes expert providing analysis and actionable insights."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        return jsonify({
            "insights": response.choices[0].message.content
        })

    except ApiException as e:
        return jsonify({
            "error": "Failed to connect to the Kubernetes cluster.",
            "details": str(e)
        }), 500
    except Exception as e:
        return jsonify({
            "error": "Failed to generate insights.",
            "details": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK"})

@app.route('/refresh-deployments', methods=['POST'])
def refresh_deployments():
    global deployments_cache
    deployments_cache["data"] = k8s_client.list_deployment_for_all_namespaces(watch=False)
    deployments_cache["timestamp"] = time.time()
    return jsonify({"message": "Deployments cache refreshed."}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)