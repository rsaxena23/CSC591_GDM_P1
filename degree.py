from graphframes import *
from pyspark.sql import SQLContext,Row
from pyspark import SparkContext, SparkConf
from math import *
import math
import matplotlib.pyplot as pyplot

class Degree:
	sc = None
	conf = None
	degree_frequency = None
	sqlContext = None
	res_graph = None
	total_vertex = None
	x_list = list()
	y_list = list()

	def setSC(self,appName,master):
		self.conf = SparkConf().setAppName(appName).setMaster(master)
		self.sc = SparkContext(conf=self.conf)

	def setSQLConextext(self):
		self.sqlContext=SQLContext(self.sc)

	def createGF(self):
		in_file = self.sc.textFile("/home/abhishek/Downloads/network/stanford_graphs/youtube.graph.small")
		op_rdd = in_file.map(lambda line: line.split(",")).map(lambda line : Row(src=line[0],dst=line[1]))
		edge_df = self.sqlContext.createDataFrame(op_rdd)
		edge_df.registerTempTable("edge_list")
		vertice_df = self.sqlContext.sql("SELECT distinct src as id from edge_list UNION SELECT distinct dst as id from edge_list")
		self.total_vertex = vertice_df.count()
		self.res_graph = GraphFrame(vertice_df,edge_df)

	def execute(self):
		createGF()
		self.res_graph.inDegrees.show()
		degree_list = self.res_graph.outDegrees
		degree_list.registerTempTable("degree")
		degree_count = self.sqlContext.sql("SELECT outDegree as degree,count(*) as freq from degree group by outDegree order by outDegree")

		self.degree_frequency = degree_count

	def displayPowerLaw(self):
		for i in self.degree_frequency.collect():
			log_pk = math.log(i.freq/float(self.total_vertex))
			if i.degree == 1:
				log_k = math.log(i.degree + 1)
			else:
				log_k = math.log(i.degree)
			log_k = log_k*(-1)
			res = log_pk/log_k
			print str(i.degree) + "->" + str(res)
			self.x_list.append(i.degree)
			self.y_list.append(res)

	def plot(self):
		pyplot.xlabel('Degree')
		pyplot.ylabel('gamma')
		pyplot.plot(self.x_list,self.y_list)
		pyplot.show()

def main():
	d = Degree()
	d.setSC('degree','local')
	d.setSQLConextext()
	d.execute()
	d.displayPowerLaw()
	d.plot()

if __name__ == '__main__':
	main()