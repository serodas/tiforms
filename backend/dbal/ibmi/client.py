class FakeClient:
    def __init__(self, wrapper):
        # Django espera un cliente, aunque no haga nada
        self.wrapper = wrapper