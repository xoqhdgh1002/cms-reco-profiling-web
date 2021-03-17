import re
import sys
import numpy as np
import pandas as pd

class TimeMem():

	def Get_TimeMem(self,data):

		matching1 = re.compile('^MemoryCheck')
		matching2 = re.compile('^TimeEvent')

		self.vsize = []
		self.rss = []
		self.event = []
		self.time = []

		with open(data,'r') as file:

			for i in file:

				if matching1.match(i):
					self.vsize.append(float(i.split()[4]))
					self.rss.append(float(i.split()[7]))

				if matching2.match(i):
					self.event.append(int(i.split()[1]))
					self.time.append(float(i.split()[3]))

		return pd.DataFrame({"vsize":self.vsize,"rss":self.rss,"event":self.event,"time":self.time})
