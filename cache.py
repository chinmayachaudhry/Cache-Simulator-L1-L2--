from math import *
from cacheline import Cacheline

non_exclusive_cache_access = True

class Cache(object):


	def __init__(self, blocksize, size, assoc, repl_Policy, inclusion):
		self.Trace_num = 0
		self.nextLevel_Cache = None

		self.supporting_vars = {
			"Evicted" : False,
			"EvictedAddress" : -1,
			"Hit" : False,	
			"Way" : -1,
			"WriteBack" : False
		}

		# Cache Paramemters
		self.size = size
		self.blocksize = blocksize
		self.assoc = assoc
		self.repl_Policy = repl_Policy
		self.inclusion = inclusion
		
		# Define Cache
#		self.cache = []
		self.Sets = (self.size)/(self.assoc * self.blocksize)
		self.Cachelines = self.Sets * self.assoc
		self.cache = [Cacheline() for j in range(self.Cachelines)]

		# Size of Index, Blockoffset and Tag from Address
		self.offset_Width = int(log(blocksize, 2))
		self.index_Width = int(log(self.Sets, 2))
		self.tag_Width = int(64 - self.offset_Width - self.index_Width)

		# Masks to calculate Index, Offset and Tag
		self.offset_Mask = self._get_mask(self.offset_Width)
		self.index_Mask = self._get_mask(self.index_Width + self.offset_Width)
		self.tag_Mask = self._get_mask(self.tag_Width + self.index_Width + self.offset_Width)
	
		# Performance Variables
		self._Reads = 0
		self._Writes = 0
		self._RdMiss = 0
		self._WtMiss = 0
		self._RdHits = 0
		self._WtHits = 0
		self._Writebacks = 0
		self._Mem_Traffic = 0
		self._BackInvalidation_WB = 0

		
		# PSeudo Replacement Policy
		if self.repl_Policy == "Pseudo":
			self.PseudoLRU = [None] * self.Cachelines

	def _get_mask(self, width):
		mask = 0
		for i in range(0, width, 1):
			mask = mask << 1
			mask = mask | 1
		return mask	
		
	def _calcOffset(self, address):
		return (address & self.offset_Mask)

	def _calcIndex(self, address):
		return ((address & self.index_Mask) >> self.offset_Width)	

	def _calcTag(self, address):
		return ((address & self.tag_Mask) >> (self.index_Width + self.offset_Width))
	
	def _getSet(self, List, Index):
		return (List[(self.assoc * Index):(Index+1) * self.assoc])
 
	def _blockAccess(self, address, op):
		self.supporting_vars["Evicted"] = False
		self.supporting_vars["Hit"] = False
		self.supporting_vars["Way"] = -1
#		self.supporting_vars["EvictedAddress"] = -1
		self.supporting_vars["WriteBack"] = False

		self.Trace_num = self.Trace_num + 1

		if(op == 'r'):
			self._Reads = self._Reads + 1
		else:
			self._Writes = self._Writes + 1
	
		Cache_Cell = self._findBlock(address)
		if (Cache_Cell == None):
#			print "Cell Not Found"
			self.supporting_vars["Hit"] = False
			if (op == 'r'):
				self._RdMiss = self._RdMiss + 1
			else:
				self._WtMiss = self._WtMiss + 1

			self._Mem_Traffic = self._Mem_Traffic + 1
			if non_exclusive_cache_access == True:
				Cache_Cell = self._replaceCell(address)
		else:
#			print "Cell Found"
			self.supporting_vars["Hit"] = True
			if(op == 'r'):
				self._RdHits = self._RdHits + 1
			else:
				self._WtHits = self._WtHits + 1	
			
			self._updateRanking(Cache_Cell, address)
		
		if(op == 'w'):
			Cache_Cell._setValidity("Dirty")
	
	def _findBlock(self, address):
		Tag = self._calcTag(address)
		Index = self._calcIndex(address)
		cacheSet = self._getSet(self.cache, Index)		
