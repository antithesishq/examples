# Dgraph

This example demonstrates how to test dgraph, an ACID-compliant graph database using Antithesis. It includes:

- A reproducible cluster setup using Docker Compose.  
- A client workload.  
- Example assertions.

Follow the step-by-step tutorial here.

---

## Architecture Overview

The system under test includes:

- 3 dgraph alpha server nodes  
- 3 dgraph zero server nodes  
- 1 ring test workload container

[Faults](https://antithesis.com/docs/environment/fault_injection/) such as network partitions, restarts, pauses, and more will be introduced automatically by Antithesis.

---

## Prerequisites

You will need:

- Docker and Docker Compose.  
- An Antithesis account and authentication credentials.  
- Access to Antithesis’s container registry.

---

## Test template

Antithesis' [Test Composer](https://antithesis.com/docs/test_templates/) framework enables you to define a test template, a guide that the system uses to generate thousands of test cases that will run over a multitude of system states. When you use this framework, the platform will handle varying things like parallelism, test length, and command order.

You provide a set of test commands, executables which the framework detects based on their absolute directory location and names.

In client/Dockerfile.client, you can see the test command get defined in the client container image: `/opt/antithesis/test/v1/main/parallel_driver_generate_traffic.py`.

### First command

`first_make_ring.py` is a [first command](https://antithesis.com/docs/test_templates/test_composer_reference/#first-command) that builds the initial ring graph structure with `n` nodes.

### Singleton driver command

`singleton_driver_run_ring.sh` is a [singleton driver](https://antithesis.com/docs/test_templates/test_composer_reference/#singleton-driver) that runs hundreds of processes which each swaps two random nodes in the graph by deleting old relationships and building new ones with the new neighbors. 

### Finally command

`finally_test_ring.py` is a [finally command](https://antithesis.com/docs/test_templates/test_composer_reference/#finally-command) which runs after the swaps to check that the ring structure is still maintained. 

## SDK Usage

This repository includes the use of Antithesis's Python SDK to do the following:

### setupComplete

The "[setupComplete](https://antithesis.com/docs/generated/sdk/python/antithesis/lifecycle.html#setup_complete)" signals that the system is ready to test. For example, in `entrypoint.py`:

```shell
setup_complete({'message' : 'ready to start fuzzing!'})
```

### Assertions

Antithesis SDKs allow users to [express the properties their software should have](https://antithesis.com/docs/properties_assertions/), by adding [assertions](https://antithesis.com/docs/properties_assertions/assertions/) to their code. We use 2 types of assertions in this example.

#### Always Assertions

[Always assertions](https://antithesis.com/docs/properties_assertions/properties/#always-properties) check that something (like a guarantee) always happens, on every execution history. In this case, in `finally_test_ring.py` this line checks that the ring structure is maintained:

```shell
always(continuity, "Ring continuity maintained", {"cause":msg})
```

### Randomness

Randomness is key for autonomous testing, since we want the software to follow many unpredictable execution paths. [The Antithesis SDK](https://antithesis.com/docs/using_antithesis/sdk/#randomness) provides an easy interface to get structured random values while also providing valuable guidance to the Antithesis platform, which increases the efficiency of testing.

## Testing Locally (Optional)

Before running your application on the Antithesis platform, checking your work locally before you kick off a full Antithesis test run can be convenient.

This process is described in greater detail [here](https://antithesis.com/docs/test_templates/testing_locally/).

The repo provides various make commands you can use to get this setup running locally.

1. Pull the docker container image, build the workload and bring the cluster up:

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

4. Check that the ring structure is intact:

```shell
make test-finally-check-ring
```

Once the ring test is behaving correctly locally, you can proceed to upload it to Antithesis.

---

## Preparing for Antithesis

### Build and push container images

Replace the \<registry\> with Antithesis’s container registry: 

```
us-central1-docker.pkg.dev/molten-verve-216720/$TENANT_NAME-repository
```

```shell
docker build -f Dockerfile -t <registry>/dgraph-client:v1
docker push <registry>/dgraph-client:v1

docker build -f Dockerfile.config -t <registry>/dgraph-config:v1
docker push <registry>/dgraph-config:v1
```

---

## Running the Example on Antithesis

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

Then view the results in the [triage report](https://antithesis.com/docs/reports/#the-triage-report).