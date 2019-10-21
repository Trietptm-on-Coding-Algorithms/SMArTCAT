import re

allInstructions = ["ADC <Rd>, <Rn>, #<const>", "ADC <Rd>, <Rn>, <Rm>, <shift>", "ADC <Rd>, <Rn>, <Rm>", "ADC <Rd>, <Rn>, <Rm>, <type> <Rs>", "ADD <Rd>, <Rn>, #<const>", "ADD <Rd>, <Rn>, <Rm>, <shift>", "ADD <Rd>, <Rn>, <Rm>", "ADD <Rd>, <Rn>, <Rm>, <type> <Rs>", "ADD <Rd>, SP, #<const>", "ADD <Rd>, SP, <Rm>, <shift>", "ADD <Rd>, SP, <Rm>", "ADR <Rd>, <label>", "AND <Rd>, <Rn>, #<const>", "AND <Rd>, <Rn>, <Rm>, <shift>", "AND <Rd>, <Rn>, <Rm>", "AND <Rd>, <Rn>, <Rm>, <type> <Rs>", "ASR <Rd>, <Rm>, #<imm>", "ASR <Rd>, <Rn>, <Rm>", "B <label>", "BIC <Rd>, <Rn>, #<const>", "BIC <Rd>, <Rn>, <Rm>, <shift>", "BIC <Rd>, <Rn>, <Rm>", "BIC <Rd>, <Rn>, <Rm>, <type> <Rs>", "BKPT #<imm16>", "BL <label>", "BLX <Rm>", "BX <Rm>", "CLZ <Rd>, <Rm>", "CMN <Rn>, #<const>", "CMN <Rn>, <Rm>, <shift>", "CMN <Rn>, <Rm>", "CMN <Rn>, <Rm>, <type> <Rs>", "CMP <Rn>, #<const>", "CMP <Rn>, <Rm>, <shift>", "CMP <Rn>, <Rm>", "CMP <Rn>, <Rm>, <type> <Rs>", "DBG #<option>", "DMB <option>", "DSB <option>", "EOR <Rd>, <Rn>, #<const>", "EOR <Rd>, <Rn>, <Rm>, <shift>", "EOR <Rd>, <Rn>, <Rm>", "EOR <Rd>, <Rn>, <Rm>, <type> <Rs>", "ISB <option>", "LDM <Rn>{!}, <registers>", "LDMDA <Rn>{!}, <registers>", "LDMDB <Rn>{!}, <registers>", "LDMIB <Rn>{!}, <registers>", "LDR <Rt>, [<Rn>, #+/-<imm12>]", "LDR <Rt>, [<Rn>]", "LDR <Rt>, <label>", "LDR <Rt>, [<Rn>,+/-<Rm>, <shift>]{!}", "LDR <Rt>, [<Rn>,+/-<Rm>]{!}", "LDRB <Rt>, [<Rn>, #+/-<imm12>]", "LDRB <Rt>, [<Rn>]", "LDRB <Rt>, <label>", "LDRB <Rt>, [<Rn>,+/-<Rm>, <shift>]{!}", "LDRB <Rt>, [<Rn>,+/-<Rm>]{!}", "LDRBT <Rt>, [<Rn>], #+/-<imm12>", "LDRH <Rt>, [<Rn>, #+/-<imm8>]", "LDRH <Rt>, [<Rn>]", "LDRH <Rt>, <label>", "LDRH <Rt>, [<Rn>,+/-<Rm>]{!}", "LDRSB <Rt>, [<Rn>, #+/-<imm8>]", "LDRSB <Rt>, [<Rn>]", "LDRSB <Rt>, <label>", "LDRSB <Rt>, [<Rn>,+/-<Rm>]{!}", "LDRSH <Rt>, [<Rn>, #+/-<imm8>]", "LDRSH <Rt>, [<Rn>]", "LDRSH <Rt>, <label>", "LDRSH <Rt>, [<Rn>,+/-<Rm>]{!}", "LDRT <Rt>, [<Rn>] , #+/-<imm12>", "LDRT <Rt>, [<Rn>] ", "LSL <Rd>, <Rm>, #<imm5>", "LSL <Rd>, <Rn>, <Rm>", "LSR <Rd>, <Rm>, #<imm>", "LSR <Rd>, <Rn>, <Rm>", "MLA <Rd>, <Rn>, <Rm>, <Ra>", "MOV <Rd>, #<const>", "MOV <Rd>, <Rm>", "MRS <Rd>, <spec_reg>", "MSR <spec_reg>, #<const>", "MSR <spec_reg>, <Rn>", "MUL <Rd>, <Rn>, <Rm>", "MVN <Rd>, #<const>", "MVN <Rd>, <Rm>, <shift>", "MVN <Rd>, <Rm>", "MVN <Rd>, <Rm>, <type> <Rs>", "NOP", "ORR <Rd>, <Rn>, #<const>", "ORR <Rd>, <Rn>, <Rm>, <shift>", "ORR <Rd>, <Rn>, <Rm>", "ORR <Rd>, <Rn>, <Rm>, <type> <Rs>", "PLD <label>", "POP <registers>", "PUSH <registers>", "ROR <Rd>, <Rm>, #<imm>", "ROR <Rd>, <Rn>, <Rm>", "RRX <Rd>, <Rm>", "RSB <Rd>, <Rn>, #<const>", "RSB <Rd>, <Rn>, <Rm>, <shift>", "RSB <Rd>, <Rn>, <Rm>", "RSB <Rd>, <Rn>, <Rm>, <type> <Rs>", "RSC <Rd>, <Rn>, #<const>", "RSC <Rd>, <Rn>, <Rm>, <shift>", "RSC <Rd>, <Rn>, <Rm>", "RSC <Rd>, <Rn>, <Rm>, <type> <Rs>", "SMLAL <RdLo>, <RdHi>, <Rn>, <Rm>", "STM <Rn>{!}, <registers>", "STMDA <Rn>{!}, <registers>", "STMDB <Rn>{!}, <registers>", "STMIB <Rn>{!}, <registers>", "STR <Rt>, [<Rn>, #+/-<imm12>]", "STR <Rt>, [<Rn>]", "STR <Rt>, [<Rn>,+/-<Rm>, <shift>]{!}", "STR <Rt>, [<Rn>,+/-<Rm>]{!}", "STRB <Rt>, [<Rn>, #+/-<imm12>]", "STRB <Rt>, [<Rn>]", "STRB <Rt>, [<Rn>,+/-<Rm>, <shift>]{!}", "STRB <Rt>, [<Rn>,+/-<Rm>]{!}", "STRBT <Rt>, [<Rn>], #+/-<imm12>", "STRH <Rt>, [<Rn>{, #+/-<imm8>}]", "STRH <Rt>, [<Rn>,+/-<Rm>]{!}", "STRT <Rt>, [<Rn>] , #+/-<imm12>", "STRT <Rt>, [<Rn>] ", "SUB <Rd>, <Rn>, #<const>", "SUB <Rd>, <Rn>, <Rm>, <shift>", "SUB <Rd>, <Rn>, <Rm>", "SUB <Rd>, <Rn>, <Rm>, <type> <Rs>", "SUB <Rd>, SP, #<const>", "SUB <Rd>, SP, <Rm>, <shift>", "SUB <Rd>, SP, <Rm>", "SWP{B} <Rt>, <Rt2>, [<Rn>]", "TEQ <Rn>, <Rm>, <shift>", "TEQ <Rn>, <Rm>", "TEQ <Rn>, <Rm>, <type> <Rs>", "TST <Rn>, #<const>", "TST <Rn>, <Rm>, <shift>", "TST <Rn>, <Rm>", "TST <Rn>, <Rm>, <type> <Rs>", "UMLAL <RdLo>, <RdHi>, <Rn>, <Rm>", "UMULL <RdLo>, <RdHi>, <Rn>, <Rm>"]

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
