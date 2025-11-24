
FROM python:3.11

WORKDIR /app

COPY ./client/entrypoint.py /app/entrypoint.py

COPY --chmod=777 ./client/first_make_ring.py /opt/antithesis/test/v1/ring_test/first_make_ring.py
COPY --chmod=777 ./client/finally_test_ring.py /opt/antithesis/test/v1/ring_test/finally_test_ring.py
COPY --chmod=777 ./client/singleton_driver_run_ring.sh /opt/antithesis/test/v1/ring_test/singleton_driver_run_ring.sh

COPY --chmod=777 ./client/modify_ring.py /app/modify_ring.py

RUN pip install pydgraph && pip install antithesis

ENTRYPOINT ["python3", "/app/entrypoint.py"]