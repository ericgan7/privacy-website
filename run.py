import draw
import time
import os

d = draw.draw()

def file_range(file, start, end, delta):
	for i in range(start, end + 1):
		filename=file + str(i) + '.csv'
		if (d.new(filename, delta)):
			if(d.run(i, delta)):
				continue
			else:
				print (filename)
				os.rename(filename, 'data/invalid/tourset' + str(i) + '.csv')

	print(time.time() - start_t)
    
def file_single(file):
    d.new(file, 1)

file = 'data/tourset'
start = 1
end = 279

start_t = time.time()
file_range(file, start, end, delta = '0.2')
