import csv
from datetime import datetime
from enum import Enum
import importlib
import json
import os
from timeit import repeat

import settings


class DataType(Enum):
    COMPLEX = 1
    SIMPLE = 2


class Method(Enum):
    DUMPS = 1
    LOADS = 2


def import_modules(modules):
    """import json libraries for benchmark"""
    for module in modules:
        try:
            yield importlib.import_module(module)
        except ImportError:
            print(f"Unable to import {module}")


def benchmark_dumps(m, data: str, r: int, n: int):
    return min(repeat(lambda: m.dumps(data), repeat=r, number=n))


def benchmark_loads(m, data: str, r: int, n: int):
    return min(repeat(lambda: m.loads(data), repeat=r, number=n))


def get_filename():
    now = datetime.now()
    return settings.OUTPUT_FILE_PREFIX + now.strftime("%Y%m%d%H%M%S") + ".csv"


def export_csv(results):
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    file_path = settings.OUTPUT_DIR + get_filename()
    with open(file_path, "w") as f:
        writer = csv.writer(f)
        # header
        writer.writerow(results[0].keys())
        # body
        writer.writerow(result.values() for result in results)
    return file_path


def run_benchmarks():
    modules = settings.MODULES
    with open(settings.COMPLEX_FILE) as f:
        complex_data = f.read()
    complex_json = json.loads(complex_data)
    with open(settings.SIMPLE_FILE) as f:
        simple_data = f.read()
    simple_json = json.loads(simple_data)
    case = [
        (
            DataType.COMPLEX.name,
            Method.DUMPS.name,
            lambda m: benchmark_dumps(
                m, complex_json, settings.REPEAT, settings.NUMBER
            ),
        ),
        (
            DataType.SIMPLE.name,
            Method.DUMPS.name,
            lambda m: benchmark_dumps(m, simple_json, settings.REPEAT, settings.NUMBER),
        ),
        (
            DataType.COMPLEX.name,
            Method.LOADS.name,
            lambda m: benchmark_loads(
                m, complex_data, settings.REPEAT, settings.NUMBER
            ),
        ),
        (
            DataType.SIMPLE.name,
            Method.LOADS.name,
            lambda m: benchmark_loads(m, simple_data, settings.REPEAT, settings.NUMBER),
        ),
    ]
    results = []

    modules = import_modules(modules)
    for module in modules:
        module_name = module.__name__
        for data_type, methods, fn in case:
            result = {}
            result["module_name"] = module_name
            result["methods"] = methods
            result["data_type"] = data_type
            result["time"] = fn(module)
            results.append(result)
    return results


def main():
    results = run_benchmarks()
    file_path = export_csv(results)
    print(f"DONE! {file_path}")


if __name__ == "__main__":
    main()
