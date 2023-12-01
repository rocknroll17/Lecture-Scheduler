class Candidate:
    #꼭 들으면 좋음
    def __init__(self):
        self.data = []
    
    def add(self, group):
        self.data.append(group)

    def delete(self, index):
        del self.data[index]

    def remove(self, group):
        self.data.remove(group)

class Basket:
    #장바구니
    def __init__(self):
        self.data = []

    def add(self, lecture):
        self.data.append(lecture)

    def delete(self, index):
        del self.data[index]

    def remove(self, lecture):
        self.data.remove(lecture)