docker=podman

.PHONY: up
up: build-all run

build-all: pull-dgraph build-workload

pull-dgraph:
	${docker} pull docker.io/dgraph/dgraph:latest

build-workload:
	${docker} build --no-cache \
		-f ./client/Dockerfile \
		-t dgraph-workload-test:latest \
	.

test-first-make-ring:
	${docker} exec workload /opt/antithesis/test/v1/ring_test/first_make_ring.py

test-make-swaps:
	${docker} exec workload /opt/antithesis/test/v1/ring_test/singleton_driver_run_ring.sh

test-finally-check-ring:
	${docker} exec workload /opt/antithesis/test/v1/ring_test/finally_test_ring.py

view-sdk-logs:
	${docker} exec workload cat /root/sdk.json

run:
	docker-compose --file ./config/docker-compose.yaml up -d

down:
	docker-compose down