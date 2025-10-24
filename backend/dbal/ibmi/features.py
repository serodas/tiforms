class FakeFeatures:
    def __init__(self, wrapper):
        self.wrapper = wrapper
    # Django puede acceder a atributos mínimos, por ejemplo:
    can_return_id_from_insert = True
    supports_transactions = True
