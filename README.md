# NovelCritic

一个基于 DeepSeek 的小说评论家。分析输入的短篇科幻小说，输出分析结果。

## 用法

在当前目录中创建一个名为 `novels` 的目录。
将要分析的小说以纯文本文件格式（`.txt`）保存到这个目录中。要求：

1. 第一行必须是小说标题
2. 请删除作者和小章节标题，目前暂不支持
3. 字数不超过模型上下文长度限制，按经验，建议不超过 3 万字

接着执行下面的命令，进行小说分析：

```shell
# 假设要分析的小说保存到了文本文件 novels/some_novel.txt 中
pip3 install -r requirement.txt
export BASE_URL="https://api.deepseek.com"
export API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
pytyon3 main.py novels/some_novel.txt
```

分析结果将默认输出到目录 `reports` 中，也可通过 `-o` 或 `--output` 指定其他目录。
