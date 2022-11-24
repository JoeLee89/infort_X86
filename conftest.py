import pytest,items_collection,os,subprocess,re

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
    now_test_case=os.getenv('PYTEST_CURRENT_TEST')
    now_test_case=re.search(r'(.*) \(.*\)',now_test_case).group(1)
    # 'test_lan.py::test_current (setup)'
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
    items_collection.data_collection()

    yield None
    compare_result = comparison()
    with open('.\\test_item.txt','r') as file:
        re=file.readlines()

    if len(re) >0 and compare_result:
        items=re[0].replace('\n','')
        del re[0]
        with open('.\\test_item.txt', 'w') as file:
            file.writelines(re)
        print('\ntest item=', items)
        # pytest.main(['-vs', items, '--alluredir=.\\report'])
        subprocess.Popen(f'pytest -vs {items} --alluredir=.\\report')

    else:
        os.unlink('.\\count.txt')
        os.unlink('.\\test_item.txt')
        os.unlink('.\\test_item_original.txt')

        # pytest.exit('All test items are finished, so exit the test.')


