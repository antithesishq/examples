# Dgraph testing in Antithesis

This repository contains the system-under-test (SUT) for a Dgraph cluster (https://github.com/hypermodeinc/dgraph) and an implementation of the ring test for Dgraph.

## Getting it to run

There are various make command you can use to get this setup running locally.

Pull the docker container image, build the workload and bring the cluster up

```
make up
```

## Locally running the ring test

Use the following make command to try out the ring test locally

```
make test-first-make-ring
```

This will make the initial ring

```
make test-make-swaps
```

This will run multiple ring swaps in paralell indefinitely, you can run this for a few seconds and exit out of the terminal

```
make test-finally-check-ring
```

This will check if the ring is intact

## Viewing the Antithesis SDK assertions locally

```
make view-sdk-logs
```
