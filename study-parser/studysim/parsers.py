import copy

class BaseParser:
    def __init__(self, dict):
        self.json = dict
    
    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, str(self.__dict__))

class Configuration(BaseParser):
    def __init__(self, dict):
        super().__init__(dict)
        self.__parse()
    
    def __parse(self):
        self.meta = self.json['meta']
        self.version = self.meta['version']
        
        if self.version == 1:
            self._studies = self.json['studies']
            self._tests = self.json['tests']
            self._result_basepath = self.json['result']['basepath']
        else:
            raise ValueError("Unsupported Version: {}".format(self.version))
        
    @property
    def studies(self):
        return copy.deepcopy(self._studies)
    
    @property
    def tests(self):
        return copy.deepcopy(self._tests)
    
    @property
    def result_basepath(self):
        return self._result_basepath
    


class Study(BaseParser):
    def __init__(self, dict):
        super().__init__(dict)
        self.__parse()
    
    def __parse(self):
        self.meta = self.json['meta']
        self.version = self.meta['version']
        
        if self.version == 1:
            pass
        else:
            raise ValueError("Unsupported Version: {}".format(self.version))

class Scenario(BaseParser):
    def __init__(self, dict):
        super().__init__(dict)
        self.__parse()
    
    def __parse(self):
        self.meta = self.json['meta']
        self.version = self.meta['version']
        
        if self.version == 1:
            pass
        else:
            raise ValueError("Unsupported Version: {}".format(self.version))