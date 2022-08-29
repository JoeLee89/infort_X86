import pytest
def pytest_addoption(parser):
    parser.addoption('--item',action='store',default=None,help='input the function name you need to test, or input all for all items')

def pytest_generate_tests(metafunc):
    # print('all=',metafunc.fixturenames)

    option_value=metafunc.config.option.item
    # print('value=',option_value)
    if 'item' in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize('item',[option_value])

