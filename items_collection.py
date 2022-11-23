import subprocess, re, os
res=subprocess.Popen('pytest --co',stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

class Data:
    def __init__(self):
        self.module=None
        self.cclass=None
        self.fun=None
        self.txt=None

    def set_txt(self,txt):
        self.txt=txt

class Org:
    def __init__(self,data):
        self.data=data

    def check(self):
        if 'Module' in self.data.txt:
            result=re.search(r'^<Module (.*)>',self.data.txt).group(1)
            self.data.module=result
        if 'Class' in self.data.txt:
            result = re.search(r'.*<Class (.*)>', self.data.txt).group(1)
            self.data.cclass = result

    def act(self):
        self.check()
        try:
            if re.match(r'^  <Function',self.data.txt):
                # temp=re.search(r'.*<Function (.*)\[.*\]>',self.data.txt).group(1)
                temp = re.search(r'.*<Function (.*)\[?.*?>', self.data.txt).group(1)

                with open('test_item.txt','a') as file:
                    file.write(f'{self.data.module.strip()}::{temp}\n')
                # print(f'{self.data.module.strip()}::{temp}')
            if re.match(r'^    <Function',self.data.txt):
                temp = re.search(r'.*<Function (.*)\[?.*?>', self.data.txt).group(1)
                with open('test_item.txt', 'a') as file:
                    file.write(f'{self.data.module}::{self.data.cclass}::{temp}\n')
                # print(f'{self.data.module}::{self.data.cclass}::{temp}')
        except:
            pass
def data_collection():

    data=Data()
    org = Org(data)
    print('Start collecting all test item info and write to test_item.txt....')

    if not os.path.exists('.\\test_item.txt'):
        while True:

            content = res.stdout.readline()
            _text=content.decode()
            data.set_txt(_text)
            org.act()
            if len(content) == 0:
                break

    else:
        print('The test_item.txt exists, so skip to collect test item info.')

    #delete the first test item, because the first item will launch automatically at first test by pytest command
    with open('.\\test_item.txt','r') as file:
        re=file.readlines()
        del re[0]
    with open('.\\test_item.txt','w') as file:
        file.writelines(re)