from abc import ABC,abstractmethod

class Data:

    def __init__(self):
        self.data=[]
        self.specific_content = []
        self.search_result=[]
        with open('.\\temp\\hwinfo64log.txt', newline='') as file:
            temp=file.readlines()
            for i in temp:
                self.data.append(i.strip().replace('\\r\\n',''))

    def accept(self,visitor):
        visitor.act(self)
        return self.specific_content, self.search_result

class Type(ABC):
    def __init__(self):
        self.title=None
        self.end_line=[]

    def set_data(self,title, end):
        self.title=title
        self.end_line=end

    def act(self,data):
        pass

class Video(Type):

    def act(self,data):
        all_search_result = []
        content = []
        start=data.data.index(self.title)
        end=data.data.index(self.end_line)
        target_for_content='Video Bus:'

        for i in data.data[start:end]:
            all_search_result.append(i)
            if target_for_content in i:
                content.append(i)

        data.specific_content=content
        data.search_result=all_search_result

class Manage:
    def __init__(self):
        self.data=Data()
        self.function=None

    def set_requirment(self,title,end):
        self.function.set_data(title,end)

    def set_func(self,func):
        self.function=func

    def act(self):
        return self.data.accept(self.function)