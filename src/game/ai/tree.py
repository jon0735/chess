
class Node:
    def __init__(self, value=None, content=None, parent=None, children=None):
        self.value = value
        if content is None:
            self.content = {}
        else:
            self.content = content
        self.parent = parent
        if children is None:
            self.children = []
        else:
            self.children = children

    