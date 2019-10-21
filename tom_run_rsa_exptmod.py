from __future__ import print_function
#int rsa_exptmod(const unsigned char *in,   unsigned long inlen, unsigned char *out,  unsigned long *outlen, int which, rsa_key *key)
#tom_run_rsa_exptmod
#simple rsa exponentiation
import settings
import claripy
settings.WARNING_ADDRESS = 0x0 #0x467ad8
settings.WARNING_MOMENT = settings.WARNING_AFTER
settings.VERBOSE = True
settings.TARGET_ADDRESS = 0x4678F0 #0x4678f0
settings.TARGET_FUNCTION = "rsa_exptmod"
settings.PC_ONLY = False
settings.OUTPUT_FREQUENCY = 256
settings.TARGET_BINARY = "/media/sf_share/libtomcrypt.so"
settings.numrounds = 2
settings.roundkeyPointer = 40000
settings.key = claripy.BVS("key", 128)
settings.message = claripy.BVS("message", 1000)
settings.pointerToMessage = 10000
settings.msgLength = 10
settings.pointerToCipher = 20000
settings.pointerToOutLength = 1 #this is the value in r3 at 0x67944
settings.which = 0 #1 for private, 0 for public; r6 at 0x46792c
settings.pointerToKey = 30000

settings.epointer = 50000
settings.dpointer = 60000
settings.npointer = 70000
settings.ppointer = 80000
settings.qpointer = 90000
settings.qppointer = 100000
settings.dppointer = 110000
settings.dqpointer = 120000

settings.e = claripy.BVS("key_e", 8000)
settings.d = claripy.BVS("key_d", 8000)
settings.n = claripy.BVS("key_n", 8000)
settings.p = claripy.BVS("key_p", 8000)
settings.q = claripy.BVS("key_q", 8000)
settings.qp = claripy.BVS("key_qp", 8000)
settings.dp = claripy.BVS("key_dp", 8000)
settings.dq = claripy.BVS("key_dq", 8000)

settings.PG_EXPLORE_ARGUMENTS = {"avoid": 0x40AC5C, "find": 0x46799c}

settings.params = [settings.pointerToMessage, settings.msgLength, settings.pointerToCipher, settings.pointerToOutLength, settings.which, settings.pointerToKey]
settings.secret = settings.e.concat(settings.d.concat(settings.n.concat(settings.p.concat(settings.q.concat(settings.qp.concat(settings.dp.concat(settings.dq.concat(settings.message))))))))
from pluginTime import TIME_STRATEGY_SHORTEST
settings.TIME_STRATEGY = TIME_STRATEGY_SHORTEST

def stateInit(startState):
    """stateInit is called before symbolic execution starts. Override it to initialize the starting state."""
    startState.memory.store(settings.pointerToKey, 1, 4)  #private key
    startState.memory.store(settings.pointerToKey+4, settings.epointer, 4)
    startState.memory.store(settings.pointerToKey+8, settings.dpointer, 4)
    startState.memory.store(settings.pointerToKey+12, settings.npointer, 4)
    startState.memory.store(settings.pointerToKey+16, settings.ppointer, 4)
    startState.memory.store(settings.pointerToKey+20, settings.qpointer, 4)
    startState.memory.store(settings.pointerToKey+24, settings.qppointer, 4)
    startState.memory.store(settings.pointerToKey+28, settings.dppointer, 4)
    startState.memory.store(settings.pointerToKey+32, settings.dqpointer, 4)
    
    startState.memory.store(settings.epointer, settings.e, 8000)
    startState.memory.store(settings.dpointer, settings.d, 8000)
    startState.memory.store(settings.npointer, settings.n, 8000)
    startState.memory.store(settings.ppointer, settings.p, 8000)
    startState.memory.store(settings.qpointer, settings.q, 8000)
    startState.memory.store(settings.qppointer, settings.qp, 8000)
    startState.memory.store(settings.dppointer, settings.dp, 8000)
    startState.memory.store(settings.dqpointer, settings.dq, 8000)
    
    startState.memory.store(settings.pointerToMessage, settings.message, 1024)
    return True

settings.stateInit = stateInit

#function to call after each symbolic pipeline execution
import pipelineModel
pipelineModel.oldPip = pipelineModel.computePipelineTime
def avoidBLX(_self):
    pipelineModel.oldPip(_self)
    project = _self.state.meta.factory._project
    bytes = ''.join(project.loader.memory.read_bytes(_self.stmt.addr+4, _self.stmt.len))
    cs = project.arch.capstone if _self.stmt.delta == 0 else project.arch.capstone_thumb
    
    #we're performing double disassembling because the lifter is also doing it... probably not the most efficient thing... but it doesn't seem to be a bottleneck
    insn = next(cs.disasm(bytes, _self.stmt.addr))
    if _self.stmt.addr == 0x46792c:
        print("r6: 0x %s" % _self.state.regs.__getattr__('r6'))
    if _self.stmt.addr == 0x44e350:
        print("r1: 0x %s" % _self.state.regs.__getattr__('r1'))
    if _self.stmt.addr == 0x467944:
       # print "found"
        print("r3: 0x %s" % _self.state.regs.__getattr__('r3'))
        #_self.state.regs.__setattr__('r3', 0x1)
        #print "r3: 0x %s" % _self.state.regs.__getattr__('r3')
    if False and insn.insn_name() == "blx":
        print("found")
        branchreg = insn.reg_name(insn.regs_access()[0][1]).encode('ascii','ignore')
        _self.state.regs.__setattr__(branchreg, 0x40AC5C);
        
pipelineModel.computePipelineTime = avoidBLX

import tool