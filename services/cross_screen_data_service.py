class CrossScreenDataService():
    def __init__(self):
        self.data_center = {}

    def get_data_by_key(self, key: str):
        return self.data_center[key]
    
    def set_data_by_key(self, key: str, value):
        self.data_center[key] = value