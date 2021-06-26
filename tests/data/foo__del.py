class MyData:
  
    def __del__(self):
        print('test __del__ OK')


data = MyData()
