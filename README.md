# Kubernetes Deployment Status API

## Overview
This Python-based web application provides the deployment status of Kubernetes workloads running on an Azure Kubernetes Service (AKS) cluster. It exposes a REST API endpoint to fetch the deployment status, making it easy to monitor Kubernetes workloads externally.

## Features
1. **Fetch Deployment Status**: Provides details like deployment name, namespace, desired vs. available replicas, and status (e.g., Healthy, Degraded).
2. **Health Check Endpoint**: Ensures the app is running and accessible.
3. **Error Handling**: Handles cluster connection issues and missing deployment resources gracefully.
4. **Logging**: Logs API requests and responses for debugging purposes.

## API Endpoints

### 1. `/deployment-status`
- **Method**: `GET`
- **Description**: Fetches the deployment status of all workloads in the AKS cluster.
- **Response Example**:
  ```json
  [
    {
      "deployment_name": "app1",
      "namespace": "default",
      "desired_replicas": 3,
      "available_replicas": 3,
      "status": "Healthy"
    },
    {
      "deployment_name": "app2",
      "namespace": "default",
      "desired_replicas": 2,
      "available_replicas": 1,
      "status": "Degraded"
    }
  ]
  ```

### 2. `/health`
- **Method**: `GET`
- **Description**: Verifies that the application is running correctly.
- **Response Example**:
  ```json
  { "status": "OK" }
  ```

## Assumptions
- The app runs in an environment with access to the AKS cluster via a kubeconfig file or Azure authentication.
- Necessary Kubernetes permissions (`get`, `list` on deployments) are granted to the app.
- The AKS cluster is pre-configured and operational.

## Setup Instructions

### Prerequisites
1. Python 3.8+
2. Docker (optional, for containerized deployment)
3. Access to an AKS cluster and its kubeconfig file or Azure credentials.
4. Necessary permissions to fetch deployment details.

### Local Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set environment variables:
   - `KUBECONFIG`: Path to your kubeconfig file (if not default).
   ```bash
   export KUBECONFIG=/path/to/kubeconfig
   ```
5. Run the application:
   ```bash
   python app.py
   ```
6. Access the API at `http://localhost:5000/deployment-status`.

### Docker Setup
1. Build the Docker image:
   ```bash
   docker build -t kubernetes-deployment-status .
   ```
2. Run the container:
   ```bash
   docker run -d -p 5000:5000 -e KUBECONFIG=/path/to/kubeconfig -v /path/to/kubeconfig:/path/to/kubeconfig kubernetes-deployment-status
   ```
3. Access the API at `http://localhost:5000/deployment-status`.

## Configuration
- **Environment Variables**:
  - `KUBECONFIG`: Path to the kubeconfig file.
  - Any additional Azure credentials if required (e.g., Managed Identity settings).

## Example Response
### Successful Response:
```json
[
  {
    "deployment_name": "app1",
    "namespace": "default",
    "desired_replicas": 3,
    "available_replicas": 3,
    "status": "Healthy"
  }
]
```
### Error Response:
```json
{
  "error": "Failed to connect to the Kubernetes cluster."
}
```

## Technologies Used
- **Python**: Core programming language.
- **Flask**: Lightweight web framework.
- **Kubernetes Python Client**: For interacting with the AKS cluster.
- **Docker**: Containerized deployment.

## Future Enhancements
- Add support for namespace-specific queries.
- Implement authentication for the API endpoints.
- Add Prometheus/Grafana integration for monitoring.

## License
This project is licensed under the [MIT License](LICENSE).

---
For any issues or questions, please open an issue in the repository.
ss