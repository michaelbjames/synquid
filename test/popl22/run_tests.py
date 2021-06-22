#!/usr/bin/python3

import os
import subprocess
from multiprocessing import Pool, Manager
import sys
import csv
import time
import re

'''
Run all benchmarks, collect results, output csv and tex files

TODO:
record time
record AST size
other stats?
output csv
output tex
write all output to a log
'''

STACK_ARGS = ['--silent']
DEFAULT_ARGS = ['--print-stats']
RUN_SYNQUID = ['stack'] + STACK_ARGS + ['run', '--', 'synquid'] + DEFAULT_ARGS

VARIANTS = {
    'either/or' : ['--intersect=EitherOr']
}

TIMEOUT_SEC = 15

BASE_TEST_PATH = "./test/intersection/intersection/"

STATUS = 'status'
SIZE = 'size'
TIME = 'time'

LOGFILE = 'results.log'
CSVFILE = 'results.csv'
TEXFILE = 'results.tex'

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

SUCCESS_STATUS = bcolors.OKGREEN + 'success' + bcolors.ENDC
TIMEOUT_STATUS = bcolors.WARNING + 'timeout' + bcolors.ENDC
FAILED_STATUS = bcolors.FAIL + 'failed' + bcolors.ENDC


FNULL = open(os.devnull, 'w')

class Benchmark:
    def __init__(self, name, description, components='', options=[]):
        self.name = name
        self.description = description
        self.components = components
        self.options = options
    
    def str(self):
        return f"{self.name}: {self.description} {str(self.options)}"

BENCHMARKS = [
    Benchmark("List-Inc", "increment list"),
    Benchmark("List-Sum", "sum list"),
    Benchmark("All-Neg", "all negative"),
    Benchmark("List-Dict-Contains", "dictionary contains"),
    Benchmark("List-Dict-Find", "dictionary find"),
    Benchmark("List-Even-Parity", "list length even", "not"),
    Benchmark("List-Fold", "foldl"),
    Benchmark("List-Last", "last list element"),
    Benchmark("List-Length", "list length"),
    Benchmark("List-Snoc", "cons at end"),
    Benchmark("List-toFalse", "map const false"),
    Benchmark("TakeWhile", "take while")

]

class Result:
    def __init__ (self, name, status, time, stats, output = ''):
        self.name = name
        self.status = status
        self.time = time
        self.stats = stats
        self.output = output
        self.variant_results = {}

class VariantResult:
    def __init__ (self, status, time, output = ''):
        self.status = status
        self.time = time
        self.output = output


class Stats:
    def __init__ (self, goal_count, code_size, spec_size):
        self.goal_count = goal_count
        self.code_size = code_size
        self.spec_size = spec_size

nostats = Stats('-', '-', '-')

def get_stats(output):
    lines = output.decode('utf-8').splitlines()
    goals = re.match("\(Goals: (\d+)\).*$", lines[-4]).group(1)
    spec_size = re.match("\(Spec size: (\d+)\).*$", lines[-2]).group(1)
    ast_size = re.match("\(Solution size: (\d+)\).*$", lines[-1]).group(1)
    return Stats(goals, ast_size, spec_size)

def run_file(filename, args):
    filepath = filename + '.sq' 
    cmd = " ".join(RUN_SYNQUID + args + [filepath])
    res = None
    try:
        start = time.time()
        completed = subprocess.run(cmd, timeout=TIMEOUT_SEC, check=True, shell=True, capture_output = True)
        end = time.time()
        stats = get_stats(completed.stdout)
        res = Result(filename, SUCCESS_STATUS, end - start, stats, completed.stdout) # TODO: get stats, write output to file
    except subprocess.TimeoutExpired as e:
        res = Result(filename, TIMEOUT_STATUS, -1, nostats, '-')
    except subprocess.CalledProcessError as e:
        res = Result(filename, FAILED_STATUS, -1, nostats, e.stderr) 
    for (vid, vopts) in VARIANTS.items():
        run_variant(filename, args, vid, vopts, res)
    return res

def run_variant(filename, args, variant_id, extra_args, res):
    filepath = filename + '.sq'
    cmd = " ".join(RUN_SYNQUID + args + extra_args + [filepath])
    v = None
    try:
        start = time.time()
        completed = subprocess.run(cmd, timeout=TIMEOUT_SEC, check=True, shell=True, capture_output = True)
        end = time.time()
        v = VariantResult(SUCCESS_STATUS, end - start, completed.stdout)
    except subprocess.TimeoutExpired as e:
        v = VariantResult(TIMEOUT_STATUS, -1, '-')
    except subprocess.CalledProcessError as e:
        v = VariantResult(FAILED_STATUS, -1, e.stderr) 
    res.variant_results[variant_id] = v


def sort_dir(original_dir, status):
    if status == SUCCESS_STATUS:
        if original_dir == SYNTH_DIR:
            return SYNTH_DIR
        else:
            return CHECKS_DIR
    if status == TIMEOUT_STATUS:
        print("timeout")
        return WIP_DIR
    if status == FAILED_STATUS:
        return FAILS_DIR

def is_synquid_file(filename):
    filename[-3:] == ".sq"


def worker(bench, return_dict):
    filename = bench.name
    res = run_file(filename, bench.options)

    if return_dict is not None:
        return_dict[filename] = res

def print_result(name, status, time):
    if time > 0:
        print(f"  {name}: {time:.2}s")
    else:
        print(f"  {name}: {status}")

def print_results(statuses):
    for (filename, res) in statuses:
        print(f"{filename}:")
        print_result("default", res.status, res.time)
        for (v, vres) in res.variant_results.items():
            print_result(v, vres.status, vres.time)

def main():
    worklist = []
    manager = Manager()
    return_dict = manager.dict()

    print("building project...", end="")
    subprocess.run("stack build", shell=True)
    print("done")

    for b in BENCHMARKS:
        worklist.append((b, return_dict))

    print("running testing benchmarks...", end="")
    with Pool() as pool:
        pool.starmap(worker, worklist)
    print("done")

    statuses = sorted(return_dict.items())
    print_results(statuses)
    # TODO: write csv
    # TODO: write latex

if __name__ == '__main__':
    main()