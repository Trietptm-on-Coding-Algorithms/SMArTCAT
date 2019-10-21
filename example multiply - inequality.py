from __future__ import print_function
import claripy
import cdset
import analysisUtils as u

#define public, secret, and time symbols:
p1 = claripy.BVS("p1", 16)
s1 = claripy.BVS("s1", 16)
t1 = claripy.BVS("t1", 8)
p2 = claripy.BVS("p2", 16)
s2 = claripy.BVS("s2", 16)
t2 = claripy.BVS("t2", 8)

#create the constraint which defines the relationship between p,s, and t.
#they are all the same because this is a self composed program.
#normally this relationship would be expressed more complexly than with a simple if statement.
C1 = claripy.Solver()
C2 = claripy.Solver()
C1.add(t1 == claripy.If(s1*p1>=100, claripy.BVV(99,8), claripy.BVV(1,8)))
C2.add(t2 == claripy.If(s2*p2>=100, claripy.BVV(99,8), claripy.BVV(1,8)))

C1.add(claripy.SGT(s1, 0))
C1.add(claripy.SLE(s1, 255))
C1.add(claripy.SGT(p1, 0))
C1.add(claripy.SLE(p1, 255))
C2.add(claripy.SGT(s2, 0))
C2.add(claripy.SLE(s2, 255))
C2.add(claripy.SGT(p2, 0))
C2.add(claripy.SLE(p2, 255))
#compose the constraints for analysis
sol = claripy.Solver()
sol.add(C1.constraints)
sol.add(C2.constraints)


#create the relationship between the constraint copies
#p1 == p2
sol.add(p1 == p2)
#s1 != s2
sol.add(s1 != s2)
#t1!= t2
sol.add(t1 != t2)


assert(len(sol.eval(t1,2)) > 1)
#time hasn't concretized yet

#introduce k: s2 < k <= s1
k = claripy.BVS("k", 16)
sol.add(s1 >= k)
sol.add(s2 < k)

assert(len(sol.eval(t1,2)) == 1)
#time has concretized, but we don't yet know the meaning

#put s1 and s2 to the edge cases of k
sol.add(s1 == k)
sol.add(s2 == k-1)
sol.add(claripy.SGT(k, 0))
sol.add(claripy.SLE(k, 255))

#we can now query for concrete values on which we can differentiate:
sorted(sol.eval(k,300))

#say we want to differentiate on 50, we can find a corresponding public value p which generates this behavior.
sol.add(k==50)
sorted(sol.eval(p1,300))

#let's verify our results by putting p into the original function
C1.add(p1 == sol.eval(p1,300)[0])

#model behavior for both measured time = 99 and time = 1
C1t99 = C1.branch()
C1t99.add(t1 == 99)
C1t1 = C1.branch()
C1t1.add(t1 == 1)

print("secret for time = 99: %s; len: %s" % (sorted(C1t99.eval(s1,300)), len(C1t99.eval(s1,300))))
print("secret for time = 1: %s; len: %s" % (sorted(C1t1.eval(s1,300)), len(C1t1.eval(s1,300))))
