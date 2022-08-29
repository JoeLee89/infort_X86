import os
from pprint import pprint
import subprocess
from abc import ABC, abstractmethod
class BiosData:
    def __init__(self):
        self.data=[]
        self.title_name=None
        self.target_name=None
        self.list=[]


    def extract(self):
        pass

    def set_title_name(self,name):
        self.title_name=name

    def set_target_name(self,name):
        self.target_name=name

    def update(self,visitor):
        # re=self.search(self.name)

        visitor.action(self)


    def search(self):
        with open('.\\tool\\AMISCE\\nvram.txt') as f:
            self.data=f.readlines()
            # print(self.data)
        re=0
        for i in self.data:
            if self.title_name in i:
                re=self.data.index(i)
                break

        for i in self.data[re:]:
            if i != '\n':
                self.list.append(i)
            else:
                break

        return self.data[:6]+self.list

class Method(ABC):
    def __init__(self):
        self.data=None
        self.start_location=None
        self.target_location=None

    @abstractmethod
    def action(self,data):
        pass

    def search_title(self):
        for i in self.data:
            if 'Value	=' in i:
                re=self.data.index(i)
                return re
            if 'Options	=' in i:
                re=self.data.index(i)
                return re
        return False

    def search_target(self,name):
        for i in self.data[self.start_location:]:
            if name in i:
                re=self.data.index(i)
                return re
        return False

    def wtire_file(self):
        print('Start writing the searched result to temp.txt for further usage.')
        with open('temp.txt','w') as f:
            for i in self.data:
                f.write(i)

    def save_to_bios(self):
        process=subprocess.Popen('.\\tool\\AMISCE\\SCEWIN_64.exe /i /s .\\temp.txt', shell=True, stdout=subprocess.PIPE)
        # process=subprocess.Popen('', stdout=subprocess.PIPE)
        process.stdout.read()
        # print('aa=',re)
        # for i in iter(process.stdout.readline,''):
        #     print(i.decode('utf-8'))
        #     if not i:
        #         break




class ChangeItems(Method):
    def __init__(self):
        super().__init__()

    def action(self,datanode):
        self.data=datanode.search()
        self.start_location = self.search_title()
        self.target_location= self.search_target(datanode.target_name)
        # clear the string * first
        for i in range(self.start_location,len(self.data)):
            self.data[i]=self.data[i].replace('*','')
        # add the * to the target line in data list
        index=self.data[self.target_location].find('[')
        self.data[self.target_location]=self.data[self.target_location][:index]+'*'+self.data[self.target_location][index:]
        pprint(self.data)
        self.wtire_file()
        self.save_to_bios()



class ChangeValue(Method):
    def __init__(self):
        super().__init__()

    def action(self, datanode):
        self.data = datanode.search()
        self.start_location = self.search_title()
        #find both = and // string position
        index01 = self.data[self.start_location].find('=')
        index02 = self.data[self.start_location].find('//')
        # replace the original value to expected value based on the index01/02 position
        self.data[self.start_location] = self.data[self.start_location][:index01+1]+ datanode.target_name+self.data[self.start_location][index02:]
        pprint(self.data)
        self.wtire_file()
        self.save_to_bios()


class Manager:
    def __init__(self):
        self.data=BiosData()

    def set_bios_title_item(self,name):
        self.data.set_title_name(name)

    def set_bios_target_item(self,name):
        self.data.set_target_name(name)

    def do_update(self,act):
        self.data.update(act)

        # act.action(self.data)


class Action:
    def __init__(self):
        self.title=''
        self.target=''
        self.type=''

    def set_item(self,title,target,type):
        self.title=title
        self.target=target
        self.type=type

    def action(self):
        lan=Manager()
        lan.set_bios_title_item(self.title)
        lan.set_bios_target_item(self.target)
        item_change=ChangeItems()
        value_change=ChangeValue()
        if self.type == 'item':
            lan.do_update(item_change)
        else:
            lan.do_update(value_change)


# act=Action()
# act.set_item('Quiet Boot', '0','value')
# act.action()

# act=Action()
# act.set_item('Energy Efficient Turbo', 'Disabled','item')
# act.action()
