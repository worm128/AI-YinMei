
import queue
 
q = queue.PriorityQueue()  # 创建优先级队列
 
# 使用put方法时，可以传递一个元组，其中元组的第一个元素是优先级
q.put([3, 'A'])
q.put([-2, 'B'])
q.put([-1, 'C'])

while not q.empty():
    str = q.get_nowait()
    print(str[1])


my_list = [2, 3, 4]
my_list.insert(0, 11)
print(my_list)
