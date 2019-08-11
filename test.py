from urllib import request

url='http://www.pythonchallenge.com/pc/def/linkedlist.php?nothing=12345'
k=request.urlopen(url).read()
k=str(k)
k=k.split(" ")
print(k)
