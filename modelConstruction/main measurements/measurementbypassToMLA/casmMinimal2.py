import re

allInstructions = ["ADC<c> <Rd>, <Rn>, #<const>", "ADC<c> <Rd>, <Rn>, <Rm>, <shift>", "ADC<c> <Rd>, <Rn>, <Rm>", "ADC<c> <Rd>, <Rn>, <Rm>, <type> <Rs>", "ADD<c> <Rd>, <Rn>, #<const>", "ADD<c> <Rd>, <Rn>, <Rm>, <shift>", "ADD<c> <Rd>, <Rn>, <Rm>", "ADD<c> <Rd>, <Rn>, <Rm>, <type> <Rs>", "ADD<c> <Rd>, SP, #<const>", "ADD<c> <Rd>, SP, <Rm>, <shift>", "ADD<c> <Rd>, SP, <Rm>", "ADR<c> <Rd>, <label>", "AND<c> <Rd>, <Rn>, #<const>", "AND<c> <Rd>, <Rn>, <Rm>, <shift>", "AND<c> <Rd>, <Rn>, <Rm>", "AND<c> <Rd>, <Rn>, <Rm>, <type> <Rs>", "ASR<c> <Rd>, <Rm>, #<imm>", "ASR<c> <Rd>, <Rn>, <Rm>", "B<c> <label>", "BIC<c> <Rd>, <Rn>, #<const>", "BIC<c> <Rd>, <Rn>, <Rm>, <shift>", "BIC<c> <Rd>, <Rn>, <Rm>", "BIC<c> <Rd>, <Rn>, <Rm>, <type> <Rs>", "BKPT #<imm16>", "BL<c> <label>", "BLX<c> <Rm>", "BX<c> <Rm>", "CLZ<c> <Rd>, <Rm>", "CMN<c> <Rn>, #<const>", "CMN<c> <Rn>, <Rm>, <shift>", "CMN<c> <Rn>, <Rm>", "CMN<c> <Rn>, <Rm>, <type> <Rs>", "CMP<c> <Rn>, #<const>", "CMP<c> <Rn>, <Rm>, <shift>", "CMP<c> <Rn>, <Rm>", "CMP<c> <Rn>, <Rm>, <type> <Rs>", "DBG<c> #<option>", "DMB <option>", "DSB <option>", "EOR<c> <Rd>, <Rn>, #<const>", "EOR<c> <Rd>, <Rn>, <Rm>, <shift>", "EOR<c> <Rd>, <Rn>, <Rm>", "EOR<c> <Rd>, <Rn>, <Rm>, <type> <Rs>", "ISB <option>", "LDM<c> <Rn>{!}, <registers>", "LDMDA <Rn>{!}, <registers>", "LDMDB <Rn>{!}, <registers>", "LDMIB <Rn>{!}, <registers>", "LDR<c> <Rt>, [<Rn>, #+/-<imm12>]", "LDR<c> <Rt>, [<Rn>]", "LDR<c> <Rt>, <label>", "LDR<c> <Rt>, [<Rn>,+/-<Rm>, <shift>]{!}", "LDR<c> <Rt>, [<Rn>,+/-<Rm>]{!}", "LDRB <Rt>, [<Rn>, #+/-<imm12>]", "LDRB <Rt>, [<Rn>]", "LDRB <Rt>, <label>", "LDRB <Rt>, [<Rn>,+/-<Rm>, <shift>]{!}", "LDRB <Rt>, [<Rn>,+/-<Rm>]{!}", "LDRBT <Rt>, [<Rn>], #+/-<imm12>", "LDRH <Rt>, [<Rn>, #+/-<imm8>]", "LDRH <Rt>, [<Rn>]", "LDRH <Rt>, <label>", "LDRH <Rt>, [<Rn>,+/-<Rm>]{!}", "LDRSB <Rt>, [<Rn>, #+/-<imm8>]", "LDRSB <Rt>, [<Rn>]", "LDRSB <Rt>, <label>", "LDRSB <Rt>, [<Rn>,+/-<Rm>]{!}", "LDRSH <Rt>, [<Rn>, #+/-<imm8>]", "LDRSH <Rt>, [<Rn>]", "LDRSH <Rt>, <label>", "LDRSH <Rt>, [<Rn>,+/-<Rm>]{!}", "LDRT <Rt>, [<Rn>] , #+/-<imm12>", "LDRT <Rt>, [<Rn>] ", "LSL<c> <Rd>, <Rm>, #<imm5>", "LSL<c> <Rd>, <Rn>, <Rm>", "LSR<c> <Rd>, <Rm>, #<imm>", "LSR<c> <Rd>, <Rn>, <Rm>", "MLA<c> <Rd>, <Rn>, <Rm>, <Ra>", "MOV<c> <Rd>, #<const>", "MOV<c> <Rd>, <Rm>", "MRS<c> <Rd>, <spec_reg>", "MSR<c> <spec_reg>, #<const>", "MSR<c> <spec_reg>, <Rn>", "MUL<c> <Rd>, <Rn>, <Rm>", "MVN<c> <Rd>, #<const>", "MVN<c> <Rd>, <Rm>, <shift>", "MVN<c> <Rd>, <Rm>", "MVN<c> <Rd>, <Rm>, <type> <Rs>", "NOP<c>", "ORR<c> <Rd>, <Rn>, #<const>", "ORR<c> <Rd>, <Rn>, <Rm>, <shift>", "ORR<c> <Rd>, <Rn>, <Rm>", "ORR<c> <Rd>, <Rn>, <Rm>, <type> <Rs>", "PLD <label>", "POP<c> <registers>", "PUSH<c> <registers>", "ROR<c> <Rd>, <Rm>, #<imm>", "ROR<c> <Rd>, <Rn>, <Rm>", "RRX <Rd>, <Rm>", "RSB<c> <Rd>, <Rn>, #<const>", "RSB<c> <Rd>, <Rn>, <Rm>, <shift>", "RSB<c> <Rd>, <Rn>, <Rm>", "RSB<c> <Rd>, <Rn>, <Rm>, <type> <Rs>", "RSC<c> <Rd>, <Rn>, #<const>", "RSC<c> <Rd>, <Rn>, <Rm>, <shift>", "RSC<c> <Rd>, <Rn>, <Rm>", "RSC<c> <Rd>, <Rn>, <Rm>, <type> <Rs>", "SMLAL<c> <RdLo>, <RdHi>, <Rn>, <Rm>", "STM<c> <Rn>{!}, <registers>", "STMDA <Rn>{!}, <registers>", "STMDB <Rn>{!}, <registers>", "STMIB <Rn>{!}, <registers>", "STR<c> <Rt>, [<Rn>, #+/-<imm12>]", "STR<c> <Rt>, [<Rn>]", "STR<c> <Rt>, [<Rn>,+/-<Rm>, <shift>]{!}", "STR<c> <Rt>, [<Rn>,+/-<Rm>]{!}", "STRB <Rt>, [<Rn>, #+/-<imm12>]", "STRB <Rt>, [<Rn>]", "STRB <Rt>, [<Rn>,+/-<Rm>, <shift>]{!}", "STRB <Rt>, [<Rn>,+/-<Rm>]{!}", "STRBT <Rt>, [<Rn>], #+/-<imm12>", "STRH <Rt>, [<Rn>{, #+/-<imm8>}]", "STRH <Rt>, [<Rn>,+/-<Rm>]{!}", "STRT <Rt>, [<Rn>] , #+/-<imm12>", "STRT <Rt>, [<Rn>] ", "SUB<c> <Rd>, <Rn>, #<const>", "SUB<c> <Rd>, <Rn>, <Rm>, <shift>", "SUB<c> <Rd>, <Rn>, <Rm>", "SUB<c> <Rd>, <Rn>, <Rm>, <type> <Rs>", "SUB<c> <Rd>, SP, #<const>", "SUB<c> <Rd>, SP, <Rm>, <shift>", "SUB<c> <Rd>, SP, <Rm>", "SWP{B} <Rt>, <Rt2>, [<Rn>]", "TEQ<c> <Rn>, <Rm>, <shift>", "TEQ<c> <Rn>, <Rm>", "TEQ<c> <Rn>, <Rm>, <type> <Rs>", "TST<c> <Rn>, #<const>", "TST<c> <Rn>, <Rm>, <shift>", "TST<c> <Rn>, <Rm>", "TST<c> <Rn>, <Rm>, <type> <Rs>", "UMLAL<c> <RdLo>, <RdHi>, <Rn>, <Rm>", "UMULL<c> <RdLo>, <RdHi>, <Rn>, <Rm>"]

