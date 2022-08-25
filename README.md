# 1. Install

默认情况下需要保证项目结构如下，可以通过`meta.json`修改文件相对路径：

```
tree -L 2
openctest
├── core
│   ├── app/PROJECT
│   └── run_ctest
└── calc_flaky
```

```
# 编译Hadoop项目
cd core/app/PROJECT_PATH
mvn install -DskipTests
```

```
# 安装依赖
cd calc_flaky
pipenv install
```

# 2. Description

2.1 配置替换

循环将`meta['path']['mutated_config']`目录下的所有变异后的配置，复制到`meta['path']['default_config']`目录，并将其重命名为`meta['name']['default_config']`，实现变异配置的替换，此后再基于该替换后配置进行单元测试。

2.2 单元测试

使用 pandas 处理`meta['path']['result_ctest']`目录下的测试结果文件，该文件以`.tsv`结尾，从中获取 f 的测试结果，并对每一个结果执行：

```
mvn test -Dtest=org.apache.hadoop.xxx#xxx
```

将`mvn test`的结果存储在`meta['path']['result']`目录下。

> 新版 openctest 中，tsv 文件中仅显示 f 的测试结果，而不显示 p 的结果，因此无需过滤。

2.3 统计误报率

读取`meta['path']['result']`目录下的执行结果，做统计分析。
