from lib.agent import Agent


# TODO - important! need to pass to the package during initialization or to the executor during execution the JOB_ID to be executed!!



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

    # === write to payload === #
    agent.payload(res)
    agent.complete()
