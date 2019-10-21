from __future__ import print_function
#run_nacl_crypto_stream_salsa20_xor
import settings
import claripy
settings.WARNING_ADDRESS = 0x14b28
settings.WARNING_MOMENT = settings.WARNING_AFTER
settings.VERBOSE = False
settings.TARGET_ADDRESS = 0x14660
settings.TARGET_FUNCTION = "crypto_stream_salsa20_xor"
settings.TARGET_BINARY = "/home/roeland/Documents/tweetnacl/tweetnaclARMO3NoInline"
settings.messagelength = 2
settings.noncePointer = 150000

settings.dataBuf = 140000
settings.data = claripy.BVS('data', 1024)

settings.keyBuf = 100000
settings.key = claripy.BVS("key", 33600)

settings.outputBufferPointer = 200000

settings.params = [settings.outputBufferPointer, settings.dataBuf, settings.messagelength, settings.noncePointer, settings.keyBuf]
settings.secret = settings.key.concat(settings.message)
from pluginTime import TIME_STRATEGY_SHORTEST_IF_NONSECRET
TIME_STRATEGY = TIME_STRATEGY_SHORTEST_IF_NONSECRET
from pipelineModel import LATENCY_STRATEGY_SHORTEST_IF_NONSECRET
settings.LATENCY_STRATEGY = LATENCY_STRATEGY_SHORTEST_IF_NONSECRET

def stateInit(startState):
    """stateInit is called before symbolic execution starts. Override it to initialize the starting state."""
    print("state initialized")
    startState.memory.store(settings.keyBuf, settings.key, 33600)
    startState.memory.store(settings.dataBuf, settings.data, 1024)
    return True
settings.stateInit = stateInit

import tool