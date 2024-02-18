from PyLive2D import PyLive2D

# 加载 model
model = PyLive2D.Live2DModel("model_file_path/myModel.model.json")

# 取得模型宽高
width, height = model.get_model_width(), model.get_model_height()

# 设置动画表情
model.set_expression("expression_name")

# 模型参数变换
model.set_parameter_value("parameter_name", value)

# 绘制模型
model.draw(x, y)