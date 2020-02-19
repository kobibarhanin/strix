from core.agent import Agent


def fibonacci(n):
    a = 0
    b = 1
    if n < 0:
        print("Incorrect input")
    elif n == 0:
        return a
    elif n == 1:
        return b
    else:
        for i in range(2,n):
            c = a + b
            a = b
            b = c
        return b


def run(job_id):
    agent = Agent(job_id)
    res = 'The 200th fibonacci number is: ' + str(fibonacci(200))
    import time
    time.sleep(7)
    agent.payload(res)
    agent.complete()
