import logging
import os
from utils import config_replace, get_false_ctest, do_mvn_tests, get_all_mutated_config_names, get_result_dirs
from tqdm import tqdm

# from utils import init
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y/%m/%d %H:%M:%S %p"
logging.basicConfig(level=logging.DEBUG,
                    format=LOG_FORMAT, datefmt=DATE_FORMAT)


# logging.info(os.getcwd())  # /Users/happytsing/Projects/configClassify/script


def mvn_retest():
    mutated_config_names = get_all_mutated_config_names()
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
                    logging.error("{} 错误f大于30，跳过".format(mutated_config_name))
                    continue
                # 3. 为每个错误的测试执行mvn，并写入文件中
                do_mvn_tests(mutated_config_name, tsv_false, useCache=True)
                pbar.update(1)
            except Exception as e:
                continue


def calc_flaky_percent():

    dir_names = get_result_dirs()
    with tqdm(total=len(dir_names)) as pbar:
        pbar.set_description("flaky calcing")
        for dir_name in dir_names:
            dir_files = os.listdir("result/{}".format(dir_name))
        pbar.update(1)
    return 0


mvn_retest()
