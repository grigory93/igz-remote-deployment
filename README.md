# Iguazio Remote Deployment Example

### Quick-Start
1. Copy `.env-default` to `.env` and update respective values. View below for full overview of what each value means.
2. Install requirements via `requirements.txt`.
3. Run `deploy.py` for Iris example.

### Notes for Customizing Pipeline
- Seperate different components into their own files for simplicity
    - Place component files in `project` directory or update path accordingly
- All pipeline code and logic goes into `pipeline.py`
- Anything regarding MLRun project, MLRun functions, or running Kubeflow Pipeline belongs in `deploy.py`

### File Descriptions
- `deploy.py`
    - File that handles actual deployment. Creates MLRun project, builds custom Docker image, imports MLRun functions from Python files, loads and runs Kubeflow Pipeline
- `project/pipeline.py`
    - Kubeflow Pipeline as Python code. Implements logic and passing of items from component to component. Assumes that specific functions exist (created in `deploy.py`).
- `.env`
    - Environment file used by `python-dotenv`. Includes MLRun, V3IO, Presto, and Docker configuration. When moving to a new environment, these values must be updated.
- `project/project.yaml`
    - YAML version of MLRun project. Automatically generated and used for deployment.

### Kubeflow Pipeline Component Descriptions
- `project/data.py`
    - Queries data from Presto and saves to `.csv` file as artifact on Iguazio platform and in MLRun database.
- `project/training.py`
    - Performs training via SKLearn using data from previous step. Logs model file (pickle), model parameters, and model metrics as artifacts on Iguazio platform and in MLRun database.

### Environment Variable Descriptions
- MLRun
    - `MLRUN_DBPATH`: Path to MLRun database located on cluster. For storing/retrieving models, metrics, datasets, runs, etc.
    - `MLRUN_ARTIFACT_PATH`: Path to MLRun artifact path located on cluster. Directory that stores artifacts such as datasets, models, etc. from pipeline runs.
    - `MLRUN_PROJECT_NAME`: Name of MLRun project. Will be shown in web GUI.
    - `MLRUN_PROJECT_PATH`: Path to MLRun `project` directory located on remote machine. Where Python/YAML files will be searched for when deploying.
- V3IO
    - `V3IO_USERNAME`: V3IO username for authentication purposes.
    - `V3IO_API`: V3IO API endpoint located on cluster.
    - `V3IO_ACCESS_KEY`: V3IO Access Key for authentication purposes. Essentially a password, do not distribute or upload to source control.
- Presto
    - `PRESTO_API`: Presto API endpoint located on cluster.
    - `PRESTO_TABLE`: Name of table to query via Presto.
- Docker
    - `DOCKER_IMAGE`: Name for newly-created custom Docker image.

### TODO
- Implement testing via PyTest
- Implement examples for Dask/Horovod