conditions = ["", "eq"]
types = ["LSL"]
shifts = ["LSL #3", "LSR #3", "ASR #3", "ROR #3", "RRX"]

registers = ["<Rd>","<RdLo>","<RdHi>","<Rt>","<Rt2>","<Rn>","<Rm>","<Rs>","<Ra>"]

class Formatted:
    """
    returns an iterator over all different instructions we want to generate from this format
    """
    def __init__(self, format):
        self.format = format
        self.optionCount = format.count("{")
        self.maxOptionalParamsStep = 2**self.optionCount
    
    def __iter__(self):
        self.conditionStep = 0
        self.setFlagsStep = 0
        self.typeStep = 0
        self.firstStep = False
        self.plusMinStep = 0
        self.constStep = 0
        self.shiftStep = 0
        self.immStep = 0
        self.optionalParamsStep = 0
        
        return self
        
    def next(self):
        self._bailOnHardInstructions()
        self.regCount = 1
        format = self.format
        cc = self._formatCc(format)
        format = cc[0]
        #format = self._formatS(format)
        format = self._formatRegs(format)
        format = self._formatType(format)
        format = self._formatLSB(format)
        format = self._formatWidth(format)
        format = self._formatRotation(format)
        format = self._formatConst(format)
        format = self._formatShift(format)
        format = self._formatImm(format)
        format = self._formatOptionalParams(format)
        format = self._formatXY(format)
        format = self._formatQ(format)
        format = self._formatRegList(format)
        format = self._formatPlusMin(format)
        
        self._step()
        
        c = cc[1] if self.format.find('<c>') != -1 else None
        return (format, c)
    
    def _formatCc(self, format):
        #format all condition codes
        format = format.replace('<c>',conditions[self.conditionStep])
        return (format, conditions[self.conditionStep])
        
    def _formatS(self, format):
        #format all condition codes
        if self.setFlagsStep == 0:
            format = format.replace('{S}',"S")
        else:
            format = format.replace('{S}',"")
        return format
    
    def _formatRegs(self, format):
        #format all registers
        for reg in registers:
            if format.find(reg) != -1:
                format = format.replace(reg,'r%d'%self.regCount)
                self.regCount += 1
        return format
        
    def _formatType(self, format):
        format = format.replace("<type>", types[self.typeStep])
        return format
        
    def _formatLSB(self, format):
        format = format.replace("<lsb>", "3");
        return format
        
    def _formatWidth(self, format):
        format = format.replace("<width>", "8");
        return format
        
    def _formatXY(self, format):    #TODO: may want to iterate over options
        format = format.replace("<x>", "B");
        format = format.replace("<y>", "T");
        return format
        
    def _formatQ(self, format):    #TODO: may want to iterate over options
        format = format.replace("<q>", ".w");
        return format

    def _formatRotation(self, format):
        format = format.replace("<rotation>", "ROR #8");
        return format
        
    def _formatPlusMin(self, format):
        plusMin = "+" if self.plusMinStep == 0 else "-"
        format = format.replace("+/-", plusMin);
        return format
        
    def _formatConst(self, format):
        const = "77" if self.constStep == 0 else "0" #high entropy number
        format = format.replace("<const>", const);
        return format
        
    def _formatShift(self, format):
        format = format.replace("<shift>", shifts[self.shiftStep])
        return format
        
    def _formatImm(self,format):
        imm = "15" if self.immStep == 0 else "0" #high entropy number
        format = re.sub('<imm[0-9]*>', imm, format)
        return format
        
    def _formatRegList(self,format):
        format = format.replace("<registers>", "{r%d,r%d,r%d}" % (self.regCount, self.regCount+1, self.regCount+2))
        self.regCount += 3
        return format
        
    def _formatOptionalParams(self, format):
        def dropFirstOption(format):
            format = re.sub("{[^}]*}","",format,1)
            return format
            
        def keepFirstOption(format):
            format = format.replace("{","",1)
            format = format.replace("}","",1)
            return format
            
        i = self.optionalParamsStep
        count = self.optionCount
        while count > 0:
            if (i % 2) == 0:
                format = dropFirstOption(format)
            else:
                format = keepFirstOption(format)
            i = i >> 1
            count -= 1
        return format
        
    def _step(self):
        if self.firstStep and self.conditionStep == 0 and self.typeStep == 0 and self.plusMinStep == 0 and self.constStep == 0 and self.shiftStep == 0 and self.immStep == 0 and self.optionalParamsStep == 0:
            raise StopIteration
        else:
            self.firstStep = True
            self.conditionStep = ((self.conditionStep+1) % len(conditions))
            if self.format.find('<c>') == -1: self.conditionStep = 0 #override this step if no <c> in instruction
            if self.conditionStep == 0:
                #self.setFlagsStep = (self.setFlagsStep+1) % 2
                #if self.format.find('{S}') == -1: self.setFlagsStep = 0 #override this step if no {S} in instruction
                #if self.setFlagsStep == 0:
                    #self.typeStep = (self.typeStep+1) % len(types)
                    if self.format.find('<type>') == -1: self.typeStep = 0 #override this step if no <type> in instruction
                    if self.typeStep == 0:
                        #self.plusMinStep = (self.plusMinStep+1) % 2
                        if self.format.find('+/-') == -1: self.plusMinStep = 0 #override this step if no +/- in instruction
                        if self.plusMinStep == 0:
                            #self.constStep = (self.constStep+1) % 2
                            if self.format.find('<const>') == -1: self.constStep = 0 #override this step if no <const> in instruction
                            if self.constStep == 0:
                                #self.shiftStep = (self.shiftStep+1) % len(shifts)
                                if self.format.find('<shift>') == -1: self.shiftStep = 0 #override this step if no <shift> in instruction
                                if self.shiftStep == 0:
                                    #self.immStep = (self.immStep+1) % 2
                                    if len(re.findall('<imm[0-9]*>', self.format)) == 0: self.immStep = 0 #override this step if no <imm##> in instruction
                                    if self.immStep == 0:
                                        self.optionalParamsStep = (self.optionalParamsStep+1) % self.maxOptionalParamsStep
                                        if self.format.find('{') == -1: self.optionalParamsStep = 0 #override this step if no {} in instruction instruction
            
        
    def _bailOnHardInstructions(self):
        """
        stop iterating if certain hard to test instructions are encountered
        """
        if self.format.find('spec_reg') != -1 or self.format.find('label') != -1 or self.format.find('endian_specifier') != -1 or self.format.find('option') != -1 :
            raise StopIteration
        
        
def testFunc():
    counter = 0
    for t in allInstructions:
        f = Formatted(t)
        for insn in f:
            print insn[0]
            counter += 1
    print "%d instructions generated" % counter
    
#testFunc()
