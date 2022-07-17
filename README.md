# 零、准备

```
# 编译项目
cd hadoop-rel-release-3.3.2/hadoop-common-project/hadoop-common/
mvn install -DskipTests
```

# 一、配置替换

把`run_ctest/sample-hadoop-common-new`中的`mutated_file_hadoop-common-new_1.xml`，复制到`hadoop-rel-release-3.3.2/hadoop-common-project/hadoop-common/target/classes/core-default.xml`中。

# 二、单元测试

找到`run_ctest/run_ctest-result/hadoop-common-new/test_result_mutated_file_hadoop-common-new_1.tsv`，然后依次遍历每一行，找到其中第二列为 f 的，然后获取第一列的数据，执行：

```
mvn test -Dtest=org.apache.hadoop.xxx#xxx
```

获取测试结果
