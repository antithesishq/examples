# Example systems under test

This repository contains example systems under test (SUTs) that demonstrate how to use [Antithesis](https://antithesis.com/) to test distributed and fault-tolerant systems. Each example provides a complete, reproducible system with a configuration, test workload, and supporting explanation to help users understand how to integrate their own software with Antithesis.

## Repository Structure

Each example lives in its own directory and is completely self-contained.

Directories use the following naming conventions:

- `*-docker` for example SUTs orchestrated with Docker Compose.
- `*-k8s` for example SUTs orchestrated with Kubernetes.
- `test-composer-*` for example SUTs that demonstrate how to use Test Composer.

| SUT | Description | Companion docs |
| :---- | :---- | :---- |
| [dgraph-docker](https://github.com/antithesishq/examples/tree/main/dgraph-docker) | Testing dgraph's ACID guarantees with a Ring test. | [Test ACID compliance with a Ring test](https://antithesis.com/resources/ring_test/) |
| [etcd-docker](https://github.com/antithesishq/examples/tree/main/etcd-docker) | Testing a 3-node etcd cluster with a simple client workload. | [Set up an example system with Docker](https://antithesis.com/docs/tutorials/etcd_docker/) |
| [etcd-k8s](https://github.com/antithesishq/examples/tree/main/etcd-k8s) | Testing a 3-node etcd cluster with a simple client workload. | [Set up an example system with Kubernetes](https://antithesis.com/docs/tutorials/etcd_kubernetes/) |
| [test-composer-etcd](https://github.com/antithesishq/examples/tree/main/test-composer-etcd) | Learn how to use the test composer using an etcd SUT. |  |

Each example includes its own `README.md` with detailed setup, configuration, and testing instructions.

---

## Getting Started

### Prerequisites

To clone and run any of the examples in our testing environment, you’ll need an Antithesis account and authentication credentials.

Depending on the example you choose, you’ll need one of the following

- Docker and Docker Compose  
- Kubernetes distribution (e.g. kind, minikube, etc)

---

## How to Use This Repository

### Choose an example

Each folder contains:

* SUT configuration  
* Test templates  
* Instructions to sanity-check your SUT setup locally  
* Optional diagrams

### Build container images

Examples include Dockerfiles and instructions for building images that Antithesis will later run during testing.

### Run the SUT locally (optional but recommended)

Each example provides local run instructions to sanity-check the system before testing with Antithesis.

### Push to Antithesis and run tests

Follow the example-specific instructions for:

* Uploading images
* Launching a test run
* Viewing test results