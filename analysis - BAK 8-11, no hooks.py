from __future__ import print_function
import angr, claripy

s = claripy.Solver()

class MockAnalysis(angr.Analysis):
	def __init__(self, maxDepth, verbose):
		self.maxDepth = maxDepth
		self.verbose = verbose

	def analyse(self):
		p = b.factory.path()
		self.stepPathRecursively(p, 0, 0)
				
	def stepPathRecursively(self, path, depth, timeSoFar):
		if depth < self.maxDepth:
			path.step()
			if (self.verbose):
				print(" ")
				print("step %d; addr 0x%08x" % (depth, path.addr))
			#just add a last path for easy manual labor in python
			self.lastPath = path
			timeSoFar = self.walkOverStatements(path.addr, timeSoFar)
			if len(path.successors) > 0:
				if len(path.successors) != 1:
					print("branching: %d paths ahead" % len(path.successors))
				for p in path.successors:
					self.stepPathRecursively(p, depth+1, timeSoFar)
			else:
				print("path ended at depth %d. execution time: %d cycles" % (depth, timeSoFar))
		else:
			print("path stopped, maxdepth reached. execution time: %d cycles" % timeSoFar)
	
	def walkOverStatements(self, address, timeSoFar):
		block = b.factory.block(address)
		for stmt in block.vex.statements:
			if stmt.tag == 'Ist_IMark':
				mnemonic = b.factory.block(stmt.addr).capstone.insns[0].mnemonic
				tte = TimingModel(mnemonic)
				timeSoFar += tte
				if (self.verbose):
					print("---- Processing \"%s\" at address 0x%08x: ----" % (mnemonic, stmt.addr))
					print("time to execute: %d" % tte)
					print("cumulative time in this path: %d" % timeSoFar)
		return timeSoFar
				
				
				
def TimingModel(instruction):
	return {
		'add': 1,
		'mov': 2,
	}.get(instruction,0)
		
		
angr.register_analysis(MockAnalysis, 'MockAnalysis')

#b = angr.Project("/bin/true")
b = angr.Project("/home/roeland/Documents/programs/fauxware/fauxware")
#b = angr.Project("/home/roeland/Documents/programs/test1/a.out")
mock = b.analyses.MockAnalysis(500, False)
mock.analyse()