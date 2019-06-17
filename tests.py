from core.utils import count_file_lines
from core.utils import file_seek_toline
from core.utils import pick_equivalent_project_string
from core.utils import pick_duplicated_project_string
from core.utils import draw_sample_from_indices
from core.utils import build_index
from core.utils import build_indices_csv
from core.utils import build_indices
from core.utils import DRULES
from os import path
from random import randint


def test_count_file_lines():
    print('\n>test_count_file_lines ->')
    with open('res/a.test', 'r') as testf:
        result = count_file_lines(testf)
        success = result == 9
        if success:
            print('SUCCESS')
        else:
            print(f'FAIL: expected 9, got {result}')


def test_zero_count_file_lines():
    print('\n>test_zero_count_file_lines ->')
    with open('res/nothing.test', 'r') as testf:
        result = count_file_lines(testf)
        success = result == 0
        if success:
            print('SUCCESS')
        else:
            print(f'FAIL: expected 0, got {result}')


def test_oneline_count_file_lines():
    print('\n>test_oneline_count_file_lines ->')
    with open('res/oneline.test', 'r') as testf:
        result = count_file_lines(testf)
        success = result == 1
        if success:
            print('SUCCESS')
        else:
            print(f'FAIL: expected 1, got {result}')


def test_file_seek_toline():
    print('\n>test_file_seek_toline ->')
    with open('res/a.test', 'r') as testf:
        expectedv = testf.readlines()
        results = [file_seek_toline(testf, i).readline() for i in range(9)]
        for expected,result in zip(expectedv,results):
            success = expected == result
            if not success:
                print(f'FAIL: expected {expected}, got {result}')
            else:
                print('SUCCESS')


def test_seek_toline_beginning():
    print('\n>test_file_seek_toline ->')
    with open('res/a.test', 'r') as testf:
        expectedv = testf.readlines()
        # Seek to file end.
        testf.seek(0, 2)
        # Seek to first line
        result = file_seek_toline(testf, 0).readline()
        if result == expectedv[0]:
            print('SUCCESS')
        else:
            print(f'FAIL: expected {expectedv[0]}, got {result}')


def test_seek_toline_end():
    print('\n>test_file_seek_toline ->')
    with open('res/a.test', 'r') as testf:
        expectedv = testf.readlines()
        # Seek to last line
        result = file_seek_toline(testf, len(expectedv) - 1).readline()
        if result == expectedv[-1]:
            print('SUCCESS')
        else:
            print(f'FAIL: expected {expectedv[-1]}, got {result}')


def test_seek_toline_somewhere():
    print('\n>test_file_seek_toline ->')
    place = randint(0, 8)
    with open('res/a.test', 'r') as testf:
        expectedv = testf.readlines()
        result = file_seek_toline(testf, place).readline()
        if result == expectedv[place]:
            print('SUCCESS')
        else:
            print(f'FAIL: expected {expectedv[place]}, got {result}')


def test_pick_equivalent_project_string():
    print('\n>test_pick_project_line_equivalent ->')
    with open('res/equivalentline.test', 'r') as equivalent_line:
        line = equivalent_line.readline()
        expected = 'org.apache.tools.ant.AntClassLoader'
        result = pick_equivalent_project_string(line)
        if result == expected:
            print('SUCCESS')
        else:
            print(f'FAIL: expected {expected}, got {result}')


def test_pick_duplicated_project_string():
    print('\ntest_pick_duplicated_project_string ->')
    with open('res/duplicatedline.test', 'r') as duplicatedline:
        line = duplicatedline.readline()
        expected = 'org.apache.tools.ant.AntClassLoader'
        result = pick_duplicated_project_string(line)
        if result == expected:
            print('SUCCESS')
        else:
            print(f'FAIL: expected {expected}, got {result}')


def test_base():
    test_count_file_lines()
    test_zero_count_file_lines()
    test_oneline_count_file_lines()
    test_file_seek_toline()
    test_seek_toline_end()
    test_seek_toline_beginning()
    test_seek_toline_somewhere()
    test_pick_equivalent_project_string()
    test_pick_duplicated_project_string()


def display_indices_built():
    indices = build_index('res/dummy/result_commons-lang/nimrod_equivalent.log')
    samples_dict = draw_sample_from_indices(indices)
    for k, v in indices.items():
        print(f'\n{k}->')
        for op, howmany in v.items():
            samples = samples_dict[k][op]
            print(f'{op}:{len(howmany)}. Samples: {len(samples)} ->\n{samples}')


def test_build_meta():
    build_indices(['res/dummy/result_commons-lang', 'res/dummy/result_joda-time'])

def test_build_csv_meta():
    build_indices_csv(['res/dummy/result_commons-lang', 'res/dummy/result_joda-time'])


def test_build_both():
    indices = build_index(path.normpath('res/dummy/result_commons-lang/nimrod_equivalent.log'))
    build_index(path.normpath('res/dummy/result_commons-lang/nimrod_duplicated.log'), indices_dict=indices, rules=DRULES,
                project_picker=pick_duplicated_project_string)
    print('Finished')

test_build_csv_meta()


