from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.core.container import DockerContainer

from simple_http_server import SimpleHTTPServer

HOST = 'localhost'
RABBIT_PORT = 5672

def before_all(context):
    # Adding label to identify Docker container as testcontainer container (testcontainers-java does this
    # by default). 
    #
    # Much of the testcontainers-python library is simply a wrapper around Docker SDK for Python. This is 
    # a good example of how to make use of the parameters that the Docker SDK makes available, even if
    # testcontainers doesn't do so explicitly. When using testcontainers-python, it is therefore advisable
    # to be familiar with the Docker SDK (https://docker-py.readthedocs.io/en/stable/containers.html)
    # and the testcontainers-python source code (https://github.com/testcontainers/testcontainers-python).
    #
    context.rabbit = DockerContainer('rabbitmq:3.8.3-management', labels = {"org.testcontainers":"true"}) \
            .with_exposed_ports(RABBIT_PORT)

    context.rabbit.start()

    wait_for_logs(context.rabbit, r"Server startup complete; \d+ plugins started", timeout = 120)

    context.server = SimpleHTTPServer(HOST, 0, context.rabbit.get_exposed_port(RABBIT_PORT))
    context.server.serve()
