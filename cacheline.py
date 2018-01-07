class Cacheline(object):
	def __init__(self):
		self.Validity = "Invalid"
		self.Address = -1
		self.Tag = -1
		self.Ranking = -1

	def _setValidity(self, Validity):
		self.Validity = Validity
	def _setAddress(self, Address):
		self.Address = Address
	def _setTag(self, Tag):
		self.Tag = Tag
	def _setRanking(self, Ranking):
		self.Ranking = Ranking
	
	def _getValidity(self):
		return self.Validity
	def _getAddress(self):
		return self.Address
	def _getTag(self):
		return self.Tag
	def _getRanking(self):
		return self.Ranking
