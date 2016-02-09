from test_model import TestModel

class test_model_script(NebriOS):

    listens_to = ['test_model_script']

    def check(self):
        return self.test_model_script == True

    def action(self):
        self.test_model_script = 'RAN ' + str(datetime.now())




