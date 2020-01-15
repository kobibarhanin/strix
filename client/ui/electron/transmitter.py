import sys

with open('output','a') as file:
    file.write(sys.argv[1])
sys.stdout.write("Failed")
sys.stdout.flush()