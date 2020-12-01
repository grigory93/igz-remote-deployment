import os
from os import getenv, path

from dotenv import load_dotenv
from mlrun import (
    run_local,
    NewTask,
    mlconf,
    import_function,
    mount_v3io,
    new_project,
    code_to_function,
)

# Load environment variables
load_dotenv()

# Setup Project
project_name = os.getenv("MLRUN_PROJECT_NAME")
project_path = "./python_to_mlrun"
skproj = new_project(name=project_name, context=project_path)
artifact_path = os.getenv("MLRUN_ARTIFACT_PATH")
mlconf.dbpath = os.getenv("MLRUN_DBPATH")

print(f"Project name: {project_name}")
print(f"Artifacts path: {artifact_path}\nMLRun DB path: {mlconf.dbpath}")

# Setup task
inputs = {"data": "https://datahub.io/machine-learning/iris/r/iris.csv"}
task = NewTask(
    name="training-demo",
    project=project_name,
    handler="handler",
    artifact_path=artifact_path,
    inputs=inputs,
)

# Create MLRun job
fn = code_to_function(
    name="train_model",
    filename=f"{project_path}/training.py",
    handler="handler",
    kind="job",
)
fn.spec.build.image = "mlrun/mlrun"
fn.apply(mount_v3io())
fn.deploy()

# Run MLRun job on cluster
run = fn.run(runspec=task)
print("\nRun Outputs:\n", run.outputs)