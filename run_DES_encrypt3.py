from __future__ import print_function
#run_DES_encrypt3
#                  DES_encrypt3(DES_LONG *data, DES_key_schedule *ks1,
#                  DES_key_schedule *ks2, DES_key_schedule *ks3)

import settings
import claripy
settings.WARNING_ADDRESS = 0x49e1d4
settings.WARNING_MOMENT = settings.WARNING_AFTER
settings.VERBOSE = True#False
settings.TARGET_ADDRESS = 0x49EB50
settings.TARGET_FUNCTION = "DES_encrypt3"
settings.TARGET_BINARY = "/home/roeland/Documents/opensslARM/bin/lib/libcrypto.so.1.1"

settings.dataBuf = 100000
settings.data = claripy.BVS('data', 1024)

settings.keyBuf = 110000
settings.key1 = claripy.BVS("key1", 512)
settings.key2 = claripy.BVS("key2", 512)
settings.key3 = claripy.BVS("key3", 512)

settings.params = [settings.dataBuf, settings.keyBuf, settings.keyBuf+512, settings.keyBuf+1024]

settings.secret = settings.key1.concat(settings.key2.concat(settings.key3.concat(settings.data)))
from pluginTime import TIME_STRATEGY_SHORTEST_IF_NONSECRET
TIME_STRATEGY = TIME_STRATEGY_SHORTEST_IF_NONSECRET

from pipelineModel import LATENCY_STRATEGY_SHORTEST_IF_NONSECRET
settings.LATENCY_STRATEGY = LATENCY_STRATEGY_SHORTEST_IF_NONSECRET

def stateInit(startState):
    """stateInit is called before symbolic execution starts. Override it to initialize the starting state."""
    print("state initialized")
    startState.memory.store(settings.keyBuf, settings.key1, 512)
    startState.memory.store(settings.keyBuf+512, settings.key2, 512)
    startState.memory.store(settings.keyBuf+1024, settings.key3, 512)
    startState.memory.store(settings.dataBuf, settings.data, 1024)
    return True


settings.stateInit = stateInit

import tool