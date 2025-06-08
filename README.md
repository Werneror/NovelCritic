# NovelCritic

一个基于 DeepSeek 的小说评论家。

## 用法

```shell
# 将要分析的小说保存到文本文件 some_novel.txt 中
pip3 install -r requirement.txt
export BASE_URL="https://api.deepseek.com"
export API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
pytyon3 main.py some_novel.txt
```

分析结果将默认输出到目录 `reports` 中，也可通过 `-o` 或 `--output` 指定其他目录。
