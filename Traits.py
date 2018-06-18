

import pandas as pd
import matplotlib.pyplot as plt,mpld3
import matplotlib
from textwrap import wrap
# from matplotlib.figure import Figure
matplotlib.use('TkAgg')
plt.style.use('ggplot')

plt.style.use('ggplot')


'''
this class will transform the given data in a meaningfull dataset of candidate traits and plot it in the form of bar charts.
'''
class CandidateTraits():
	
	
	def __init__(self,file_path):
		self.data=pd.read_excel(file_path,header=None)

		'''
		this function will result into a dataframe with all candidates data.
		'''
	def candidate_data(self): 
		traits_data=self.data.iloc[0:10]
		traits_data=traits_data.iloc[:,:-4]
		fill_traits=[]
		self.test=traits_data.iloc[0,2:].astype(str).tolist()
		self.groups=list(set(self.test))
		self.groups.remove('nan')

		for trait in self.test:
		    if trait !='nan':
		            fill_traits.extend([trait]*self.count_nan(trait))

		self.final_frame=traits_data.iloc[1:].transpose()
		self.final_frame['trait_group']=pd.Series(['trait_group']*2+fill_traits)
		self.final_frame.columns=self.final_frame.iloc[0]
		self.final_frame=self.final_frame.iloc[3:]

		'''
		This function accepts candidate name as parameter and will plot bar chart of each candidate
		'''

	def plot_candidate_traits(self,candidate_name):
		col_list=list(self.final_frame.columns)
		fig=plt.figure()
		ax=fig.add_subplot(111)
		if candidate_name in col_list[1:-1]:
			plot_data=pd.DataFrame((self.final_frame.iloc[2:][candidate_name].astype('float').groupby(self.final_frame['trait_group']).mean()))
			labels = [ '\n'.join(wrap(l, 15)) for l in list(plot_data.index) ]
			ax.set_xticklabels(labels)
			barlist=ax.bar(list(plot_data.index),plot_data[candidate_name].tolist(),color='b')
			for i in barlist[6:9]:
				i.set_color('r')
			plt.show()

	'''
	This function will count the number of nan values between the trait groups ( this is a helping function used to transpose the dataframe)
	'''

	def count_nan(self,t):
		
		ncount=0
		for i in self.test[self.test.index(t)+1:]:
			if i!='nan':
				break
			if i=='nan':
				ncount+=1
		return ncount+1 # add 1 to add trait_grp as trait



if __name__=='__main__':
	ct=CandidateTraits('/home/vinove/HarrisonData/HATS - Sample Trait Export - 2018.xls')
	ct.candidate_data()
	ct.plot_candidate_traits('Ram Kumar')
	

