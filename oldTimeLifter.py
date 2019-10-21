from __future__ import print_function
import sys
import logging
from cachetools import LRUCache

import pyvex
import simuvex
from archinfo import ArchARM

import angr

import angr.lifter

l = logging.getLogger("angr.lifter")

VEX_IRSB_MAX_SIZE = 400
VEX_IRSB_MAX_INST = 99
VEX_DEFAULT_OPT_LEVEL = 1

import timeStmt

#VEX_DEFAULT_OPT_LEVEL = 0

class TimeLifter(angr.lifter.Lifter):
    """
    The lifter is the part of the factory that deals with the logic related to lifting blocks to IR.
    It is complicated enough that it gets its own class!

    Usually, the only way you'll ever have to interact with this class is that its `lift` method has
    been transplanted into the factory as `project.factory.block`.
    DEPRECATED
    """

    LRUCACHE_SIZE = 10000

    def __init__(self, project=None, arch=None, cache=False):
        angr.lifter.Lifter.__init__(self, project, arch, cache)
        self.referenceProject = angr.Project(self._project.filename)
        print("opt level: %d" % angr.lifter.VEX_DEFAULT_OPT_LEVEL)
        angr.lifter.VEX_DEFAULT_OPT_LEVEL = 0
        print("opt level new: %d" % angr.lifter.VEX_DEFAULT_OPT_LEVEL)
        
    def lift(self, addr, arch=None, insn_bytes=None, max_size=None, num_inst=None,
            traceflags=0, thumb=False, backup_state=None, opt_level=None):
        return angr.lifter.Lifter.lift(self, addr, arch, insn_bytes, max_size, num_inst, traceflags, thumb, backup_state, 0)
        
    def _post_process(self, block, arch):
        """
        Do some post-processing work here.

        :param block:
        :return:
        """
        
        self.upgrade(block)
        block = angr.lifter.Lifter._post_process(self, block, arch)

        return block

    def upgrade(self, block):
        """
        Adds pseudo-vex time statements into the instruction list
        """
        targetStmt = [None, None]
        instructionAddress = 0
        block.pp()
        for i, stmt in enumerate(block.statements):
            #code to read stmt tags generated for a certain mnemonic:
            #if targetStmt[0] == 'str':
            #   print stmt.tag
            #   stmt.pp()
            #   print stmt.expressions[0]
            #   if ("%s" % stmt.expressions[0]) == "LDle:I32(t0)":
            #       global LDStmt
            #       LDStmt = stmt
            if stmt.tag == "Ist_IMark":
                if targetStmt != [None, None]:
                    #This should never occur!
                    print("\033[93mWarning: missed a key statement! DEBUG; this should never occur\033[0m")
                    
                #print stmt
                
                #bytes = ''
                #for addr in range(stmt.addr, stmt.addr+stmt.len):
                #    bytes += self._project.loader.memory[addr]
                
                bytes = ''.join(self._project.loader.memory.read_bytes(stmt.addr, stmt.len))
                #bytes = "%s%s" % (b.loader.memory[0x4013d0], b.loader.memory[0x4013d1])
                cs = self._project.arch.capstone if stmt.delta == 0 else self._project.arch.capstone_thumb
                
                #this should only return a single disassembled instruction
                for d in cs.disasm(bytes, stmt.addr): mnemonic = angr.lifter.CapstoneInsn(d).mnemonic
                
                instructionAddress = stmt.addr
                
                print(angr.lifter.CapstoneInsn(d));
                #print mnemonic
                
                targetStmt = self.keyStatement.get(mnemonic, [mnemonic, 'Ist_Put'])
                if (mnemonic == 'jmp'):
                    print('jmp found:')
                    block.pp()
                #print "instruction: %s" % mnemonic
                #print "looking for vex statement: %s" % targetStmt[1]
            elif stmt.tag == targetStmt[1]:
                if (targetStmt[0] == 'ldr'):
                    #special case because ldr instruction shouldn't trigger on just any Ist_WrTmp
                    if stmt.expressions[0].tag == 'Iex_Load':
                        block.statements.insert(i, timeStmt.Time(block, targetStmt[0], stmt, instructionAddress))
                        targetStmt = [None, None]
                else:
                    #Generic case for most instructions:
                    #TODO: check if this statement insertion doesn't break any program logic (don't think it does)
                    block.statements.insert(i, timeStmt.Time(block, targetStmt[0], stmt, instructionAddress))
                    
                    #print "statement found"
                    targetStmt = [None, None]
            elif stmt.tag == 'Ist_Store' and targetStmt != [None, None]:
                #why am I doing this? This doesn't seem to be very useful and does make some things messy
                block.statements.insert(i, timeStmt.Time(block, "%s" % targetStmt[0], stmt, instructionAddress))
                targetStmt = [None, None]
            #print stmt.tag
                
    #currently only support single key statements
    #should probably use regex's to group instructions
    keyStatement = {
        'mov.w': ['mov_w','Ist_Put'],
        'pop': ['pop','Ist_Put'],
        'mov': ['mov','Ist_Put'],
        'add': ['add','Ist_Put'],
        'jmp': ['jmp','Ist_Put'],
        'movzx' : ['movzx', 'Ist_Put'],
        'bgt' : ['bgt', 'Ist_Exit'],
        'ble' : ['ble', 'Ist_Exit'],
        'beq' : ['beq', 'Ist_Exit'],
        'str' : ['str', 'Ist_Store'], #TODO: or STbe (little-endian vs big-endian)
        'strb' : ['str', 'Ist_Store'], #TODO: for now this is mapped as a normal str instruction, might want to fix this or make this a generic approach (current approach provides false information about instructions to high level layers)
        'ldr' : ['ldr', 'Ist_WrTmp'],
        'ldrb' : ['ldr', 'Ist_WrTmp'] #TODO: for now this is mapped as a normal ldr instruction, might want to fix this or make this a generic approach (current approach provides false information about instructions to high level layers)
    }
        
from angr.errors import AngrMemoryError, AngrTranslationError, AngrLifterError
from angr.knowledge.codenode import BlockNode