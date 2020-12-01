import os
from os import getenv, path

from dotenv import load_dotenv
from mlrun import (
    NewTask,
    code_to_function,
    get_run_db,
    import_function,
    mlconf,
    mount_v3io,
    new_function,
    new_project,
    run_local,
    wait_for_pipeline_completion,
)

# Load environment variables
load_dotenv()

# Setup Project
project_name = os.getenv("MLRUN_PROJECT_NAME")
project_path = os.getenv("MLRUN_PROJECT_PATH")
skproj = new_project(name=project_name, context=project_path)
artifact_path = os.getenv("MLRUN_ARTIFACT_PATH")
mlconf.dbpath = os.getenv("MLRUN_DBPATH")
image = os.getenv("DOCKER_IMAGE")

print(f"Project name: {project_name}")
print(f"Artifacts path: {artifact_path}\nMLRun DB path: {mlconf.dbpath}")
print("Docker Image:", image)

# # Build Docker Image (only needs to be run once)
# build_image = new_function(name="build-image", kind="job")
# build_image.build_config(
#     image=f".mlrun/{image}", base_image="mlrun/mlrun", commands=["pip install pyhive"]
# )
# build_image.deploy(with_mlrun=False)

# Import functions
data_fn = code_to_function(
    filename=f"{project_path}/data.py",
    name="get-data",
    kind="job",
    image=f".mlrun/{image}",
    handler="handler",
)
train_fn = code_to_function(
    filename=f"{project_path}/training.py",
    name="train-model",
    kind="job",
    image=f".mlrun/{image}",
    handler="handler",
)
skproj.set_function(data_fn)
skproj.set_function(train_fn)

# Set Pipeline
skproj.set_workflow("main", "pipeline.py")
skproj.save(f"{project_path}/project.yaml")

# Run Pipeline
run_id = skproj.run(
    "main",
    arguments={},
    artifact_path=artifact_path,
    dirty=True,
)


wait_for_pipeline_completion(run_id)
db = get_run_db().connect()
db.list_runs(project=project_name, labels=f"workflow={run_id}").show()
