from www.orm import Model


class ResultBean(dict):
    def __init__(self, code, result):
        self.code = code
        self.result = result

    def __getattr__(self, name):
        if name in self:
            return self[name]
        n = ResultBean()
        super().__setitem__(name, n)
        return n

    def __getitem__(self, name):
        if name not in self:
            super().__setitem__(name, ResultBean())
        return super().__getitem__(name)

    def __setattr__(self, name, value):
        super().__setitem__(name, value)
