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
project_path = "./hadoop_hack"
skproj = new_project(name=project_name, context=project_path)
artifact_path = os.getenv("MLRUN_ARTIFACT_PATH")
mlconf.dbpath = os.getenv("MLRUN_DBPATH")

print(f"Project name: {project_name}")
print(f"Artifacts path: {artifact_path}\nMLRun DB path: {mlconf.dbpath}")

# Setup task
task = NewTask(
    name="hdfs-submit",
    project=os.getenv("MLRUN_PROJECT_NAME"),
    params={"hdfs_cmd": "hadoop fs -ls", "shell_pod_name": "nick-shell"},
    handler="hdfs_submit",
    artifact_path=artifact_path,
)

# Create MLRun job
fn = code_to_function(
    name="hdfs-submit",
    filename=f"{project_path}/hadoop.py",
    handler="hdfs_submit",
    kind="job",
)

fn.spec.service_account = "mlrun-api"
fn.spec.build.image = "mlrun/mlrun"
fn.apply(mount_v3io())
fn.deploy()

# Run MLRun job on cluster
run = fn.run(runspec=task)
# print("\nRun Outputs:\n", run.outputs)