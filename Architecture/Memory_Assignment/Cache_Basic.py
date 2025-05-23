#!/usr/bin/env python3

import m5
from m5.objects import *
import sys
import os


# Create a system
system = System()

# Set the clock frequency
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

# Create a CPU
system.cpu = TimingSimpleCPU()

# Create the memory system
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

# Create the memory bus
system.membus = SystemXBar()

# Create and configure the D-cache
system.cpu.dcache = L1_DCache()
system.cpu.dcache.size = '64kB'  # Default size
system.cpu.dcache.assoc = 2      # Default associativity
system.cpu.dcache.tag_latency = 2
system.cpu.dcache.data_latency = 2
system.cpu.dcache.response_latency = 2
system.cpu.dcache.mshrs = 4
system.cpu.dcache.tgts_per_mshr = 20

# Connect the CPU to the memory bus
system.cpu.connectBus(system.membus)

# Create the memory controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# Create the process
process = Process()
process.cmd = ['tests/test-progs/hello/bin/x86/linux/hello']
system.cpu.workload = process
system.cpu.createThreads()

# Set up the root
root = Root(full_system=False, system=system)

# Create the simulation
m5.instantiate()

# Run the simulation
print("Beginning simulation!")
exit_event = m5.simulate()

# Print statistics
print("\nSimulation completed!")
print("\nD-Cache Statistics:")
print("-----------------")
print(f"D-Cache Hit Rate: {system.cpu.dcache.overall_hits / (system.cpu.dcache.overall_hits + system.cpu.dcache.overall_misses):.2%}")
print(f"D-Cache Miss Rate: {system.cpu.dcache.overall_misses / (system.cpu.dcache.overall_hits + system.cpu.dcache.overall_misses):.2%}")
print(f"Average Memory Access Latency: {system.cpu.dcache.avg_miss_latency:.2f} cycles")
print(f"Total D-Cache Accesses: {system.cpu.dcache.overall_hits + system.cpu.dcache.overall_misses}")
print(f"D-Cache Size: {system.cpu.dcache.size}")
print(f"D-Cache Associativity: {system.cpu.dcache.assoc}")