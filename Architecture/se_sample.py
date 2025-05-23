#!/usr/bin/env python3

import m5
from m5.objects import *
from gem5.resources.resource import obtain_resource

# Create a system
system = System()

# Set the clock frequency
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

# Set up the memory system
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

# Create a CPU
system.cpu = X86TimingSimpleCPU()

# Create a memory bus
system.membus = SystemXBar()

# Connect the CPU to the memory bus
system.cpu.icache_port = system.membus.cpu_side_ports
system.cpu.dcache_port = system.membus.cpu_side_ports

# Create a memory controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# Create the interrupt controller
system.cpu.createInterruptController()
# Connect the interrupt controller to the memory bus
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

binary = 'tests/test-progs/hello/bin/x86/linux/hello'

# for gem5 V21 and beyond
system.workload = SEWorkload.init_compatible(binary)

# for gem5 V21 and beyond
# system.workload = SEWorkload.init_compatible(binary)

# Create a process
process = Process()
# Example path to an x86 binary - replace with your actual binary path
process.cmd = [binary]
system.cpu.workload = process
system.cpu.createThreads()

# Set up the root
root = Root(full_system=False, system=system)

# Instantiate all of the objects
m5.instantiate()

# Run the simulation
print("Beginning simulation!")
exit_event = m5.simulate()
print('Exiting @ tick {} because {}'.format(m5.curTick(), exit_event.getCause()))
