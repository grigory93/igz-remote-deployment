import pandas as pd
from pyhive import presto


def handler(context, v3io_username, v3io_access_key, presto_api, presto_table):
    """
    Query data from KV table via Presto.
    """
    context.logger.info("Connecting to Presto")
    req_kw = {
        "auth": (v3io_username, v3io_access_key),
        "verify": False,
    }
    conn = presto.connect(
        presto_api,
        port=443,
        username=v3io_username,
        protocol="https",
        requests_kwargs=req_kw,
    )
    context.logger.info("Querying Presto")
    df = pd.read_sql_query(f"select * from {presto_table}", conn)

    context.logger.info("Logging Dataset")
    context.log_dataset("data", df=df, format="csv", index=False)
