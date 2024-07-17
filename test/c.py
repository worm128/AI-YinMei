class OuterClass:

    def __init__(self, outer_value):

        self.outer_value = outer_value


    class InnerClass:

        def __init__(self, outer_instance, inner_value):

            self.outer_instance = outer_instance

            self.inner_value = inner_value


        def display_values(self):

            # 正确地访问外部类的实例变量

            print("Outer value:", self.outer_instance.outer_value)

            print("Inner value:", self.inner_value)


# 创建外部类的实例

outer_instance = OuterClass("Hello from Outer")


# 使用外部类的实例创建内部类的实例

inner_instance = OuterClass.InnerClass(outer_instance, "Hello from Inner")


# 调用内部类的方法

inner_instance.display_values()