import yaml

class configInit:
      def __init__(self,filename,encoding):
          f = open(filename, "r", encoding = encoding)
          cont = f.read()
          self.config = yaml.load(cont, Loader=yaml.FullLoader)

      def get_config(self):
          return self.config
