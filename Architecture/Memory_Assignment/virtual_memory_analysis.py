import m5
from m5.objects import *
import argparse
from gem5.resources.resource import obtain_resource
from caches import *

# Command-line options
parser = argparse.ArgumentParser(description='A simple system for Virtual memory analysis.')
parser.add_argument("--l1i_size",  type=str, default="64kB", help=f"L1 instruction cache size. Default: 16kB.")
parser.add_argument("--l1d_size", type=str, default="256kB", help="L1 data cache size. Default: Default: 64kB.")
parser.add_argument("--l2_size", type=str, default="256kB", help="L2 cache size. Default: 256kB.")
parser.add_argument("--itlb_size", type=int, default=64, help="Instruction TLB entries")
parser.add_argument("--dtlb_size", type=int, default=128, help="Data TLB entries")
# parser.add_argument("--cmd", type=str, help="Binary to run with full path", default="/home/user/test_program")
parser.add_argument('--dcache_assoc', type=int, default=2, help='L1D cache associativity')
options = parser.parse_args()

# System setup
system = System()
system.clk_domain = SrcClockDomain(clock="2GHz", voltage_domain=VoltageDomain())
system.mem_mode = "timing"
system.mem_ranges = [AddrRange("512MB")]

# CPU
system.cpu = X86TimingSimpleCPU()


# Memory system

system.cpu.icache = L1ICache()
system.cpu.dcache = L1DCache()
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)
system.cpu.dcache.assoc = options.dcache_assoc

# Connect CPU side bus to L2 cache
system.l2bus = L2XBar()
system.cpu.icache.connectBus(system.l2bus)
system.cpu.dcache.connectBus(system.l2bus)

system.l2cache = L2Cache(options)
system.l2cache.connectCPUSideBus(system.l2bus)

# Connect L2 cache to memory bus
system.membus = SystemXBar()
system.l2cache.connectMemSideBus(system.membus)


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


# TLB setup
system.cpu.mmu = X86MMU()
system.cpu.mmu.itb.size = options.itlb_size
system.cpu.mmu.dtb.size = options.dtlb_size


binary = obtain_resource(resource_id="x86-matrix-multiply")

# # for gem5 V21 and beyond
system.workload = SEWorkload.init_compatible(binary.get_local_path())

# Process
process = Process()
process.cmd = [binary.get_local_path()]
system.cpu.workload = process
system.cpu.createThreads()

# Root and run
root = Root(full_system=False, system=system)
m5.instantiate()

print("Starting simulation...")
exit_event = m5.simulate()
print("Exited at tick {} because {}".format(m5.curTick(), exit_event.getCause()))

# Dump all statistics
m5.stats.dump()

# Reset all stats for the next run
m5.stats.reset()

print("\nDetailed statistics have been dumped above.")
