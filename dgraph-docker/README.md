# Testing Dgraph with a ring test

This example demonstrates how to test ACID compliance with a workload we call the ring test. We test the [Dgraph](https://docs.hypermode.com/dgraph/overview) distributed graph database using this workload. It includes:

- A reproducible cluster setup using Docker Compose.
- A client workload.  
- Example assertions.

Follow the step-by-step tutorial [here](https://antithesis.com/resources/ring_test/).

### Example triage report

The resulting [triage report](https://antithesis.com/docs/reports/#the-triage-report) can be found [here](https://public.antithesis.com/report/pIEU5Hg1buB8V9cCIMhMlvV4/KJlPOcIi0ntEQsp9gOYlZZxg9hOIX3mcck206tMXyTY.html). The report lists all test properties and their status as either passing or failing. In this report, you'll find the `always assertion - Ring held before commit` failing which was a bug found in Dgraph. 

### Architecture overview

The system under test includes:

- 3 [Dgraph Alpha](https://docs.hypermode.com/dgraph/self-managed/dgraph-alpha) server nodes
- 3 [Dgraph Zero](https://docs.hypermode.com/dgraph/self-managed/dgraph-zero) server nodes
- 1 ring test workload container

[Faults](https://antithesis.com/docs/environment/fault_injection/) such as network partitions, restarts, pauses, and more will be introduced automatically by Antithesis.

---

## Prerequisites

You will need:

- Docker and Docker Compose.  
- An Antithesis account and authentication credentials.  
- Access to Antithesis's container registry.

---

## How to run the example

This section explains how to build the example and run it Antithesis. Optionally, you may want to [test locally](#testing-locally-optional) first.

### Build and run in Antithesis

To run the example, first build and push your container images and then submit a test run to Antithesis.

#### Build and push container images

Replace the \<registry\> placeholder with your Antithesis tenant repository: 
```
us-central1-docker.pkg.dev/molten-verve-216720/$TENANT_NAME-repository
```
```shell
docker build -f Dockerfile -t <registry>/dgraph-client:v1
docker push <registry>/dgraph-client:v1

docker build -f Dockerfile.config -t <registry>/dgraph-config:v1
docker push <registry>/dgraph-config:v1
```

#### Run the example on Antithesis

Submit a test run (replace credentials, tenant name, config image, report recipients):
```shell
curl --fail -u '$USER:$PASSWORD' \
-X POST https://$TENANT_NAME.antithesis.com/api/v1/launch/basic_test \
-d '{"params": { "antithesis.description":"basic_test on main",
    "antithesis.duration":"180",
    "antithesis.config_image":"dgraph-config:v1", 
    "antithesis.report.recipients":"foo@email.com;bar@email.com"
    } }'
```

### Testing locally (optional)

It's convenient to check your work locally before starting a full Antithesis test.

This process is described in greater detail [here](https://antithesis.com/docs/test_templates/testing_locally/).

The repo provides various make commands you can use to get this setup running locally.

1. Pull the docker container image, build the workload and bring up the cluster:
    ```shell
    make up 
    ```

2. Build the initial ring:
    ```shell
    make test-first-make-ring
    ```

3. Run multiple ring swaps in parallel indefinitely, you can run this for a few seconds and exit out of the terminal:
    ```shell
    make test-make-swaps
    ```

4. Check that the ring structure is maintained:
    ```shell
    make test-finally-check-ring
    ```

5. (Optional) Run the following to view the SDK assertions locally.
    ```shell
    make view-sdk-logs
    ```

Once the ring test is behaving correctly locally, you can proceed to upload it to Antithesis.


---

## About the example

The example uses the following [Test Composer](https://antithesis.com/docs/test_templates/) commands.

### First command

`first_make_ring.py` is a [first command](https://antithesis.com/docs/test_templates/test_composer_reference/#first-command) that builds the initial ring graph structure with `n` nodes.

### Singleton driver command

`singleton_driver_run_ring.sh` is a [singleton driver](https://antithesis.com/docs/test_templates/test_composer_reference/#singleton-driver) that runs hundreds of processes which each swaps two random nodes in the graph by deleting old relationships and building new ones with the new neighbors. 

### Finally command

`finally_test_ring.py` is a [finally command](https://antithesis.com/docs/test_templates/test_composer_reference/#finally-command) which runs after the swaps to check that the ring structure is still maintained.

It uses [always assertions](https://antithesis.com/docs/properties_assertions/properties/#always-properties) to assert that node swaps are durable and the ring structure is maintained.