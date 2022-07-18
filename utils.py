import shutil, os
import logging
import json
import pandas as pd
from functools import cmp_to_key
import subprocess

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y/%m/%d %H:%M:%S %p"
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)

# logging.info(os.getcwd())  # /Users/happytsing/Projects/configClassify/script

'''
@meta_type: [path, name]
@meta_name：[mutated_config, ctest_result, hadoop_config, maven]
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


def get_all_mutated_config_names():
    mutated_config_path = get_meta("path", "mutated_config")
    mutated_config_names = os.listdir(mutated_config_path)
    # 删除core-default.xml
    mutated_config_names.remove("core-default.xml")
    # 排序
    mutated_config_names.sort(key=cmp_to_key(cmp))
    return mutated_config_names


def config_replace(mutated_config_name):
    try:
        mutated_config_path = get_meta("path", "mutated_config")
        hadoop_config_path = get_meta("path", "hadoop_config")
        hadoop_config_name = get_meta("name", "hadoop_config")
        shutil.copy("{}/{}".format(mutated_config_path, mutated_config_name),
                    "{}/{}".format(hadoop_config_path, hadoop_config_name))
        return True
    except Exception as e:
        logging.error(e)
        raise


def get_ctest_result_name(mutated_config_name):
    mutated_config_name_list = mutated_config_name.split(".")
    ctest_result_name = "test_result_" + mutated_config_name_list[0] + ".tsv"
    return ctest_result_name


def get_false_ctest(mutated_config_name):
    try:
        ctest_result_path = get_meta("path", "ctest_result")
        ctest_result_name = get_ctest_result_name(mutated_config_name)
        ctest_result_fullpath = "{}/{}".format(ctest_result_path, ctest_result_name)
        tsv = pd.read_csv(ctest_result_fullpath, delimiter='\t', names=["class_path", "bool", "time"], header=None,
                          usecols=["class_path", "bool"])
        tsv_false = tsv.query("bool == 'f'")
        # tsv_false =tsv[tsv["bool"]=="f"]  # 这个方法也可以，但感觉阅读起来不直接
        return tsv_false
    except Exception as e:
        logging.error("Get ctest_result Failed：{}".format(ctest_result_name))
        raise


# @useCache：已经跑过的是否需要重新跑一次
def do_mvn_tests(mutated_config_name, tsv_false, useCache: bool = False):
    maven_path = get_meta("path", "maven")
    mutated_config_name_no_suffix = mutated_config_name.split(".")[0]  # 去文件后缀.xml
    # 避免重复创建结果文件夹
    if not os.path.exists("result"):
        os.system("mkdir result")
    if not os.path.exists("result/mvn_test_{}".format(mutated_config_name_no_suffix)):
        os.system("mkdir result/mvn_test_{}".format(mutated_config_name_no_suffix))
    for _index, row in tsv_false.iterrows():
        class_path = row["class_path"]
        if useCache and os.path.exists("result/mvn_test_{}/{}.log".format(mutated_config_name_no_suffix, class_path)):
            logging.info("mvn_test_{}/{}.log Hit the cache！".format(mutated_config_name_no_suffix, class_path))
            continue
        with open("result/mvn_test_{}/{}.log".format(mutated_config_name_no_suffix, class_path), 'w') as f:
            # 执行命令并覆盖写入文件中
            subprocess.run("mvn test -Dtest={}".format(class_path), shell=True, cwd=maven_path, stdout=f)
