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
    df = pd.read_csv("/User/demos/titanic.csv")


    context.logger.info("Saving Dataset")
    context.log_dataset("data", df=df, format="csv", index=False)
