class Circuits():
    def __init__(self):
        pass

    class AND():
        def __init__(self):
            self.text = "AND"
            self.color = (50,100,150)
            self.pins = [2,1]

        
        def get_data(self):
            return self.text, self.color, self.pins

        def work(self, inp:list):
            return inp[0] and inp[1]

    class NOT():
        def __init__(self):
            self.text = "NOT"
            self.pins = [1,1]
            self.color = (150,22,22)
        
        def get_data(self):
            return self.text, self.color, self.pins

        def work(self, inp:list):
            return not inp[0]