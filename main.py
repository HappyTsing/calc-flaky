from tqdm import tqdm
from utils import *
from time import sleep
from time import sleep

from tqdm import tqdm

from utils import *

# from utils import init
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y/%m/%d %H:%M:%S %p"
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)


# logging.info(os.getcwd())  # /Users/happytsing/Projects/configClassify/script


def mvn_retest():
    mutated_config_names = get_all_mutated_config_names()
    with tqdm(total=len(mutated_config_names)) as pbar:
        pbar.set_description("Testing")
        for mutated_config_name in mutated_config_names:
            try:
                # 1. 替换配置
                config_replace(mutated_config_name)

                # 2. 分析变异配置的测试结果
                tsv_false = get_false_ctest(mutated_config_name)

                # 3. 为每个错误的测试执行mvn，并写入文件中
                do_mvn_tests(mutated_config_name, tsv_false, useCache=True)
                pbar.update(1)
            except Exception as e:
                continue

def calc_flaky_percent():
    # todo
    return 0

mvn_retest()
