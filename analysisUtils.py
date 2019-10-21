from __future__ import print_function
import angr
import claripy
#this module provides a bunch of util functions for program analysis.\

#ascii to int conversion (but I'm not taking into account the + and - signs!
#takes a list of bit vector ascii values for [0-9, +/-]: [48-57,43/45] and converts it to a symbolic number.
#Expacts all bitvectors in the numlist have equal length
def a2i(numList):
    #use first character to determine sign
    signbit = claripy.If(numList[0] == 45, claripy.BVV(-1, numList[0].length), claripy.BVV(1, numList[0].length))
    #skip the signbit if it was a + or -
    result = numList[len(numList)-1]-48
    #start = 1 if numList[0] < 48 else 0
    #walk over numlist in reverse order, starting at before last position
    for i,a in enumerate(numList[-2:0:-1]):
        #subr = claripy.BVS('subresult', 32)
        change = (a-48)*(10**(i+1))
        result += change
        print(change)
    result += claripy.If(numList[0] < 48, claripy.BVV(0,numList[0].length), (numList[0]-48)*(10**(len(numList)-1)))
    return result * signbit

#returns a intersection of BV1 and BV2
#does not work if the BVs have operations on them.
#BVs must be symbollic
#create a BVS with an equality constraint to another BV if this doesn't comply with want you want
#adds the intersection constraints to resultConstraintset
#initially only support all constraintsets are equal! (so just don't supply them)
#changing constraints which affect BV1 or BV2 after this function has been called leads to undefined behavior
def intersection(BV1, BV2, se1, se2=None, resultSe=None):
    se2 = se1 if se2 == None else se2
    resultSe = se1 if resultSe == None else resultSe
    bv1Name = list(BV1.variables)[0]
    bv2Name = list(BV2.variables)[0]
    intersection = claripy.BVS('intersection_(%s,%s)_' % (bv1Name,bv2Name), BV1.length)
    for c1 in se1.constraints:
        if c1.variables.__contains__(bv1Name):
            resultSe.add(c1.replace(BV1, intersection))
            print("added constraint: %s" % c1.replace(BV1, intersection))
    for c2 in se2.constraints:
        if c2.variables.__contains__(bv2Name):
            resultSe.add(c2.replace(BV2, intersection))
            print("added constraint: %s" % c2.replace(BV2, intersection))
    return intersection
    
#returns a union of BV1 and BV2
#does not work if the BVs have operations on them.
#BVs must be symbollic
#create a BVS with an equality constraint to another BV if this doesn't comply with want you want
#adds the union constraints to resultConstraintset
#initially only support all constraintsets are equal! (so just don't supply them)
#changing constraints which affect BV1 or BV2 after this function has been called leads to undefined behavior
def union(BV1, BV2, se1, se2=None, resultSe=None):
    se2 = se1 if se2 == None else se2
    resultSe = se1 if resultSe == None else resultSe
    bv1Name = list(BV1.variables)[0]
    bv2Name = list(BV2.variables)[0]
    union = claripy.BVS('union_(%s,%s)_' % (bv1Name,bv2Name), BV1.length)
    BV1constraints = claripy.true
    BV2constraints = claripy.true
    for c1 in se1.constraints:
        if c1.variables.__contains__(bv1Name):
            BV1constraints = claripy.And(BV1constraints, c1.replace(BV1, union))
    for c2 in se2.constraints:
        if c2.variables.__contains__(bv2Name):
            BV2constraints = claripy.And(BV2constraints, c2.replace(BV2, union))
    resultSe.add(claripy.Or(BV1constraints, BV2constraints))
    return union
    
