import re
from enum import Enum
from copy import deepcopy
import random
from collections import defaultdict
import heapq
import math
import csv
import shelve
from os import path

ERULES = ['AOIU:', 'ROR:', 'AOIS:', 'AORB:', 'JSD:']
DRULES = ['AOIU:ASRS:', 'LOI:ROR:', 'ROR:SDL:', 'AOIU:AOIU:', 'ROR:ROR:', 'ROR:SDL:']


class LogType(Enum):
    Equivalent = 1
    Duplicated = 2


def count_file_lines(file_object):
    count = 0
    curr = file_object.tell()
    file_object.seek(0)
    dd = False
    if len(file_object.read(1)) > 0:
        dd = True
    while 1:
        buffer = file_object.read(65536)
        if not buffer:
            break
        count += buffer.count('\n')

    file_object.seek(curr)
    return 1 if ((count == 0) and (dd is True)) else count


# Seeks until line in file so we can start reading lines at it
def file_seek_toline(file_object, line_position):
    file_object.seek(0)
    if line_position == 0:
        return file_object
    count = 0
    byte = 1
    while byte != b"" and (count < line_position):
        byte = file_object.read(1)
        if byte == '\n':
            count = count + 1
    return file_object


# Yeah, yeah. Bad algo design. But I don't want to spend time I don't have here.
def pick_equivalent_project_string(line_string: str):
    begin = -1
    end = -1
    sz = len(line_string)
    for i in range(sz):
        if line_string[i] is ':':
            begin = i
            break

    if begin > 0:
        begin = begin + 1
        for i in range(begin, sz):
            if line_string[i] is '/':
                end = i
                break
        return line_string[begin: end]
    else:
        return ''


def pick_duplicated_project_string(line_string: str):
    begin = -1
    end = -1
    sz = len(line_string)
    for i in range(sz):
        if line_string[i] is ':':
            begin = i
            break

    for i in range(begin + 1, sz):
        if line_string[i] is ':':
            begin = i
            break

    if begin > 0:
        begin = begin + 1
        for i in range(begin, sz):
            if line_string[i] is '/':
                end = i
                break
        return line_string[begin: end]
    else:
        return ''


# Reads one line at time, following generator pattern.
def log_reader(log_path: str, start=0):
    log = None
    assert start >= 0 and len(log_path) > 0
    index = start
    lines = 0

    try:
        log = open(log_path, 'r', encoding='utf-8')
        lines = count_file_lines(log)
    except IOError as error:
        print(f'Could not read log file at {log_path}.'
              f'\nReason: {error.strerror}')
    if log is not None and (lines > 0):
        # jump to start
        if start > 0:
            file_seek_toline(log, start)
        while index < lines:
            yield index, log.readline()
            index = index + 1
        log.close()
    else:
        return


# def read_log(log_file, conf_dict):
#     with open(log_file, 'r') as log:
#         current_line = int(conf_dict['current_line'])
#         log.seek(int(current_line))
#
#         line = log.readline()
#         try:
#             while len(line) > 0:
#                 # logic goes here
#                 mut_path = re.search('[^:]*/\w*', line).group(0)
#                 # TODO: Change WHEN DOING FOR DRULES
#                 if mut_operator in ERULES:
#                     print(mut_operator)
#                 else:
#                     pass
#                 line = log.readline()
#                 current_line = current_line + 1
#         except InterruptedError:
#             print("Exiting!")


def build_indices(root_paths: [str]):
    for root_path in root_paths:
        root_path = path.normpath(root_path)
        assert path.isdir(root_path) is True
        nimrod_equivalent = path.join(root_path, 'nimrod_equivalent.log')
        nimrod_duplicated = path.join(root_path, 'nimrod_duplicated.log')
        assert path.isfile(nimrod_equivalent) is True
        assert path.isfile(nimrod_duplicated) is True
        indices = build_index(nimrod_equivalent)
        build_index(nimrod_duplicated, indices, rules=DRULES, project_picker=pick_duplicated_project_string)
        samples = draw_sample_from_indices(indices)
        persist_meta(indices, samples, 'meta', root_path)
        build_samples_csv(samples, root_path)


