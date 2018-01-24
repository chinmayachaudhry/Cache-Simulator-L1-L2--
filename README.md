# README
Generic Cache Simulator written in Python. It models a Multi-Level cache with parameterized geometry, replacement and inclusion policy. Supports two level of heirarchy i.e. L1 and L2 cache. Different _INCLUSION_ properties include,Non-Inlusive Non-Exclusive, Inclusive and Exclusive. Different _REPLACEMENT_ policies include Least Recently Used(__LRU__), First in First out (__FIFO__) and PseudoLRU. The _WRITE-BACK_ policy used is _WRITE-BACK WRITE ALLOCATE_

## Command Line / Run Simulator
python main.py BLOCKSIZE L1_SIZE L1_ASSOC L2_SIZE L2_ASSOC REPL_POLICY INCLUSION TRACE_FILE
- __BLOCKSIZE__: Positive int. Block size in bytes
- __L1_SIZE__: Positive int. L1 cachesize in bytes
- __L1_ASSOC__: Positive int. L1 set-associativty (1 is direct mapped)
- __L2_SIZE__: Positive int. L2 cachesize in bytes; 0signifies the absence of L2 cache
- __L2_ASSOC__: Positive int. L2 set-associativty (1 is direct mapped)
- __REPL_POLICY__: Positive int. 0 for LRU, 1 for FIFO, 2 for PseudoLRU
- __INCLUSION__: Positive int. 0 for Non-Inclusive Non-Exclusive, 1 for Inclusive, 2 for Exclusive
- __TRACE_FILE__: Full name of trace file including extensions.

## Simulator Input
**r|w Address**
- The first arguument is the operation. __r__ means a read operation and __w__ means a write operation
- The second argument is the address accessed, in _Hexadecimal_ format. Address can be upto 64 bits long
