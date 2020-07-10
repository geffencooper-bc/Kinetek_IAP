from decoder import *

kin_sim = Decoder("socket_can")

kin_sim.init_simulator("vcan0")
kin_sim.run_simulator()