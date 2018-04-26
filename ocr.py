#coding:utf8

from PIL import Image
import pytesseract

def get_problem_title(fpath):
	with Image.open(fpath) as img:
		s = pytesseract.image_to_string(img)
		problem_title = s.split('\n')[0]
	return problem_title

def get_edit_distance(str1, str2):
	str1 = str1.lower()
	str2 = str2.lower()
	len1 = len(str1)
	len2 = len(str2)
	matrix = [range(len2+1) for i in range(len1+1)]
	for i in range(1, len1+1):
		matrix[i][0] = matrix[i-1][0] + 1
		for j in range(1, len2+1):
			#print str1[i-1]," ",str2[j-1]
			if(str1[i-1] == str2[j-1]):
				matrix[i][j] = matrix[i-1][j-1]
				#print i," ",j," ",matrix[i][j]
			else:
				matrix[i][j] = min(matrix[i-1][j-1], min(matrix[i-1][j], matrix[i][j-1]))+1
	return matrix[len1][len2]

if __name__ == '__main__':
	'''
	test get_problem_title
	'''
	fpath = "test/test1.jpg"
	img = Image.open(fpath)
	print get_problem_title(fpath)
	#img.show()
	'''
	test get_edit_distance
	'''
	s1 = "Merge"
	s2 = "Marga"
	print get_edit_distance(s1, s2)