def build_indices_csv(root_paths: [str], force=False):
    for root_path in root_paths:
        root_path = path.normpath(root_path)
        assert path.isdir(root_path) is True
        nimrod_equivalent = path.join(root_path, 'nimrod_equivalent.log')
        nimrod_duplicated = path.join(root_path, 'nimrod_duplicated.log')
        assert path.isfile(nimrod_equivalent) is True
        assert path.isfile(nimrod_duplicated) is True
        save_p = path.join(root_path,'meta.csv')
        if path.isfile(save_p) and not force:
            return
        build_index_csv(nimrod_equivalent,save_path=save_p)
        build_index_csv(nimrod_duplicated,save_path=save_p, rules=DRULES,
                        project_picker=pick_duplicated_project_string)


def build_index(log_path, indices_dict=None, rules=None, project_picker=pick_equivalent_project_string):
    """
    Takes a path to a nimrod_equivalent or nimrod_duplicated and returns a dictionary containing
    project as keys, and, for each rule processed, corresponding indexes of the rule occurrence on
    the log file
    Ex: project.full.qualified.name : {aois:[0,1,2], ror:[3,45]}
    """
    if rules is None:
        rules = ERULES
    if indices_dict is None:
        indices_dict = defaultdict(lambda: defaultdict(list))
    for index, log_line in log_reader(log_path):
        mut_operator = re.search(r'(^)\w+:(\w+:)?', log_line).group(0)
        if mut_operator in rules:
            project_string = project_picker(log_line)
            heapq.heappush(indices_dict[project_string][mut_operator[0:-1]], index)
    return indices_dict


def build_index_csv(log_path, save_path: str, rules=None, project_picker=pick_equivalent_project_string):
    """
    Takes a path to a nimrod_equivalent or nimrod_duplicated and returns a dictionary containing
    project as keys, and, for each rule processed, corresponding indexes of the rule occurrence on
    the log file
    project, kind, mutation_op, index, path
    """
    if rules is None:
        rules = ERULES
    mode = 'w'
    if path.isfile(save_path):
        mode = 'a'
    with open(save_path, mode, newline='\n') as save_csv:
        writer = csv.writer(save_csv)
        for index, log_line in log_reader(log_path):
            mut_operator = re.search(r'(^)\w+:(\w+:)?', log_line).group(0)
            if mut_operator in rules:
                project_string = project_picker(log_line)
                file_path = re.search(r'[^:]*/\w*', log_line).group(0)
                writer.writerow([project_string,mut_operator[0:-1],index,file_path])


def popfn(size: int):
    if size < 100:
        if size <= 10:
            return size
        else:
            return 10
    else:
        return int(math.ceil(0.1 * size))


# Takes a indices dict and draw 10% or arbitrary number per rule
def draw_sample_from_indices(indices_dict: dict):
    samples_dict = defaultdict(lambda: defaultdict(list)).fromkeys(indices_dict.keys())
    for key in indices_dict.keys():
        samples_dict[key] = deepcopy(indices_dict[key])
    for key, value in samples_dict.items():
        indices_dict = value
        for operator, ilist in indices_dict.items():
            samples_dict[key][operator] = random.sample(ilist, popfn(len(ilist)))
    return samples_dict


# project, kind, mutation_op, index
def build_samples_csv(sample_dict: dict, root_path: str):
    with open(path.join(root_path, 'sample.csv'), 'w', newline='\n') as csvfile:
        writer = csv.writer(csvfile)
        for key, value in sample_dict.items():
            rows = []
            for operator, indices in value.items():
                kind = 'equivalent'
                if ':' in operator:
                    kind = 'duplicated'
                for index in indices:
                    rows.append([key, kind, operator, index])
            writer.writerows(rows)



def persist_meta(data_dict: dict, samples_dict: dict, save_name: str, root_path: str):
    for key, value in data_dict.items():
        rpath = path.join(root_path, key)
        rpath = path.join(rpath, save_name)
        with shelve.open(rpath, 'c') as db:
            db['indices'] = value
            db['samples'] = samples_dict[key]


