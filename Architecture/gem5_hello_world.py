from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.cachehierarchies.classic.no_cache import NoCache
from gem5.components.memory.single_channel import SingleChannelDDR3_1600
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.components.processors.cpu_types import CPUTypes
from gem5.isas import ISA
from gem5.resources.resource import obtain_resource
from gem5.simulate.simulator import Simulator

# Create component objects
# This example uses a simple board with a single core and no cache hierarchy
cache_hierarchy = NoCache()
memory = SingleChannelDDR3_1600("1GiB")
processor = SimpleProcessor(cpu_type=CPUTypes.ATOMIC, num_cores=1, isa=ISA.X86)

# Create a simple board with the components
# The clock frequency is set to 3GHz
board = SimpleBoard(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

# Load a binary workload into the board
# The binary is a simple hello world program compiled for x86_64
binary = obtain_resource(resource_id="x86-hello64-static")
board.set_se_binary_workload(binary)

# Create a simulator object
# The simulator will run the workload on the board
simulator = Simulator(board=board)
simulator.run()