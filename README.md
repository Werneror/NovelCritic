# NovelCritic

一个基于 DeepSeek 的小说评论家。分析输入的短篇小说，输出分析结果。


## 用法

在当前目录中创建一个名为 `novels` 的目录。
将要分析的小说以纯文本文件格式（`.txt`）保存到这个目录中。要求：

1. 第一行必须是小说标题
2. 请删除作者和小章节标题，目前暂不支持
3. 字数不超过模型上下文长度限制，按经验，建议不超过 3 万字

考虑你想要投稿的杂志。不同杂志接收不同风格、类型的稿件，对稿件有不同要求，指定杂志有助于做出更有针对性的分析。

接着执行下面的命令，进行小说分析：

```shell
# 假设要分析的小说保存到了文本文件 novels/some_novel.txt 中
# 假设想要投稿的杂志是《科幻世界》
pip3 install -r requirement.txt
export BASE_URL="https://api.deepseek.com"
export API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
pytyon3 main.py novels/some_novel.txt -m 科幻世界
```

分析结果将默认输出到目录 `reports` 中，也可通过 `-o` 或 `--output` 指定其他目录。


## 特别注意

大语言模型可能存在幻觉，请仔细甄别输出结果。


## TODO

- [ ] 实现更多的类型的小说分析
