from __future__ import print_function
#run_Camellia_set_key
#                      int Camellia_set_key(const unsigned char *userKey, const int bits,
#                     CAMELLIA_KEY *key)

import settings
import claripy
settings.WARNING_ADDRESS = 0x486ad8
settings.WARNING_MOMENT = settings.WARNING_AFTER
settings.VERBOSE = True#False
settings.TARGET_ADDRESS = 0x488208
settings.TARGET_FUNCTION = "Camellia_set_key"
settings.TARGET_BINARY = "/home/roeland/Documents/opensslARM/bin/lib/libcrypto.so.1.1"

settings.keyBuf = 110000
settings.key = claripy.BVS("key", 1024)

settings.outputBuf = 120000

settings.keyBitLength = claripy.BVS("keyLength", 32)

settings.params = [settings.keyBuf, settings.keyBitLength, settings.outputBuf]

settings.secret = settings.key
from pluginTime import TIME_STRATEGY_SHORTEST#_IF_NONSECRET
TIME_STRATEGY = TIME_STRATEGY_SHORTEST#_IF_NONSECRET

from pipelineModel import LATENCY_STRATEGY_SHORTEST#_IF_NONSECRET
settings.LATENCY_STRATEGY = LATENCY_STRATEGY_SHORTEST#_IF_NONSECRET

def stateInit(startState):
    """stateInit is called before symbolic execution starts. Override it to initialize the starting state."""
    print("state initialized")
    startState.memory.store(settings.keyBuf, settings.key, 1024)
    return True


settings.stateInit = stateInit

import tool