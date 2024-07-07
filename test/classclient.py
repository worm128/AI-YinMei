from classtest import class1
from classtest import class2
import gc
import time
if __name__ == "__main__":
    c1 = class1(5)
    c1.is_singing = 1
    c1.print_val()

    c1 = class1(5)
    c1.print_val()
    # c1.is_singing=2
    # c1.print_val()
    # c1.alter_val(3)
    # c1.print_val()
    #
    # c2 = class2(5)
    # c2.print_val()

    #c1.del_singleton()
    # del c1
    # gc.collect()
    # time.sleep(10)
    class1.delInstance()
    c1 = class1(3)
    c1.print_val()