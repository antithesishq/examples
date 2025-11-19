
FROM python:3.11

WORKDIR /app

COPY ./entrypoint.py /app/entrypoint.py




COPY --chmod=777 ./ring_test/first_make_ring.py /opt/antithesis/test/v1/ring_test/first_make_ring.py
COPY --chmod=777 ./ring_test/finally_test_ring.py /opt/antithesis/test/v1/ring_test/finally_test_ring.py
COPY --chmod=777 ./ring_test/singleton_driver_run_ring.sh /opt/antithesis/test/v1/ring_test/singleton_driver_run_ring.sh

COPY --chmod=777 ./ring_test/modify_ring.py /app/modify_ring.py


RUN pip install pydgraph && pip install antithesis

ENTRYPOINT ["python3", "/app/entrypoint.py"]