import os
from flask import Flask, jsonify
from kubernetes import client, config

app = Flask(__name__)

# Initialize Kubernetes in-cluster configuration
try:
    config.load_incluster_config()
except config.ConfigException:
    # Fallback for local development/testing outside the cluster
    try:
        config.load_kube_config()
    except Exception:
        print("[WARNING] Could not configure Kubernetes client. API calls will fail.")

k8s_api = client.CoreV1Api()

@app.route('/health', methods=['GET'])
def health():
    """
    Returns basic liveness and readiness health status.
    """
    return jsonify({
        "status": "healthy",
        "service": "k8s-node-app"
    }), 200

@app.route('/nodes', methods=['GET'])
def get_nodes():
    """
    Fetches all Kubernetes cluster nodes and flags the node running the current pod.
    """
    try:
        # Retrieve the node name where the current pod is running via Downward API env variable
        current_node_name = os.getenv("NODE_NAME", "unknown")

        # Query the Kubernetes API Server for the list of nodes
        nodes_list = k8s_api.list_node()

        cluster_nodes = []
        for node in nodes_list.items():
            name = node.metadata.name

            # Extract node readiness status
            is_ready = "NotReady"
            for condition in node.status.conditions:
                if condition.type == 'Ready':
                    is_ready = "Ready" if condition.status == 'True' else "NotReady"
                    break

            cluster_nodes.append({
                "name": name,
                "status": is_ready,
                "is_current_pod_node": name == current_node_name
            })

        return jsonify({
            "current_pod_node": current_node_name,
            "total_nodes_count": len(cluster_nodes),
            "nodes": cluster_nodes
        }), 200

    except Exception as e:
        print(f"[ERROR] Failed to query Kubernetes API: {str(e)}")
        return jsonify({
            "error": "Internal Server Error",
            "message": "Make sure the Pod has a ServiceAccount with proper RBAC permissions to list nodes."
        }), 500

if __name__ == '__main__':
    # Run production-ready lightweight server inside container
    app.run(host='0.0.0.0', port=8080)