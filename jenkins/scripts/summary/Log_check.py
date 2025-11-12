import re
import sys
import numpy as np
import pandas as pd

class TimeMem():

	def Get_TimeMem(self,input_data):

		matching1 = re.compile('^TimeEvent')
		matching2 = re.compile('^MemoryCheck')
		matching3 = re.compile('%MSG-w MemoryCheck:  PostProcessPath')

		self.event1 = []
		self.time = []
		self.event2 = []
		self.vsize = []
		self.rss = []

		with open(input_data,'r') as file:
			flag = 0
			for i in file:
				if matching1.match(i):
					self.event1.append(int(i.split()[1]))
					self.time.append(float(i.split()[3]))
				if matching3.match(i):
					if len(i.split()) < 10:
						self.event2.append(self.event1[-1])
					else:
						self.event2.append(int(i.split()[9]))
					flag = 1
					continue;
				if flag == 1:
					self.vsize.append(float(i.split()[4]))
					self.rss.append(float(i.split()[7]))
					flag = 0
				
		print(len(self.vsize),len(self.rss),len(self.event2),len(self.time))
	
		df1 = pd.DataFrame({"event":self.event1,"time":self.time})
		df2 = pd.DataFrame({"event":self.event2,"vsize":self.vsize,"rss":self.rss})

		return pd.merge(df1,df2,on="event",how="outer").sort_values(by="event")

	def summary(self,output_data):

		f = open(output_data,"w")
		f.write("Summary for {} events\n".format(len(self.time)))
		f.write("Max VSIZ {0} on evt {1} ; max RSS {2} on evt {3}\n".format(max(self.vsize),self.event2[self.vsize.index(max(self.vsize))],max(self.rss),self.event2[self.rss.index(max(self.rss))]))
		f.write("Time av {0:0.5f} s/evt   max {1} s on evt {2}\n".format(sum(self.time)/len(self.time),max(self.time),self.event1[self.time.index(max(self.time))]))
		f.write("M1 Time av {0:0.5f} s/evt   max {1} s on evt {2}\n".format(sum(self.time[1:])/len(self.time[1:]),max(self.time[1:]),self.event1[self.time.index(max(self.time[1:]))]))
		f.write("M8 Time av {0:0.5f} s/evt   max {1} s on evt {2}".format(sum(self.time[8:])/len(self.time[8:]),max(self.time[8:]),self.event1[self.time.index(max(self.time[8:]))]))
		f.close()
