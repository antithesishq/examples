# Etcd

## Overview

This repo demonstrates the use of the [Antithesis platform](https://antithesis.com/product/what_is_antithesis/) to test [etcd](https://etcd.io/). Follow the step-by-step tutorial [here](https://antithesis.com/docs/tutorials/etcd_kubernetes)

## Setup

We use the [etcd helm chart](https://github.com/bitnami/charts) to run a 3-node etcd cluster (`etcd-0`, `etcd-1`, `etcd-2`). Additionally, we run two `client` containers to exercise the cluster. `manifests/etcd.yaml` is generated using the values documented [in the tutorial](https://antithesis.com/docs/tutorials/k8s-cluster-setup/#create-a-values.yaml-file)

## Test Composer 

Antithesis' [Test Composer](https://antithesis.com/docs/test_templates/) framework enables you to define a *test template,* a guide that the system uses to generate thousands of test cases that will run over a multitude of system states. When you use this framework, the platform will handle varying things like parallelism, test length, and command order. 

You provide a set of *test commands,* executables which the framework detects based on [their absolute directory location and names](https://antithesis.com/docs/test_templates/first_test/#structuring-test-templates). 

In `client/Dockerfile.client`, you can see the test command get defined in the `client` container image: `/opt/antithesis/test/v1/main/parallel_driver_generate_traffic.py`.

*Drivers can be defined on any container in the system.* 

### Parallel Driver

`parallel_driver_generate_traffic.py` is a [parallel driver](https://antithesis.com/docs/test_templates/test_composer_reference/#parallel-driver) that submits puts against the etcd cluster. 0 to many of these can run at once. It then validates that these puts were persisted in the database by connecting to another node and submitting get requests. 


## SDK Usage

This repository includes the use of Antithesis's Python SDK to do the following: 

### Assertions

Antithesis SDKs allow users to [express the properties their software should have,](https://antithesis.com/docs/properties_assertions/) by [adding assertions to their code](https://antithesis.com/docs/properties_assertions/assertions/). We use 2 types of assertions in this example. 

#### Sometimes Assertions

[Sometimes assertions](https://antithesis.com/docs/properties_assertions/properties/#sometimes-properties) check that intended functionality *happens at least once in the course of testing* - in this case, that operations happen against the etcd cluster and that validation occurs. For example, in `parallel_driver_generate_traffic.py`: 

`sometimes(success, "Client can make successful put requests", {"error":error})`

#### Always Assertions

[Always assertions](https://antithesis.com/docs/properties_assertions/properties/#always-properties) check that something (like a guarantee) *always happens, on every execution history.* In this case, in `parallel_driver_generate_traffic.py` this line checks that the database key values stay consistent: 

`always(values_stay_consistent, "Database key values stay consistent", {"mismatch":mismatch})`

### Randomness

Randomness is key for autonomous testing, since we want the software to follow many unpredictable execution paths. [The Antithesis SDK](https://antithesis.com/docs/using_antithesis/sdk/#randomness) provides an easy interface to get structured random values while also providing valuable guidance to the Antithesis platform, which increases the efficiency of testing.

## Testing Locally

Before running your application on the Antithesis platform, checking your work locally before you kick off a full Antithesis test run can be convenient.

This process is [described in greater detail here](https://antithesis.com/docs/tutorials/k8s-cluster-setup/#start-the-cluster-locally) and [here](https://antithesis.com/docs/test_templates/testing_locally/)

1. Build the client image: 

    `docker build -f client/Dockerfile.client -t etcd-client:k8s client/`

2. Deploy your manifests. 

    `kubectl apply -f manifests/` 

    or if you're using `kapp`:

    `kapp deploy -a app-name -f manifests/ --yes`

3. Check your rollout status
    ```
    kubectl rollout status statefulset/etcd --timeout=3m
    kubectl get sts etcd
    kubectl get pods
    ```

    You should see 3/3 pods become ready, named `etcd-0`, `etcd-1`, `etcd-2`.

4. After the system is up, you can run the parallel driver 1 to many times via `kubectl exec`: 

    `kubectl exec client1 /opt/antithesis/test/v1/main/parallel_driver_generate_traffic.py`

    `kubectl exec client2 /opt/antithesis/test/v1/main/parallel_driver_generate_traffic.py`

6. Confirm that the parallel driver command works

You've now validated that your test is ready to run on the Antithesis platform! (Note that SDK assertions won't be evaluated locally.)
