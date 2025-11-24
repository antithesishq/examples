import time
from antithesis.lifecycle import setup_complete
import sys
import time



print("Python script ran!",flush = True,file = sys.stderr)

setup_complete({'message' : 'ready to start fuzzing!'})


print("Workload setup complete, sleeping.... ",flush = True,file = sys.stderr)

while True:
    time.sleep(5)

