# Etcd

This example demonstrates how to bring a system under test with Antithesis. It includes:

- A reproducible 3-node etcd cluster setup using Docker Compose.
- A basic client workload.
- Example assertions.

Follow the step-by-step tutorial [here](https://antithesis.com/docs/tutorials/etcd_kubernetes/).

## Example triage report
The resulting [triage report](https://antithesis.com/docs/reports/#the-triage-report) can be found [here](https://public.antithesis.com/report/F196l8feJ70SBfDIfB0Ih3I3/-aEZKGBnQP9SmqrER3PFHhtuRxkd3fwK0meEUz6Qma8.html). The report highlights the test properties that failed during the test run.

## Architecture Overview

The system under test includes:

- **3 etcd server nodes** (`etcd0`, `etcd1`, `etcd2`).
- **2 client containers** that perform read/write operations.

[Faults](https://antithesis.com/docs/environment/fault_injection/) such as network partitions, restarts, pauses, and more will be introduced automatically by Antithesis.

---

## Prerequisites

You will need:

- Kubernetes.  
- An Antithesis account and authentication credentials.  
- Access to Antithesis’s container registry.

---

## Testing Locally

It's convenient to check your work locally before starting a full Antithesis test.

This process is [described in greater detail here](https://antithesis.com/docs/tutorials/k8s-cluster-setup/#start-the-cluster-locally) and [here](https://antithesis.com/docs/test_templates/testing_locally/)

1. Pull the etcd image:

```shell
docker pull bitnamilegacy/etcd:3.5
```

2. Build the client image: 

    `docker build -f client/Dockerfile.client -t etcd-client:k8s client/`

3. Deploy your manifests. 

    `kubectl apply -f manifests/` 

    or if you're using `kapp`:

    `kapp deploy -a app-name -f manifests/ --yes`

4. Check your rollout status
    ```
    kubectl rollout status statefulset/etcd --timeout=3m
    kubectl get sts etcd
    kubectl get pods
    ```

    You should see 3/3 pods become ready, named `etcd-0`, `etcd-1`, `etcd-2`.

5. Run the test command locally:
    After the system is up, you can run the parallel driver 1 to many times via `kubectl exec`.

    `kubectl exec client1 /opt/antithesis/test/v1/main/parallel_driver_generate_traffic.py`

    `kubectl exec client2 /opt/antithesis/test/v1/main/parallel_driver_generate_traffic.py`

Once the cluster is behaving correctly locally, you can proceed to upload it to Antithesis. (Note that SDK assertions won't be evaluated locally.)

## Preparing for Antithesis

### Build and push container images

Replace the \<registry\> with your Antithesis tenant repository: 

```
us-central1-docker.pkg.dev/molten-verve-216720/$TENANT_NAME-repository
```

```shell
docker build -f Dockerfile.client -t <registry>/etcd-client:v1
docker push <registry>/etcd-client:v1

docker build -f Dockerfile.config -t <registry>/etcd-config:v1
docker push <registry>/etcd-config:v1
```

---

## Running the Example on Antithesis

Submit a test run (replace credentials, tenant name, config image, report recipients):

```shell
curl --fail -u '$USER:$PASSWORD' \
-X POST https://$TENANT_NAME.antithesis.com/api/v1/launch/basic_test \
-d '{"params": { "antithesis.description":"basic_test on main",
    "antithesis.duration":"15",
    "antithesis.config_image":"etcd-config:v1", 
    "antithesis.report.recipients":"foo@email.com;bar@email.com"
    } }'
```

<!-- 
---

## Test template

Antithesis' [Test Composer](https://antithesis.com/docs/test_templates/) framework enables you to define a test template, a guide that the system uses to generate thousands of test cases that will run over a multitude of system states. When you use this framework, the platform will handle varying things like parallelism, test length, and command order.

You provide a set of test commands, executables which the framework detects based on their absolute directory location and names.

In client/Dockerfile.client, you can see the test command get defined in the client container image: `/opt/antithesis/test/v1/main/parallel_driver_generate_traffic.py`.

### Parallel Driver

`parallel_driver_generate_traffic.py` is a [parallel driver](https://antithesis.com/docs/test_templates/test_composer_reference/#parallel-driver) that submits puts against the etcd cluster. 0 to many of these can run at once. It then validates that these puts were persisted in the database by connecting to another node and submitting get requests.

## SDK Usage

This repository includes the use of Antithesis's Python SDK to do the following:

### setupComplete

The "[setupComplete](https://antithesis.com/docs/generated/sdk/python/antithesis/lifecycle.html#setup_complete)" signals that the system is ready to test. For example, in `entrypoint.py`:

```shell
setup_complete({"Message":"ETCD cluster is healthy"})
```

### Assertions

Antithesis SDKs allow users to [express the properties their software should have](https://antithesis.com/docs/properties_assertions/), by adding [assertions](https://antithesis.com/docs/properties_assertions/assertions/) to their code. We use 2 types of assertions in this example.

#### Sometimes Assertions

[Sometimes assertions](https://antithesis.com/docs/properties_assertions/properties/#sometimes-properties) check that intended functionality happens at least once in the course of testing \- in this case, that operations happen against the etcd cluster and that validation occurs. For example, in `parallel_driver_generate_traffic.py`:

```shell
sometimes(success, "Client can make successful put requests", {"error":error})
```

#### Always Assertions

[Always assertions](https://antithesis.com/docs/properties_assertions/properties/#always-properties) check that something (like a guarantee) always happens, on every execution history. In this case, in `parallel_driver_generate_traffic.py` this line checks that the database key values stay consistent:

```shell
always(values_stay_consistent, "Database key values stay consistent", {"mismatch":mismatch})
```

### Randomness

Randomness is key for autonomous testing, since we want the software to follow many unpredictable execution paths. [The Antithesis SDK](https://antithesis.com/docs/using_antithesis/sdk/#randomness) provides an easy interface to get structured random values while also providing valuable guidance to the Antithesis platform, which increases the efficiency of testing. -->
