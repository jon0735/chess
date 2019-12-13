
import json
import sys



def makeMove(arg1, arg2):
    if int(arg1) + int(arg2) % 2 == 0:
        return True, "message 12"
    else:
        return False, "message 22"


success, msg = makeMove(sys.argv[1], sys.argv[2])

print(success, msg)
