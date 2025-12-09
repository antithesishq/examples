# Etcd with Docker Compose

This example demonstrates how to bring a system under test with Antithesis. It includes:

- A reproducible 3-node etcd cluster setup using Docker Compose.
- A basic client workload.
- Example assertions.

Follow the step-by-step tutorial [here](https://antithesis.com/docs/tutorials/etcd_docker/).

### Example triage report

The resulting [triage report](https://antithesis.com/docs/reports/#the-triage-report) can be found [here](https://public.antithesis.com/report/Zm0x1mKtmL7CI_UKdmpgNIne/G9mqeYWiFWoxwxgxLu-YFQVzxUAUujlwJmj5Hnzr7Jc.html). The report highlights the test properties that failed during the test run.

### Architecture overview

The system under test includes:

- **3 etcd server nodes** (`etcd0`, `etcd1`, `etcd2`).
- **2 client containers** that perform read/write operations.
- **A health-checker** that prompts Antithesis when the system is ready for testing.

[Faults](https://antithesis.com/docs/environment/fault_injection/) such as network partitions, restarts, pauses, and more will be introduced automatically by Antithesis.

## Prerequisites

You will need:

- Docker and Docker Compose.
- An Antithesis account and authentication credentials.
- Access to Antithesis's container registry.

## How to run the example

This section explains how to build the example and run it in Antithesis. Optionally, you may want to [test locally](#testing-locally-optional) first.

### Build and run in Antithesis

To run the example, first build and push your container images and then submit a test run to Antithesis.

#### Build and push container images

Replace the \<registry\> placeholder with your Antithesis tenant repository: 

```
us-central1-docker.pkg.dev/molten-verve-216720/$TENANT_NAME-repository
```

```shell
docker build -f Dockerfile.health-checker -t <registry>/etcd-health-checker:v1
docker push <registry>/etcd-health-checker:v1

docker build -f Dockerfile.client -t <registry>/etcd-client:v1
docker push <registry>/etcd-client:v1

docker build -f Dockerfile.config -t <registry>/etcd-config:v1
docker push <registry>/etcd-config:v1
```

#### Run the example on Antithesis

Submit a test run (replace credentials, tenant name, config image, report recipients):

```shell
curl --fail -u '$USER:$PASSWORD' \
-X POST https://$TENANT_NAME.antithesis.com/api/v1/launch/basic_test \
-d '{"params": { "antithesis.description":"basic_test on main",
    "antithesis.duration":"240",
    "antithesis.config_image":"etcd-config:v1", 
    "antithesis.report.recipients":"foo@email.com;bar@email.com"
    } }'
```

### Testing locally (optional)

It's convenient to check your work locally before starting a full Antithesis test.

This process is described in greater detail [here](https://antithesis.com/docs/test_templates/testing_locally/).

1. Pull the etcd image:

    ```shell
    docker pull bitnamilegacy/etcd:3.5
    ```

2. Build container images (health-checker, client):

    ```shell
    docker build . -f Dockerfile.health-checker -t etcd-health-checker:v1
    docker build . -f Dockerfile.client -t etcd-client:v1
    ```

3. Bring up the system. Run the following command from the config directory containing the `docker-compose.yaml` file:

    ```shell
    docker-compose up
    ```

4. Verify health:  
   Check the output of the above step to find a printed `cluster is healthy`  
     
5. Run the test command locally:  
   After the cluster is healthy, you can run the parallel driver 1 to many times via docker exec.  

    ```shell
    docker exec client1 /opt/antithesis/test/v1/main/parallel_driver_generate_traffic.py
    ```

    ```shell
    docker exec client2 /opt/antithesis/test/v1/main/parallel_driver_generate_traffic.py
    ```

Once the cluster is behaving correctly locally, you can proceed to upload it to Antithesis. (Note that SDK assertions won't be evaluated locally.)