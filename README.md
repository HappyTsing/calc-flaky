# 1. Install

默认情况下需要保证项目结构如下，可以通过`meta.json`修改文件相对路径：
```
tree -L 1
.
├── hadoop-rel-release-3.3.2
├── run_ctest
└── calc_flaky
```

```
# 编译Hadoop项目
cd hadoop-rel-release-3.3.2/hadoop-common-project/hadoop-common/
mvn install -DskipTests
```

```
# 安装依赖
cd calc_flaky
pipenv install
```

# 2. Description

2.1 配置替换

把`run_ctest/sample-hadoop-common-new/mutated_file_hadoop-common-new_1.xml`，复制到`hadoop-rel-release-3.3.2/hadoop-common-project/hadoop-common/target/classes/core-default.xml`中。

2.2 单元测试

使用pandas处理`run_ctest/run_ctest-result/hadoop-common-new/test_result_mutated_file_hadoop-common-new_1.tsv`，获取 f 的测试结果，并对每一个结果执行：

```
mvn test -Dtest=org.apache.hadoop.xxx#xxx
```
将`mvn test`的结果存储在`/result`目录下。

2.3 统计误报率

读取`/result`目录下的执行结果，做统计分析。