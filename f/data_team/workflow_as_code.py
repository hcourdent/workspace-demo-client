from wmill import task

import pandas as pd
import numpy as np

@task()
# You can specify tag to run the task on a specific type of worker, e.g. @task(tag="custom_tag")
def heavy_compute(n: int):
    df = pd.DataFrame(np.random.randn(100, 4), columns=list('ABCD'))
    return df.sum().sum()


@task
def send_result(res: int, email: str):
    # logs of the subtask are available in the main task logs
    print(f"Sending result {res} to {email}")
    return "OK"

def main(n: int):
    l = []

    # to run things in parallel, simply use multiprocessing Pool map instead: https://docs.python.org/3/library/multiprocessing.html
    for i in range(n):
        l.append(heavy_compute(i))
    print(l)
    return send_result(sum(l), "example@example.com")
