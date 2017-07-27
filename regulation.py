from Python_Fluigent import *
from sys import stdout
import time

mfcs = MFCS_EZ()
frp = FRP()
Q0 = [10,10] #uL/min
PdQ= [0,0]
IdQ = [0,0]
PdQprev = [0,0]
DdQ = [0,0]
P0 = [0,0]

#PID coefficients
p = 1.
i = 1.
d = 0.
P0min = 0.
P0max = 1024.

while True:
    Q = frp.read_flow_rate([1,2])
    P = mfcs.read_pressure([1,2])
    for ch in range(len(Q0)):
        PdQ[ch] = Q0[ch]-Q[ch].value            #prop error
        IdQ[ch] = IdQ[ch]+ PdQ[ch]              #int error
        DdQ[ch] = PdQ[ch]-PdQprev[ch]           #der error
        PdQprev[ch] = PdQ[ch]
        P0[ch] = max(min(p*PdQ[ch]+i*IdQ[ch]+d*DdQ[ch],P0max),P0min) 
    mfcs.set_pressure([1,2],P0)
    for q in Q: print(q)
    print('consign pressure: '+str(P0))
    print('real pressure: '+str(P))
    stdout.flush()
    time.sleep(0.5)



mfcs.purge()
mfcs.set_pressure([1,2],[150,150])
p = mfcs.read_pressure([1,2])
print(p)
time.sleep(1)
mfcs.set_pressure([1,2],[0,0])
p = mfcs.read_pressure([1,2])
del(mfcs)


frp.read_flow_rate([1,2])
del frp
