from datetime import time
from .services import StudyTypeService
from .models import StudyType, Conditionality

import abc

class ProgramletParameters:
    def __init__(self, 
                 name: str,
                 study_type_service: StudyTypeService,
                 conditionality: Conditionality):
        self.name = name
        self.study_type_service = study_type_service
        self.conditionality = conditionality

class Programlet(metaclass=abc.ABCMeta):
    def __init__(self, params: ProgramletParameters):
        self.parameters = params
        self.name = self.parameters.name
        self.study_type_service = self.parameters.study_type_service
        self.conditionality = self.parameters.conditionality
        self.conditionality_parameters = self.study_type_service.get_conditionality_parameters(self.conditionality)
        self.check_parameters()
    
    @abc.abstractmethod
    def prepare(self):
        """prepare running. run() tries this once a second until this returns true (timeout=100s).
        """
        pass
    
    @abc.abstractmethod
    def main_logic(self):
        """do main logic of the programlet.
        This is declared, but not implemented. should be implemented in subclasses.
        Returns:
            bool: whatever the logic is, returns if it succeeded or not
        """     
        raise NotImplementedError
    
    @abc.abstractmethod
    def check_parameters(self):
        """do parameter checking. if no parameter is necessary, just "pass".
        This is declared, but not implemented. should be implemented in subclasses.
        """
        raise NotImplementedError

    def filter_parameter(self, parameter_fullname):
        returnlist = []
        for item in self.conditionality_parameters:
            if item.parameter_fullname == parameter_fullname:
                returnlist.append(item)
        return returnlist
    
    def pick_value(self, parameter_object):
        # from pydoc import locate
        
        # typed = locate(parameter_object.value_type)
        # return typed(parameter_object.value)
        
        
        # this needs to be changed to formal type casting
        try:
            v = float(parameter_object.value)
            if v == int(v):
                return int(v)
            else:
                return v
        except:
            return parameter_object.value
            
    def run(self):
        max_trial = 100
        prepared = False
        for i in range(max_trial):
            if self.prepare():
                prepared = True
                break
            else:
                pass
        if prepared:
            return self.main_logic()            
        else:
            return False
        
### Don't touch above! ###

class Programlet_Test_Test(Programlet):
    def check_parameters(self):            
        self.threshold = self.pick_value(self.filter_parameter("nlm.test.test_conditionality.ramdom.threshold")[0])
        self.test_str = self.pick_value(self.filter_parameter("nlm.test.test_conditionality.ramdom.test_str")[0])

    def prepare(self):
        return True
            
    def main_logic(self):
        import random
        import json
        from nlm.services import LogService
        
        random_value = random.random()
        
        logger = LogService(subject_name=self.name)
        logger.log(value=json.dumps({
            "name": "random value", 
            "value": (random_value > self.threshold),
            "support_evidences": {
                "random_value": random_value,
                "threshold": self.threshold
                }
            }), purpose="test purpose", object="test object")