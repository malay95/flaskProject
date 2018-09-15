import matplotlib.pyplot as plt
import numpy as np
import base64
import io

def build_graph(x,y):
	img = io.BytesIO()
	plt.plot(x,y)
	plt.savefig(img, format='png')
	img.seek(0)
	graph_url = base64.b64encode(img.getvalue()).decode()
	plt.close()
	return 'data:image/png;base64,{}'.format(graph_url)