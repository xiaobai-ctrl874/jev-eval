# Jev Prompt V1

- 冻结日期：2026-09-29
- 内容：线上 Prompt（autoroute.py 的 DEFAULT_PREAMBLE / DEFAULT_QUESTIONS）加上 math 类。与线上相比只有三处不同：task_type 的总说明加了数学优先规则；reasoning 去掉数学；新增 math 的定义。其余逐字相同。
- 文件 `jev_prompt_v1.json` 只包含发给 Jev 的内容（preamble 和三个维度的说明），只读，哈希见 `jev_prompt_v1.sha256`。
- 不再修改；后续改动另建 V2 文件。
