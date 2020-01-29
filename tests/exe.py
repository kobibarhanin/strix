from lib.agent import Agent

agent = Agent()

# === run logic ==== #
# import time
# time.sleep(10)


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


# res = 'This is some\n' \
#       'payload returned\n' \
#       'from agent execution\n'


res = 'The 200th fibonacci number is: ' + str(fibonacci(200))

# === write to payload === #
agent.payload(res)
agent.complete()