#		print "Before findblock loop: "		
		for way in range(0, self.assoc):		
			if((cacheSet[way]._getTag() == Tag) and (cacheSet[way]._getValidity() != "Invalid")):
				self.supporting_vars["Way"] = way
				return cacheSet[way]
		else:
			return None			

	def _replaceCell(self, address):
		Tag = self._calcTag(address)
		Index = self._calcIndex(address)
		Evicted_Block = self._getBlocktoReplace(Index)

		if Evicted_Block._getValidity() == "Dirty":
			self.supporting_vars["WriteBack"] = True
			self._Writebacks = self._Writebacks + 1
			self._Mem_Traffic = self._Mem_Traffic + 1
	
		Evicted_Block._setTag(Tag)
		Evicted_Block._setAddress(address)
		Evicted_Block._setValidity("Valid")
		self._updateRanking(Evicted_Block, address) 
		
		return Evicted_Block

	def _getBlocktoReplace(self, Index):
		Block_toReplace = self._getInvalidBlock(Index)
		if(Block_toReplace == None):
			Block_toReplace = self._getReplacementBlock(Index)
			self.supporting_vars["Evicted"] = True
			self.supporting_vars["EvictedAddress"] = Block_toReplace._getAddress()

		return Block_toReplace

	def _getInvalidBlock(self, Index):
		cacheSet = self._getSet(self.cache, Index)
		for way in range(0, self.assoc):
			if cacheSet[way]._getValidity() == "Invalid":
				self.supporting_vars["Way"] = way 
				return cacheSet[way]
		else:
			return None

	def _getReplacementBlock(self, Index):
		self._findWaytoReplace(Index)
		Way = self.supporting_vars["Way"]
		return self.cache[(self.assoc * Index) + Way]

	def _findWaytoReplace(self, Index):
		Way = 0
		minimum = self.Trace_num
		cacheSet = self._getSet(self.cache, Index)
		if(self.repl_Policy == "LRU" or self.repl_Policy == "FIFO"):
			for i in range(0, self.assoc):
				if(cacheSet[i]._getRanking() < minimum):
					minimum = cacheSet[i]._getRanking()
					Way = i
		
		if(self.repl_Policy) == "Pseudo":
			current_node = int(1)
			i = int(0)
			j = int(self.assoc)
			count = int(0)
			pseudoSet = self._getSet(self.PseudoLRU, Index)
			while(count < int(log(self.assoc, 2))):
				if pseudoSet[current_node] == 0:
					current_node = (2 * current_node) + 1
					i = ((j - i)/2) + i
				else:
					current_node = (2 * current_node)
					j = ((j - i)/2) + i
				count = count + 1
			
			self.PseudoLRU[(self.assoc * Index):(Index + 1) * self.assoc] = pseudoSet	
			Way = i

		self.supporting_vars["Way"] = Way

	def _updateRanking(self, Cache_Cell, address):
		if (self.repl_Policy == "LRU"):
			Cache_Cell._setRanking(self.Trace_num)
		
		if(self.repl_Policy == "FIFO"):
			if self.supporting_vars["Hit"] == False:
				Cache_Cell._setRanking(self.Trace_num)

		if(self.repl_Policy == "Pseudo"):
			Index = self._calcIndex(address)
			pseudoSet = self._getSet(self.PseudoLRU, Index)
			position = self.supporting_vars["Way"]
			current_node = 1
			j = self.assoc
			i = 0
			count = int(0)
			while(count < int(log(self.assoc, 2))):
				if position < (((j - i)/2) + i):
					pseudoSet[current_node] = 0
					current_node = 2 * current_node
					j = ((j - i)/2) + i
				else:
					pseudoSet[current_node] = 1
					current_node = (2 * current_node) + 1
					i = (j/2) + i
				count = count + 1				
			self.PseudoLRU[(self.assoc * Index):(Index + 1) * self.assoc] = pseudoSet	

	def invalidateCache(self, address):
		cacheline = self._findBlock(address)
		if cacheline != None:
			if self.inclusion == "inclusive":
				if cacheline._getValidity() == "Dirty":
					self.supporting_vars["WriteBack"] = True
					self._BackInvalidation_WB = self._BackInvalidation_WB + 1
			cacheline._setValidity("Invalid")				
			
