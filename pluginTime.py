from __future__ import print_function
TIME_STRATEGY_SHORTEST = 0
TIME_STRATEGY_AVERAGE = 1
TIME_STRATEGY_LONGEST = 2
TIME_STRATEGY_NO_CHANGE = 3
TIME_STRATEGY_SHORTEST_IF_NONSECRET = 4
TIME_STRATEGY_AVERAGE_IF_NONSECRET = 5
TIME_STRATEGY_LONGEST_IF_NONSECRET = 6

import claripy

import angr
from angr.sim_state import SimState
from angr.state_plugins.plugin import SimStatePlugin
import timingModel
import capstone.arm_const as capcon
import timeAnalysis
import settings

import logging
l= logging.getLogger(name="pluginTime")

#maintain lists of violations:
type1violations = []
type2violations = []
type3violations = []

FLAGS_REGISTER = -1

class PluginTime(SimStatePlugin):
    """
    Plugin to keep track of state execution time and register / memory availability time
    TODO low priority: can currently only handle memory accesses of 4 bytes, should make this dynamic?.
    TODO low priority: add counters for branch prediction and caching violations? (why?)
    """
    def __init__(self, time=None):
        SimStatePlugin.__init__(self)
        # timing info on the current state
        self.totalExecutionTime = claripy.BVV(0x000000, 32) #this path's cummulative execution time
        
        #The decision was made to precompute self-composition. This is a cpu-memory tradeof in favor of using cpu, as otherwise states need to be copied into registers as states are required to compute self-composition
        #registers and memory are dicts containing:
        #[0]: time at which this register/memory becomes available
        #[1]: None if this register doesn't depend on a secret, or a tuple (mnemonic, address) of the instruction which last wrote to this location if it does depend on a secret
        #[2]: the instruction which last wrote to this location
        #[3]: the properties of the instruction in [2]
        self.registers = {} #timewise availability of registers in this state
        self.memory = {} #timewise availability of memory in this state

        
        self.lastInsn = None #(insn, format)
        
        self.instructionCount = 0
        if time is not None:
            self.totalExecutionTime = time.totalExecutionTime
            self.registers = time.registers
            self.memory = time.memory
            self.lastInsn = time.lastInsn
            self.instructionCount = time.instructionCount

    def countTime(self, deltaTime, compositionCheck=None, props=None, dependencies=None):
        """
        if compositionCheck isn't None, it expects a capstone instruction causing the time update, it then also expects props to be the props associated with that instruction. If so, it will perform self composition to check for timing channels
        returns True iff self-composition identifies a timing difference on deltaTime
        
        If compositionCheck != None and dependencies is a list of symbolic expressions, instead of checking time inequality we check dependency inequality
        """
        #print "total execution time: %s" % self.totalExecutionTime
        #print "delta time: %s" % deltaTime
        #print "dependencies: %s" % (dependencies,)
        result = False;
        if compositionCheck!=None and ((type(deltaTime) == claripy.ast.bv.BV and deltaTime.symbolic) or dependencies != None):
            #perform self-composition to check if deltaTime depends on the secret
            solver = self.state.se._stored_solver.branch()
            if type(deltaTime) == claripy.ast.bv.BV and deltaTime.symbolic:
                compositionTargets = [deltaTime]
            else:
                compositionTargets = []
            if dependencies != None:
                for d in dependencies:
                    if type(d) == int and d == -1:
                        compositionTargets.append(timingModel.computeCondition(compositionCheck.cc-1, self.state))
                    elif type(d) == claripy.ast.bv.BV:
                        compositionTargets.append(d)
            for target in compositionTargets: #perform self-composition proofs for the list of targets (time + dependencies)
                if solver.hasMultipleSolutions(target) and not result and solver.proofInequalityPossible(target):#only perform if the target can actually take on multiple values, also, a single result is sufficient
                    result = True
                    #print "violating target: %s" % target
                    import store
                    store.violation = target
                    store.violationinsn = compositionCheck
                    print("time incremented by: %s" % deltaTime)
                        
            if result:
                if compositionCheck.group(props.isTrueBranch()):
                    print("\033[93mWarning: Type 1 violation at instruction: %s @ 0x%x\033[0m" % (compositionCheck.mnemonic, compositionCheck.address))
                    global type1violations
                    type1violations.append((compositionCheck.mnemonic, compositionCheck.address))
                elif props.isMemInsn():
                    print("\033[93mWarning: Type 2 violation at instruction: %s @ 0x%x\033[0m" % (compositionCheck.mnemonic, compositionCheck.address))
                    global type2violations
                    type2violations.append((compositionCheck.mnemonic, compositionCheck.address))
                else:
                    print("\033[93mWarning: violation of unknown type at instruction: %s @ 0x%x\033[0m" % (compositionCheck.mnemonic, compositionCheck.address))
                  
        solverCopy = self.state.se._solver.branch()
        
        
        #possibly change the time if it doesn't depend on the secret. (after all, we're not really interested in many timing-differences for non-secret-dependent timings
        #note: calling solver.min regularly, significantly slows down analysis (but is faster than not concretizing)
        if type(deltaTime) == claripy.ast.bv.BV and deltaTime.symbolic and settings.TIME_STRATEGY != TIME_STRATEGY_NO_CHANGE and (settings.TIME_STRATEGY < 3 or (not result and settings.TIME_STRATEGY > 3)) and self.state.se._stored_solver.satisfiable():
            if settings.TIME_STRATEGY == TIME_STRATEGY_SHORTEST_IF_NONSECRET or settings.TIME_STRATEGY == TIME_STRATEGY_SHORTEST:
                if deltaTime.op == 'If' and deltaTime.args[0].args[0].cache_key in timingModel.cacheSwitchInstances:
                    instance = deltaTime.args[0].args[0]
                    deltaTime = deltaTime.args[2]
                    del timingModel.cacheSwitchInstances[instance.cache_key]
                elif deltaTime.op == 'If' and deltaTime.args[0].args[0].cache_key in timingModel.branchSwitchInstances:
                    instance = deltaTime.args[0].args[0]
                    deltaTime = deltaTime.args[2]
                    del timingModel.branchSwitchInstances[instance.cache_key]
                else:
                    deltaTime = solverCopy.min(deltaTime, useComposition=False)
            elif settings.TIME_STRATEGY == TIME_STRATEGY_LONGEST_IF_NONSECRET or settings.TIME_STRATEGY == TIME_STRATEGY_LONGEST:
                if deltaTime.op == 'If' and deltaTime.args[0].args[0].cache_key in timingModel.cacheSwitchInstances:
                    instance = deltaTime.args[0].args[0]
                    deltaTime = deltaTime.args[1]
                    del timingModel.cacheSwitchInstances[instance.cache_key]
                elif deltaTime.op == 'If' and deltaTime.args[0].args[0].cache_key in timingModel.branchSwitchInstances:
                    instance = deltaTime.args[0].args[0]
                    deltaTime = deltaTime.args[1]
                    del timingModel.branchSwitchInstances[instance.cache_key]
                else:
                    deltaTime = solverCopy.max(deltaTime)
            elif settings.TIME_STRATEGY == TIME_STRATEGY_AVERAGE_IF_NONSECRET or settings.TIME_STRATEGY == TIME_STRATEGY_AVERAGE:
                if deltaTime.op == 'If' and deltaTime.args[0].args[0].cache_key in timingModel.cacheSwitchInstances:
                    instance = deltaTime.args[0].args[0]
                    deltaTime = (deltaTime.args[1] + deltaTime.args[2])/2
                    del timingModel.cacheSwitchInstances[instance.cache_key]
                elif deltaTime.op == 'If' and deltaTime.args[0].args[0].cache_key in timingModel.branchSwitchInstances:
                    instance = deltaTime.args[0].args[0]
                    deltaTime = (deltaTime.args[1] + deltaTime.args[2])/2
                    del timingModel.branchSwitchInstances[instance.cache_key]
                else:
                    deltaTime = (solverCopy.min(deltaTime) + solverCopy.max(deltaTime))/2
        if isinstance(deltaTime, float) and deltaTime.is_integer():
            deltaTime = int(deltaTime)
        self.totalExecutionTime += deltaTime
        self.state.se.simplify()
        return result

    def copy(self, memo):
        return PluginTime(time=self)

    def merge(self, others, merge_conditions, common_ancestor=None):
		#TODO low priority
        return False

    def widen(self, others):
        return False

    def clear(self):
        s = self.state
        self.__init__()
        self.state = s

    def updateTimeFromDependencies(self, regs, memory):
        """
        Sets the execution time to the max of the execution time and the time required to access the dependencies.
        The max function is symbolic so it can handle symbolic expressions with overlapping feasibility space
        Call this after all dependencies are known
        
        returns a tuple of two symbolic boolean expressions.
            The first expresses whether there was a pipeline bubble (wait on data dependency)
            The first expresses whether dual issuing is prevented (by either a bubble or the register being available only in the current moment)
        TODO low priority, optimisation only: This function gets called often but heavily relies on calls to the solver. Thus, if the constraints are complex, the function can significantly slow down the entire analysis.
        
        TODO: registers get processed in order... which is strange.
            if a register analysed first could actually increase execution time it gets added as a registers influencing maxtime.
            if another resgister takes longer the previous register is still seen as influencing max time (it could, but this isn't sure)
            basically: we should first see witch registers can influence time, and the registers that are left
        """
        bubble = claripy.false
        dualPrevented = claripy.false
        
        regsInfluencingMaxTime = []
        memsInfluencingMaxTime = []
        #check whether we have to wait for a register
        for r in regs:
            if r in self.registers:
                compute = claripy.backends.z3.simplify(self.registers[r][0].SGT(self.totalExecutionTime))
                satisfiability = self.state.se.satisfiable([compute])
                if satisfiability: #actually wait for the register
                    registerName = ("register %s" % self.state.meta.factory.project.arch.capstone.reg_name(r)) if r != FLAGS_REGISTER else "flags register"
                    if self.state.se.satisfiable([claripy.Not(compute)]):
                        #symbolic maximum function:
                        self.totalExecutionTime = claripy.If(compute, self.registers[r][0], self.totalExecutionTime)
                        print("Symbolically waiting for %s..." % registerName)
                        #print compute
                    else:
                        self.totalExecutionTime = self.registers[r][0]
                        if settings.VERBOSE:
                            print("Waiting for %s..." % registerName)
                    regsInfluencingMaxTime.append(r)

        #check whether we have to wait for a memory
        for m in memory:
            if m in self.memory:
                compute = claripy.backends.z3.simplify(self.memory[m][0].SGT(self.totalExecutionTime))
                satisfiability = self.state.se.satisfiable([compute])
                if satisfiability:  #actually wait for the memory
                    if self.state.se.satisfiable([claripy.Not(compute)]):
                        self.totalExecutionTime = claripy.If(compute, self.memory[m][0], self.totalExecutionTime)
                        if m.concrete:
                            print("Symbolically waiting for memory [0x%x]..." % m.args[0])
                        else:
                            print("Symbolically waiting for memory [%s]..." % m)
                    else:
                        self.totalExecutionTime = self.memory[m][0]
                        if settings.VERBOSE:
                            if m.concrete:
                                print("Waiting for memory [0x%x]..." % m.args[0])
                            else:
                                print("Waiting for memory [%s]..." % m)
                    memsInfluencingMaxTime.append(m)

        global type1violations
        global type2violations
        global type3violations
        
        #if we have multiple contenders for time-influences, we need to check whether some rule some others out
        if len(regsInfluencingMaxTime) + len(memsInfluencingMaxTime) > 1:
            if not self.state.se._solver.hasMultipleSolutions(self.totalExecutionTime): #if execution time doesn't have multiple solutions, there's no need to process any further.
                regsInfluencingMaxTime = []
                memsInfluencingMaxTime = []
            else:
                #we know that execution time can take on multiple values, now we check which registers or memory dependencies can really slow it down.
                for r in regsInfluencingMaxTime:
                    if not self.state.se._solver.satisfiable([self.registers[r][0].SGT(self.totalExecutionTime)]):
                        regsInfluencingMaxTime.remove(r)
                for m in memsInfluencingMaxTime:
                    if not self.state.se._solver.satisfiable([self.memory[m][0].SGT(self.totalExecutionTime)]):
                        memsInfluencingMaxTime.remove(m)
        
        #determine whether any of the registers we're waiting for depends on a secret
        for r in regsInfluencingMaxTime:
            if self.registers[r][1] != None:    #this value was updated to (insn.mnemonic, insn.address) in the pipelineModel step 4, if in step 3 it was computed that the latency depends on a secret, and has multiple timings. So if this condition is passed we know a timing channel exists -> raise warnings and register the violations
                vType = timingModel.violationType(self.registers[r][2], self.registers[r][3])
                if vType != 0:
                    print("\033[93mWarning: Type %d violation at instruction: %s @ 0x%x\033[0m" % (vType, self.registers[r][1][0], self.registers[r][1][1]))
                    if vType == 1:
                        type1violations.append(self.registers[r][1])
                    elif vType == 2:
                        type2violations.append(self.registers[r][1])
                        if not (self.state.options.__contains__(simuvex.o.CONSERVATIVE_WRITE_STRATEGY) and self.state.options.__contains__(simuvex.o.CONSERVATIVE_READ_STRATEGY)):
                            print("\033[93mFor better results you should probably run the analysis and with the initial states' options \"add_options={simuvex.o.CONSERVATIVE_WRITE_STRATEGY, simuvex.o.CONSERVATIVE_READ_STRATEGY}\"\033[0m")
                    elif vType == 3:
                        type3violations.append(self.registers[r][1])
                    import store
                    store.violations.append(("%s, @ 0x%x" % (self.registers[r][1][0], self.registers[r][1][1]), self.registers[r]))
                else: #unknow violation type
                    print("\033[93mWarning: violation of unknown type at instruction: %s @ 0x%x\033[0m" % (vType, self.registers[r][1][0], self.registers[r][1][1]))
                    
        for m in memsInfluencingMaxTime:
            if self.memory[m][1] != None:
                vType = timingModel.violationType(self.memory[m][2], self.memory[m][3])
                if vType != 0:
                    print("\033[93mWarning: Type %d violation at instruction: %s @ 0x%x\033[0m" % (vType, self.registers[r][1][0], self.registers[r][1][1]))
                    if vType == 1:
                        type1violations.append(self.memory[m][1])
                    elif vType == 2:
                        type2violations.append(self.memory[m][1])
                        if not (self.state.options.__contains__(simuvex.o.CONSERVATIVE_WRITE_STRATEGY) and self.state.options.__contains__(simuvex.o.CONSERVATIVE_READ_STRATEGY)):
                            print("\033[93mFor better results you should probably run the analysis and with the initial states' options \"add_options={simuvex.o.CONSERVATIVE_WRITE_STRATEGY, simuvex.o.CONSERVATIVE_READ_STRATEGY}\"\033[0m")
                    elif vType == 3:
                        type3violations.append(self.memory[m][1])
                    import store
                    store.violations.append(("%s, @ 0x%x" % (self.registers[m][1][0], self.registers[m][1][1]), self.registers[m]))
                else: #unknow violation type
                    print("\033[93mWarning: violation of unknown type at instruction: %s @ 0x%x\033[0m" % (vType, self.registers[r][1][0], self.registers[r][1][1]))
                     
        bubble = claripy.backends.z3.simplify(bubble)
        dualPrevented = claripy.backends.z3.simplify(claripy.Or(dualPrevented, bubble))
        return (bubble, dualPrevented)
        
SimState.register_default('time', PluginTime)
