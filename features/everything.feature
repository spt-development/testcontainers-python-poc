Feature: Testcontainers POC: demonstrates use of Testcontainers for integration testing

  Scenario: When a GET request is made to the simple webserver, a successful 'Hello World' response is returned
    When a GET request is made to the simple webserver
    Then the webserver will respond with a HTTP status of "200"
    And the response body will contain "Hello, world!"

  Scenario: When a POST request is made to the simple webserve, the request body is added to the RabbitMQ queue
    When a POST request is made to the simple webserver
    Then the webserver will respond with a HTTP status of "201"
    And the response body will be empty
    And the request body is added to the RabbitMQ queue
