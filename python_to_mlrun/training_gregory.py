from cloudpickle import dumps
from mlrun import get_or_create_ctx
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, f1_score
from sklearn.preprocessing import LabelEncoder


def handler(context):
    """
    Read CSV file and save it to MLRun artifacts DB
    """
    context.logger.info("Logging Dataset")
    context.log_dataset("data", df=df, format="csv", index=False)




    # Load data
    context.logger.info("Loading Data")
    df = context.inputs["data"].as_df()
    X = df.drop(["class"], axis=1).values
    y = LabelEncoder().fit_transform(df["class"])

    # ML training code
    context.logger.info("Training Model")
    clf = SVC().fit(X, y)
    y_pred = clf.predict(X)

    # Log metrics to MLRun DB
    context.logger.info("Evaluating Model")
    acc = accuracy_score(y, y_pred)
    f1 = f1_score(y, y_pred, average="micro")
    context.log_result("accuracy", acc)
    context.log_result("f1_score", f1)
    context.set_label("framework", "sklearn")

    # Log model to MLRun DB
    context.logger.info("Saving Model and Params")
    context.log_model(
        "clf",
        body=dumps(clf),
        model_file="model.pkl",
        metrics={"accuracy": acc},
        parameters=clf.get_params(),
        labels={"framework": "sklearn"},
    )
