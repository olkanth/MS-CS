import m5
from m5.objects import *
from caches import *
import argparse
from gem5.resources.resource import obtain_resource


parser = argparse.ArgumentParser(description='A simple system with 2-level cache.')
parser.add_argument("--l1i_size", help=f"L1 instruction cache size. Default: 16kB.")
parser.add_argument("--l1d_size", help="L1 data cache size. Default: Default: 64kB.")
parser.add_argument("--l2_size", help="L2 cache size. Default: 256kB.")
parser.add_argument('--cache_line_size', type=int, default=64, help='Cache line size in bytes (affects all caches)')
parser.add_argument('--dcache_assoc', type=int, default=2, help='L1D cache associativity')
options = parser.parse_args()

# Create a system
system = System()
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

# Set up the memory system
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

# Set global cache line size BEFORE creating caches
system.cache_line_size = options.cache_line_size

# Create a CPU
system.cpu = X86TimingSimpleCPU()

# Create a L1 I-cache and D-cache
system.cpu.icache = L1ICache(options)
system.cpu.dcache = L1DCache(options)
system.cpu.dcache.assoc = options.dcache_assoc

# Connect the CPU to the memory bus
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)

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

#binary = 'tests/test-progs/hello/bin/x86/linux/hello'
binary = obtain_resource(resource_id="x86-matrix-multiply")

# # for gem5 V21 and beyond
system.workload = SEWorkload.init_compatible(binary.get_local_path())

# Create a process
process = Process()
process.cmd = [binary.get_local_path()]
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


# Print statistics
print("\nSimulation completed!")


# Access statistics through the simulation object's statistics dictionary
print(f"D-Cache Size: {system.cpu.dcache.size}")
print(f"D-Cache line size: {system.cache_line_size}")
print(f"D-Cache Associativity: {system.cpu.dcache.assoc}")

print("\nD-Cache Statistics:")
print("-----------------")

# Dump all statistics
m5.stats.dump()

# Reset all stats for the next run
m5.stats.reset()

print("\nDetailed statistics have been dumped above.")


