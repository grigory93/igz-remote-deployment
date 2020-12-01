import os

from dotenv import load_dotenv
from kfp import dsl
from mlrun import NewTask, mount_v3io

load_dotenv("..")

# Define pipeline
funcs = {}

# Configure function resources and local settings
def init_functions(functions: dict, project=None, secrets=None):
    for fn in functions.values():
        fn.apply(mount_v3io())


# Create a Kubeflow Pipelines pipeline
@dsl.pipeline(name="Demo Remote Kubeflow Pipeline")
def kfpipeline():

    params = {
        "v3io_username": os.getenv("V3IO_USERNAME"),
        "v3io_access_key": os.getenv("V3IO_ACCESS_KEY"),
        "presto_api": os.getenv("PRESTO_API"),
        "presto_table": os.getenv("PRESTO_TABLE"),
    }

    # Get data via Presto query
    data = funcs["get-data"].as_step(params=params, outputs=["data"])

    # Train model
    train = funcs["train-model"].as_step(
        inputs={"data": data.outputs["data"]}, outputs=["clf", "accuracy", "f1_score"]
    )
