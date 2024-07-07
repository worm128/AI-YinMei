def singleton(cls):
    instances = {}
    def getInstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    def delInstance():
        del instances[cls]

    getInstance.delInstance = delInstance
    return getInstance

@singleton
class class1:
     is_singing = 1
     __xx=3
     def __init__(self,val):
         self.is_singing = val

     def print_val(self):
         print(self.is_singing)

     def alter_val(self,val):
         self.is_singing = val

     def __del__(self):
         print("MyClass 实例销毁")


@singleton
class class2:
     swing_motion = 1
     def __init__(self,val):
         self.swing_motion = val

     def print_val(self):
         print(self.swing_motion)