#return a complement of BV
#changing constraints which affect BV1 or BV2 after this function has been called leads to undefined behavior
#stores the complement in resultSe if supplied, otherwise in se
def complement(BV, se, resultSe=None):
    #replace_dict isn't working properly... defined my own.
    #returns a copy with key ASTs in dictionary replaced by value ASTs from dictionary.
    #make sure keys and values are disjunct and the values don't already appear in the BV.
    def replace_dict(BV, dictionary):
        replaced = BV.replace_dict({"":""}) #makes a copy, doesn't replace anything
        for key in dictionary:
            replaced = replaced.replace(key, dictionary[key])
        return replaced
    resultSe = se if resultSe == None else resultSe
    #complement = claripy.BVS('complement_(%s)_' % (bvName), BV.length)
    varDict = {}
#    var = enumerate(BV.variables)[0]
#    actualVar = ta.stringToVar(var,se.constraints)
#    newvars[actualVar] = claripy.BVS("partial_complement_(%s)" % var, BV.length)
#    complement = BV.replace(actualVar, newvars[actualVar])
    BVconstraints = claripy.true
    for var in list(BV.variables):
        actualVar = ta.stringToVar(var,se.constraints)
        varDict[actualVar] = claripy.BVS("partial_complement_(%s)" % var, BV.length)
        #complement.replace(ta.stringToVar(var,se.constraints), newvars[actualVar])
    complement = replace_dict(BV, varDict)
    for c in se.constraints:
        if not c.variables.isdisjoint(BV.variables):
            BVconstraints = claripy.And(BVconstraints, replace_dict(c,varDict))
    print(BVconstraints)
    resultSe.add(claripy.Not(BVconstraints))
    return complement
    
#======================================================================================================
# binary function utils
#======================================================================================================
cfg = None #store a cfg for faster reuse in same projects. format [cfg, binaryName]
    
def printFunctions(binaryName):
    global cfg
    if (cfg == None or cfg[1]!=binaryName):
        cfg = [angr.Project(binaryName).analyses.CFGFast(), binaryName]
    for addr, f in cfg[0].functions.iteritems():
        print("0x%x: %s" % (addr, f.name))
        
def functionAddress(function, binaryName):
    global cfg
    if (cfg == None or cfg[1]!=binaryName):
        cfg = [angr.Project(binaryName).analyses.CFGFast(), binaryName]
    for address, f in cfg[0].functions.iteritems():
        if (function == f.name):
            return address
    return None
    
#======================================================================================================
# state variable utils
#======================================================================================================

def printEvalAllVariables(solverEngine, maxOptions=256):
    # this function isn't efficient, it calls stringToVar very often whereas it could walk over the constraint list just once and map everything
    for s in uniqueVarStrings(solverEngine.constraints):
        print("%s: %s" % (s, solverEngine.eval(stringToVar(s,solverEngine.constraints), maxOptions)))
        #we're currently still looking at individual variables (characters read from stdin), should change this to entire variables
        # find address using 'objdump ./a.out -d', then work from there

varCache = {}
def stringToVar(varString, constraintList):
    # converts a string representation of a variable to a VBS used in the constraintList
    if varString in varCache:
        return varCache[varString]
    for c in constraintList:
        for d in c.recursive_leaf_asts:
            if len(d.variables) != 0 and list(d.variables)[0] == varString:
                varCache[varString] = d
                return d

def uniqueVarStrings(constraints):
    varSet = set([])
    for c in constraints:
        varSet = varSet.union(c.variables)
    return list(varSet)
    
def uniqueSymbols(constraints):
    symbols = {}
    for var in uniqueVarStrings(constraints):
        symbols[var] = stringToVar(var,constraints)
    return symbols
    
def symMax(sym1, sym2, solver=None):
    if solver == None:
        solver = claripy.Solver()
    if solver.satisfiable([sym1 > sym2]):
        if solver.satisfiable([sym2 > sym1]):
            return claripy.If(sym1 > sym2, sym1, sym2)
        else:
            return sym1
    else:
        return sym2
        
#======================================================================================================
# AST utils
#======================================================================================================

import claripy
def ASTSafeEqualsComparison(c1, c2):
    if type(c1) == claripy.ast.bv.BV:
        if type(c2) != claripy.ast.bv.BV:
            return False
        return c1.cache_key == c2.cache_key
    else:
        return c1 == c2