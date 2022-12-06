import subprocess, re, os, sys


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
    # collect how many test items are commanded from user, start collecting all the command line
    argv = sys.argv
    result = []
    command = ''
    for i in argv:
        if '.py' in i:
            result.append(i)

    for i in result:
        command = command + ' ' + i
    res = subprocess.Popen(f'pytest --co {command}', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # ==================================================================================
    # start organizing all need test items and save to test_item.txt for further usage
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


        # delete the first test item, because the first item will launch automatically at first test by pytest command
        with open('.\\test_item.txt', 'r') as file:
            re = file.readlines()

        with open('.\\test_item_original.txt', 'w') as file:
            file.writelines(re)

        with open('.\\test_item.txt', 'w') as file:
            del re[0]
            file.writelines(re)

    else:
        print('The test_item.txt exists, so skip to collect test item info.')

# if __name__ == '__main__':
#     data_collection()