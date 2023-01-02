import pytest,items_collection,os,subprocess,re
from tools_manage import InstallManage


# def pytest_addoption(parser):
#     parser.addoption('--item',action='store',default='all',help='input the function name you need to test, or input all for all items')
#
# def pytest_generate_tests(metafunc):
#     # print('all=',metafunc.fixturenames)
#
#     option_value=metafunc.config.option.item
#     # print('value=',option_value)
#     if 'item' in metafunc.fixturenames and option_value is not None:
#         metafunc.parametrize('item',[option_value])
#


def comparison():
    # get now test case name, and delete no needed strings
    now_test_case=os.getenv('PYTEST_CURRENT_TEST')
    now_test_case=re.search(r'(.*) \(.*\)',now_test_case).group(1)
    # 'test_lan.py::test_current (setup)'

    # each test will count and save the file to count.txt
    # compare list in test_item_original.txt specific number with count number,
    # if the same means test starting from the square, or they test with special test items.
    if not os.path.exists('count.txt'):
        with open('count.txt','w') as file:
            file.write('0')

    with open('count.txt', 'r') as file:
        count=int(file.readline())

    with open('test_item_original.txt','r') as file:
        content_ori=file.readlines()[count].replace('\n','')

    with open('count.txt','w') as file:
        count+=1
        file.write(str(count))

    return content_ori == now_test_case



@pytest.fixture(scope='session',autouse=True)
def final():
    items=None
    if not os.path.exists('temp'):
        os.mkdir('temp')
    if not os.path.exists('tool'):
        os.mkdir('tool')
    # 先裝sleeper tool，之後會一直需要
    result = InstallManage().set_name('sleeper')
    if not result:
        pytest.skip('The installation process is failed, so skip the test.')

    items_collection.data_collection()

    yield None

    # after item test is finished, the following is going to test.
    # compare count number with the file test_item_original.txt list, if they are the same
    # compare_result = comparison()

    # record how many test items remain, if ==0 means all test is finished.
    with open('.\\test_item.txt','r') as file:
        re=file.readlines()

    # if test_item.txt has no test item, and compare_result is FALSE, it means all items are finished.
    # if len(re) >0 and compare_result:
    if len(re) > 0:
        items=re[0].replace('\n','')
        del re[0]
        with open('.\\test_item.txt', 'w') as file:
            file.writelines(re)
        print('\ntest item=', items)
        # pytest.main(['-vs', items, '--alluredir=.\\report'])
        sub=subprocess.Popen(f'pytest -vs {items} --alluredir=.\\report')
        sub.wait()
        sub.kill()

    else:
        # os.unlink('.\\count.txt')
        try:
            startup_bat_path = os.path.expanduser(
                '~') + '\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\run.bat'
            os.unlink('.\\test_item.txt')
            os.unlink('.\\test_item_original.txt')
            os.unlink(startup_bat_path)
            temp_file=os.listdir('.\\temp')
            for i in temp_file:
                print('delete ffile', 'i')
                os.unlink(f'.\\temp\\{i}')
        except Exception as a:
            print('Error occure:', a)

        # pytest.exit('All test items are finished, so exit the test.')


