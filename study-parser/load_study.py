"""Tries to load study designs"""


# load_study.py
import json
import pprint

from studysim.parsers import Configuration, Study, Scenario

def load_json(filepath):
    with open(filepath, "r") as f:
        dict = json.load(f)
    return dict

class Runner:
    def __init__(self, filepath_configuration = "./configuration.json"):
        self.configuration = Configuration(load_json(filepath_configuration))

        if self.configuration.version == 1:
            self.studies = []
            for dict_study in self.configuration.studies:
                self.studies.append(
                    {
                        "name": dict_study['name'],
                        "study": Study(
                            load_json(dict_study['design'])
                            )
                    }
                )
            
            self.tests = []
            for dict_test in self.configuration.tests:
                self.tests.append(
                    {
                        "name": dict_test['name'],
                        "study": dict_test['study'],
                        "scenario": Scenario(
                            load_json(dict_test['scenario'])
                        )
                    }
                )
            
            self.result_basepath = self.configuration.result_basepath
        else:
            raise ValueError("Unsupported Version: {}".format(self.configuration.version))
            
    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, str(self.__dict__))


if __name__ == "__main__":
    runner = Runner()
    print(runner)