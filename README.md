# tescontainers-python POC

The aim of this project is to POC the use of 
[testcontainers-python](https://testcontainers-python.readthedocs.io/en/latest/) for integration testing python code. 
The project aims to demonstrate the following:

1. Integration of testcontainers-python with [behave](https://behave.readthedocs.io/en/latest/) (or similar python 
Cucumber port).
2. The spinning up of a generic container - running RabbitMQ in this case.
3. Waiting for the application running in the container to finish initializing.
4. Interacting with the application running inside the test container.

## Running

To run the project code and the associated integration tests, initialize a virtual environment.

    $ python3 -m venv ./.venv && source .venv/bin/activate && pip install -r requirements.txt
    (.venv) $
    
It is assumed that docker will have been installed and is running on the machine being used.
    
### simple_http_server.py

`simple_http_server.py` is the simple application that is being tested. It is a very simple web server that returns
'Hello, world!' in response to `GET` requests and adds the contents of the request body to RabbitMQ when a `POST` request
is received. 

To manually test the application, spin up a docker container running RabbitMQ:

    $ docker run -d --hostname my-rabbit -p 15672:15672 -p 5672:5672 --name some-rabbit rabbitmq:3.8.3-management
    
Run the simple web server specifying the http port to listen for requests on and the rabbit port to send messages on:

    $ source .venv/bin/activate
    (.venv) $ python3 simple_http_server.py 8082 5672
    
Interact with the web server using cURL:

    $ curl http://localhost:8082
      Hello, world!
    $
    $ curl -v http://localhost:8082 -d'[{"hello":"world"}]'
      *   Trying ::1...
      * TCP_NODELAY set
      * Connection failed
      * connect to ::1 port 8082 failed: Connection refused
      *   Trying 127.0.0.1...
      * TCP_NODELAY set
      * Connected to localhost (127.0.0.1) port 8082 (#0)
      > POST / HTTP/1.1
      > Host: localhost:8082
      > User-Agent: curl/7.64.1
      > Accept: */*
      > Content-Length: 19
      > Content-Type: application/x-www-form-urlencoded
      > 
      * upload completely sent off: 19 out of 19 bytes
      * HTTP 1.0, assume close after body
      < HTTP/1.0 201 Created
      < Server: BaseHTTP/0.6 Python/3.7.7
      < Date: Fri, 27 Mar 2020 13:33:16 GMT
      < 
      * Closing connection 0
    $
    
Browse to http://localhost:15672/#/queues/%2F/test_queue using the credentials guest:guest to view the queue and see 
the 'hello world' message added to the queue.

### Running the integration tests

To run the integration tests making use of testcontainers-python, activate the virtual environment and run `behave`:

    $ source .venv/bin/activate
    (.venv) $ behave

    Pulling image rabbitmq:3.8.3-management
    ⠇
    Container started:  00c3b92042
    Feature: Testcontainers POC: demonstrates use of Testcontainers for integration testing # features/everything.feature:1

      Scenario: When a GET request is made to the simple webserver, a successful 'Hello World' response is returned  # features/everything.feature:3
        When a GET request is made to the simple webserver                                                           # features/steps/steps.py:12 0.004s
        Then the webserver will respond with a HTTP status of "200"                                                  # features/steps/steps.py:27 0.000s
        And the response body will contain "Hello, world!"                                                           # features/steps/steps.py:32 0.000s

      Scenario: When a POST request is made to the simple webserve, the request body is added to the RabbitMQ queue  # features/everything.feature:8
        When a POST request is made to the simple webserver                                                          # features/steps/steps.py:17 0.033s
        Then the webserver will respond with a HTTP status of "201"                                                  # features/steps/steps.py:27 0.000s
        And the response body will be empty                                                                          # features/steps/steps.py:37 0.000s
        And the request body is added to the RabbitMQ queue                                                          # features/steps/steps.py:42 0.027s

    1 feature passed, 0 failed, 0 skipped
    2 scenarios passed, 0 failed, 0 skipped
    7 steps passed, 0 failed, 0 skipped, 0 undefined
    Took 0m0.065s
    (.venv) $

