from mlrun import get_or_create_ctx
from kubernetes import config, client
from kubernetes.stream import stream
import yaml
from pathlib import Path
import os


class K8SClient(object):
    def __init__(self, logger, namespace="default-tenant", config_file=None):
        self.namespace = namespace
        self.logger = logger
        self._init_k8s_config(config_file)
        self.v1api = client.CoreV1Api()

    def _init_k8s_config(self, config_file):
        try:
            config.load_incluster_config()
            self.logger.info("using in-cluster config.")
        except Exception:
            try:
                config.load_kube_config(config_file)
                self.logger.info("using local kubernetes config.")
            except Exception:
                raise RuntimeError(
                    "cannot find local kubernetes config file,"
                    " place it in ~/.kube/config or specify it in "
                    "KUBECONFIG env var"
                )

    def get_shell_pod_name(self, pod_name="shell"):
        shell_pod = self.v1api.list_namespaced_pod(namespace=self.namespace)
        for i in shell_pod.items:
            if pod_name in i.metadata.name:
                self.logger.info(
                    "%s\t%s\t%s"
                    % (i.status.pod_ip, i.metadata.namespace, i.metadata.name)
                )
                shell_name = i.metadata.name
                break
        return shell_name

    def exec_shell_cmd(self, cmd, shell_pod_name="shell"):
        shell_name = self.get_shell_pod_name(shell_pod_name)
        # Calling exec and waiting for response
        exec_command = ["/bin/bash", "-c", cmd]
        resp = stream(
            self.v1api.connect_get_namespaced_pod_exec,
            shell_name,
            self.namespace,
            command=exec_command,
            stderr=True,
            stdin=False,
            stdout=True,
            tty=False,
            _preload_content=False,
        )

        stderr = []
        stdout = []
        while resp.is_open():
            resp.update(timeout=None)
            if resp.peek_stderr():
                stderr.append(resp.read_stderr())
            if resp.peek_stdout():
                stdout.append(resp.read_stdout())

        err = resp.read_channel(3)
        err = yaml.safe_load(err)
        if err["status"] == "Success":
            rc = 0
        else:
            rc = int(err["details"]["causes"][0]["message"])

        stdout_formated = ""
        for each in stdout:
            stdout_formated += each
        self.logger.info("STDOUT: %s" % stdout_formated)
        self.logger.info("RC: %s" % rc)

        stderr_formated = ""
        for each in stderr:
            stderr_formated += each
        if rc != 0:
            self.logger.info("STDERR: %s" % stderr_formated)
            raise Exception("Execution_error", stderr_formated + stdout_formated)


def hdfs_submit(context, hdfs_cmd, shell_pod_name="shell"):
    """hdfs_submit function

    submiting spark via shell

    :param name:        A name of your application.
    :param hdfs_cmd:    HDFS command to run on shell
    :param shell_pod_name: Pod to run HDFS command on
    """

    context.logger.info(f"Submiting: {hdfs_cmd}")

    cli = K8SClient(context.logger)
    cli.exec_shell_cmd(hdfs_cmd, shell_pod_name=shell_pod_name)