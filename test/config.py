import yaml

# 加载配置
f = open('config-prod.yml','r',encoding='utf-8')
cont = f.read()
config = yaml.load(cont,Loader=yaml.FullLoader)

fastgpt_authorization = config["llm"]["fastgpt_authorization"]
print(fastgpt_authorization.get("怒怼版"))