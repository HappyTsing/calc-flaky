from cgi import print_arguments
from email.policy import default
import json
import logging
import os
import subprocess
import shutil
from webbrowser import get
import pandas as pd
from functools import cmp_to_key
import re

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y/%m/%d %H:%M:%S %p"
logging.basicConfig(level=logging.DEBUG,
                    format=LOG_FORMAT, datefmt=DATE_FORMAT)

# logging.info(os.getcwd())  # /Users/happytsing/Projects/configClassify/script

'''
@meta_type: [path, name]
@meta_name：[mutated_config, ctest_result, default_config, maven, result]
'''


def get_meta(meta_type: str, meta_name: str) -> str:
    with open("meta.json", 'r') as f:
        meta = json.load(f)
        data = meta[meta_type][meta_name]
    return data


def cmp(a, b):
    la = a.split("_")
    lb = b.split("_")
    num_a = int(la[len(la) - 1].split(".")[0])
    num_b = int(lb[len(lb) - 1].split(".")[0])

    if num_a < num_b:
        return -1
    if num_a > num_b:
        return 1
    return 0


def get_ordered_all_mutated_config_names():
    mutated_config_path = get_meta("path", "mutated_config")
    mutated_config_names = os.listdir(mutated_config_path)
    default_config_name = get_meta("name", "default_config")
    # 删除core-default.xml
    if default_config_name in mutated_config_names:
        mutated_config_names.remove(default_config_name)
    # 排序
    mutated_config_names.sort(key=cmp_to_key(cmp))
    return mutated_config_names


def config_replace(mutated_config_name):
    try:
        mutated_config_path = get_meta("path", "mutated_config")
        default_config_path = get_meta("path", "default_config")
        default_config_name = get_meta("name", "default_config")
        shutil.copy("{}/{}".format(mutated_config_path, mutated_config_name),
                    "{}/{}".format(default_config_path, default_config_name))
        return True
    except Exception as e:
        logging.error(e)
        raise


def get_ctest_result_name(mutated_config_name):  # 根据 变异的配置名，获取 该变异的ctest结果文件名
    mutated_config_name_list = mutated_config_name.split(".xml")
    ctest_result_name = "test_result_" + mutated_config_name_list[0] + ".tsv"
    return ctest_result_name


def get_false_ctest(mutated_config_name):  # 获取所有f的测试结果
    try:
        ctest_result_path = get_meta("path", "ctest_result")
        ctest_result_name = get_ctest_result_name(mutated_config_name)
        ctest_result_fullpath = "{}/{}".format(
            ctest_result_path, ctest_result_name)
        tsv = pd.read_csv(ctest_result_fullpath, delimiter='\t', names=["class_path", "bool", "time"], header=None,
                          usecols=["class_path", "bool"])
        tsv_false = tsv.query("bool == 'f'")
        # tsv_false =tsv[tsv["bool"]=="f"]  # 这个方法也可以，但感觉阅读起来不直接
        return tsv_false
    except Exception as e:
        logging.error("Get ctest_result Failed：{}".format(ctest_result_name))
        raise


# @useCache：是否使用缓存
def do_mvn_tests(mutated_config_name, tsv_false, useCache: bool = False):
    maven_path = get_meta("path", "maven")
    mutated_config_name_no_suffix = mutated_config_name.split(".xml")[
        0]  # 去文件后缀.xml
    result_path = get_meta("path", "result")
    # 避免重复创建结果文件夹
    if not os.path.exists(result_path):
        os.system("mkdir -p {}".format(result_path))
    if not os.path.exists("{}/mvn_test_{}".format(result_path, mutated_config_name_no_suffix)):
        os.system("mkdir -p {}/mvn_test_{}".format(result_path,
                  mutated_config_name_no_suffix))
    for _index, row in tsv_false.iterrows():
        class_path = row["class_path"]
        if useCache and os.path.exists(
                "{}/mvn_test_{}/{}.log".format(result_path, mutated_config_name_no_suffix, class_path)):
            logging.info(
                "mvn_test_{}/{}.log Hit the cache！".format(mutated_config_name_no_suffix, class_path))
            continue
        with open("{}/mvn_test_{}/{}.log".format(result_path, mutated_config_name_no_suffix, class_path), 'w') as f:
            # 执行命令并覆盖写入文件中
            subprocess.run("mvn test -Dtest={}".format(class_path),
                           shell=True, cwd=maven_path, stdout=f)


'''utils for calc_flaky_percent '''


def get_ordered_result_dirs():
    result_path = get_meta("path", "result")
    if not os.path.exists(result_path):
        os.system("mkdir -p {}".format(result_path))
    dir_names = os.listdir(result_path)
    dir_names.sort(key=cmp_to_key(cmp))
    return dir_names


def calc_single_file(dir_path, mvn_test_file_log):
    try:
        with open("{}/{}".format(dir_path, mvn_test_file_log), 'r') as f:
            mvn_test_log = f.read()
            regex = r"Tests run: \d, Failures: \d, Errors: \d, Skipped: \d"
            mvn_test_result = re.search(regex, mvn_test_log).group()
            mvn_test_result_map = {
                "run": int(mvn_test_result[11]),
                "Failures": int(mvn_test_result[24]),
                "Errors": int(mvn_test_result[35]),
                "Skipped": int(mvn_test_result[47]),
            }
        return mvn_test_result_map
    except Exception as e:
        logging.error("获取测试结果失败：{}，原因可能是文件不完整".format(mvn_test_file_log))
        raise
