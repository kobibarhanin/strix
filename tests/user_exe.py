from lib.agent import Agent

agent = Agent()


# === tests logic ==== #


import time
time.sleep(10)

res = 'This is some\n' \
      'payload returned\n' \
      'from agent execution\n'


# === write to payload === #
agent.payload(res)
