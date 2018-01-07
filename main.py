import sys
import math
# from cache import Cache
# import global_vars 
# from cache import Cache
import cache

def print_config(block, size1, assoc1, size2, assoc2, rep, incl, input_file):
	print "===== Simulator configuration ====="
	print "BLOCKSIZE:              " + str(block)
	print "L1_SIZE:                " + str(size1)
	print "L1_ASSOC:               " + str(assoc1)
	print "L2_SIZE:                " + str(size2)
	print "L2_ASSOC:               " + str(assoc2)
	print "REPLACEMENT POLICY:     " + str(rep)
	print "INCLUSION PROPERTY:     " + str(incl)
	print "trace_file:             " + str(input_file)

def print_results(L1):
	print "===== Simulation Results (raw) ====="
	print "a. number of L1 reads:             " + str(L1._Reads)
	print "b. number of L1 read misses:       " + str(L1._RdMiss)
	print "c. number of L1 writes:            " + str(L1._Writes)
	print "d. number of L1 write misses:      " + str(L1._WtMiss)
	miss_rate = (float(L1._RdMiss + L1._WtMiss)) / (L1._Reads + L1._Writes)
#	miss_rate =  math.ceil(miss_rate * 1000000.0) / 1000000.0
	print "e. L1 miss rate:                   %.06f" %miss_rate
	print "f. number of L1 writebacks:        " + str(L1._Writebacks) 	
	
	if(L1.nextLevel_Cache == None):		
		print "g. number of L2 reads:             %d" %(0)
		print "h. number of L2 read misses:       " + str(0)
		print "i. number of L2 writes:            " + str(0)
		print "j. number of L2 write misses:      " + str(0)
		print "k. L2 miss rate:                   " + str(0)
		print "l. number of L2 writebacks:        " + str(0)
		print "m. total memory traffic:           " + str(L1._Mem_Traffic) 	
	else:	
		print "g. number of L2 reads:             " + str(L2._Reads)
		print "h. number of L2 read misses:       " + str(L2._RdMiss)
		print "i. number of L2 writes:            " + str(L2._Writes)
		print "j. number of L2 write misses:      " + str(L2._WtMiss)
		L2_miss_rate = (float(L2._RdMiss + L2._WtMiss)) / (L2._Reads + L2._Writes)
		print "k. L2 miss rate:                   %.06f" %L2_miss_rate
		print "l. number of L2 writebacks:        " + str(L2._Writebacks)
		print "m. total memory traffic:           " + str(L1._BackInvalidation_WB + L2._Mem_Traffic) 	

####### MAIN Function #####

BlockSize = int(sys.argv[1])
L1_Size = int(sys.argv[2])
L1_Assoc = int(sys.argv[3])
L2_Size = int(sys.argv[4])
L2_Assoc = int(sys.argv[5])
repl = int(sys.argv[6])
inclusion = int(sys.argv[7])
Trace_File = str(sys.argv[8])

repl_policies = { 0 : "LRU", 1 : "FIFO", 2 : "Pseudo"}
incl_policies = {0 : "non-inclusive", 1 : "inclusive", 2 : "exclusive"}

Replacement_Policy = repl_policies[repl]
Inclusion_Policy = incl_policies[inclusion]

# print "Replacement: %s" %Replacement_Policy
# print "Inclusion: %s" %Inclusion_Policy

#L1 = Cache(64, 1024, 2, "LRU", "non-innclusive")
L1 = cache.Cache(BlockSize, L1_Size, L1_Assoc, Replacement_Policy, Inclusion_Policy)
if L2_Size != 0:
	L2 = cache.Cache(BlockSize, L2_Size, L2_Assoc, Replacement_Policy, Inclusion_Policy)
	L1.nextLevel_Cache = L2

#print L1 
#print str(L1.blocksize) + "Block"

with open(Trace_File, "rb") as file:
	all_lines = file.read().splitlines()

for line in all_lines:
	char, address = line.split(" ")
#	print "Char: " + char
#	print "Address: " + address
#	print "Converted Back: " + str(hex(int(address, 16)))
#	print type(address)
#	print (long(address, 16))
	L1._blockAccess(long(address, 16), char)
	if L2_Size != 0:
		if Inclusion_Policy == "non-inclusive":
			if L1.supporting_vars["WriteBack"] == True:	
				L2._blockAccess(L1.supporting_vars["EvictedAddress"], 'w')
			if L1.supporting_vars["Hit"] == False:
				L2._blockAccess(long(address, 16), 'r')

		if Inclusion_Policy == "inclusive":	
			if L1.supporting_vars["WriteBack"] == True:	
				L2._blockAccess(L1.supporting_vars["EvictedAddress"], 'w')
				if L2.supporting_vars["Evicted"] == True:
					L1.invalidateCache(L2.supporting_vars["EvictedAddress"])	
			if L1.supporting_vars["Hit"] == False:
				L2._blockAccess(long(address, 16), 'r')
				if L2.supporting_vars["Evicted"] == True:
					L1.invalidateCache(L2.supporting_vars["EvictedAddress"])

		if Inclusion_Policy == "exclusive":
			if L1.supporting_vars["Hit"] == True:
				L2.invalidateCache(long(address, 16))
			if L1.supporting_vars["Evicted"] == True:
				L2._blockAccess(L1.supporting_vars["EvictedAddress"], 'w')
				if L1.supporting_vars["WriteBack"] == False:
					
#					print L2._findBlock(L1.supporting_vars["EvictedAddress"])
					L2._findBlock(L1.supporting_vars["EvictedAddress"])._setValidity("Valid")

#					print L2._findBlock(L1.supporting_vars["EvictedAddress"])
			if L1.supporting_vars["Hit"] == False:
				cache.non_exclusive_cache_access = False
				L2._blockAccess(long(address, 16), 'r')

				cache.non_exclusive_cache_access = True
				if L2.supporting_vars["Hit"] == True:
					if L2._findBlock(long(address, 16))._getValidity() == "Dirty":
						L1._findBlock(long(address, 16))._setValidity("Dirty")
					L2.invalidateCache(long(address, 16))
				
#for i in range(L1.size/L1.blocksize):
#		print L1.cache[i]
#print L1.getSize()
#print L1.getBlocksize()
#print L1.getAssoc()
#print L1.getrepl_Policy()
#print L1.getInclusion()
#print L1.printCache()

print_config(BlockSize, L1_Size, L1_Assoc, L2_Size, L2_Assoc, Replacement_Policy, Inclusion_Policy, Trace_File)

print_results(L1)

#	print L1._RdHits
#	print L1._WtHits
