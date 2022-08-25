import logging
import os
from utils import config_replace, get_false_ctest, do_mvn_tests, get_ordered_all_mutated_config_names, \
    get_ordered_result_dirs, calc_single_file, get_meta
from tqdm import tqdm

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y/%m/%d %H:%M:%S %p"
logging.basicConfig(level=logging.DEBUG,
                    format=LOG_FORMAT, datefmt=DATE_FORMAT)


# logging.info(os.getcwd())  # /Users/happytsing/Projects/configClassify/script


def mvn_retest():
    mutated_config_names = get_ordered_all_mutated_config_names()
    with tqdm(total=len(mutated_config_names)) as pbar:
        pbar.set_description("mvn testing")
        for mutated_config_name in mutated_config_names:
            try:
                # 1. 替换配置
                config_replace(mutated_config_name)

                # 2. 分析变异配置的测试结果
                tsv_false = get_false_ctest(mutated_config_name)
                counts = tsv_false.shape[0]
                if counts > 30:
                    logging.error("{} 错误f的条目总数为：{},大于30，跳过".format(
                        mutated_config_name, counts))
                    continue
                # 3. 为每个错误的测试执行mvn，并写入文件中
                do_mvn_tests(mutated_config_name, tsv_false, useCache=True)
                pbar.update(1)
            except Exception as e:
                continue


def calc_flaky_percent():
    result_dir_names = get_ordered_result_dirs()
    result_path = get_meta("path", "result")
    calc_merge = {
        "run": 0,
        "Failures": 0,
        "Errors": 0,
        "Skipped": 0
    }
    for dir_name in result_dir_names:
        logging.info("当前计算的目录名：{}".format(dir_name))
        logging.info(
            "=============================================================")
        dir_files = os.listdir("{}/{}".format(result_path, dir_name))
        for mvn_test_log in dir_files:
            logging.info("当前计算的文件名：{}".format(mvn_test_log))
            dir_path = "{}/{}".format(result_path, dir_name)
            try:
                result = calc_single_file(dir_path, mvn_test_log)
            except Exception as e:
                logging.error("获取失败不纳入计算范围")
                continue
            for k, v in result.items():
                calc_merge[k] += v
        logging.info(
            "=============================================================")
    logging.info("汇总计算结果为:{}".format(calc_merge))
    flack_percent = (
        (calc_merge["Errors"]+calc_merge["Failures"])/calc_merge["run"])*100
    logging.info("正确率 = (Failures + Errors)/run = {}%".format(flack_percent))
    return 0


# def yarn_run_ctest_result_analysis():


mvn_retest()


# calc_flaky_percent()
