# Jev 分类评测

目的：审计 8 类 task_type 的分类体系，构建测试 Jev Prompt 分类能力的标准评测集。本仓库不跑任何被测模型。

| 目录 | 内容 |
|---|---|
| `prompts/` | Jev Prompt 各版本。V1 已冻结（只读，哈希见 `.sha256`），修改只能新建版本文件 |
| `patches/` | 对 bench 用代码副本 `/root/bench/proxy/engy/gateway/autoroute.py` 的改动（engy-core 仓库未改） |
| `scripts/` | 下载、检查、抽样、划分脚本；所有抽样使用固定随机种子 |
| `raw/` | 下载的原始数据，不入库，用 `scripts/` 重新生成 |

Jev 调用方式：评测脚本复用 autoroute.py 的请求摘要构造和问题组装，直接调用 Jev API，不经过 Engy 网关，不调用被测模型。使用 V1 时必须指定 `prompts/jev_prompt_v1.json`。
