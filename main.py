import argparse
import os
import sys
from datetime import datetime
from openai import OpenAI

client = OpenAI(api_key=os.getenv("API_KEY"), base_url=os.getenv("BASE_URL"))


class Novel:

    def __init__(self, novel_path, output_dir):
        self.novel_path = novel_path
        self.output_dir = output_dir
        self.text = str()
        self.title = list()
        self.critical = str()

    def read(self):
        print("正在读取小说内容...")
        lines = list()
        with open(self.novel_path) as f:
            for line in f:
                line = line.strip()
                if line != "":
                    lines.append(line)
        title = lines[0].replace("《", "").replace("》", "")
        text = lines[1:]
        print(f"小说标题为：{title}")
        print(f"小说正文共有 {len(text)} 个自然段")
        print(f"小说正文约有 {len(''.join(text))} 字")
        self.title = title
        self.text = text

    def get_title(self):
        return self.title

    def get_text(self):
        return "\n\n".join(self.text)

    def get_text_with_title(self):
        return f"《{self.get_title()}》\n\n{self.get_title()}"

    def get_text_with_no(self):
        text_with_no = list()
        for i, p in enumerate(self.text):
            p = f"【{i + 1}】{p}"
            text_with_no.append(p)
        return "\n\n".join(self.text)

    def analysis(self):
        self.critical_analysis()

    def critical_analysis(self):
        print("正在进行最严重问题分析...")
        response = client.chat.completions.create(
            model="deepseek-chat",
            temperature=0.5,
            messages=[
                {"role": "system", "content": "你是《科幻世界》杂志的资深编辑，对投稿有着严苛的要求。"
                                              "请先仔细阅读用户投稿的科幻小说，然后向用户一针见血地指出，小说存在的最严重问题。"
                                              "不用强调自己的身份，请仅指出存在的问题。"},
                {"role": "user", "content": self.get_text_with_title()},
            ],
            stream=False
        )
        self.critical = response.choices[0].message.content
        print(self.critical)

    def save(self):
        report_filename = f"小说《{self.get_title()}》分析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path = os.path.join(self.output_dir, report_filename)
        report = f"""
# 小说《{self.get_title()}》分析报告

本文是小说《{self.get_title()}》的分析报告，由大语言模型于 {datetime.now().strftime('%Y 年 %m 月 %d 日 %H 时 %M 分 %S 秒')}生成。

## 小说概括

- 字数：越 {len(self.get_text())}
- 自然段：共 {len(self.text)} 个

## 最严重问题

{self.critical}

"""
        with open(report_path, "w") as f:
            f.write(report)


def main():
    # 设置命令行参数解析器
    parser = argparse.ArgumentParser(
        description='小说批改工具 - 输入小说文件进行批改分析',
        formatter_class=argparse.RawTextHelpFormatter
    )

    # 添加必需的文件名参数
    parser.add_argument(
        'filename',
        type=str,
        help='''输入要分析的小说文件名，仅支持纯文本文件'''
    )

    # 添加可选输出参数
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='reports',
        help='指定输出目录 (默认: reports)'
    )

    # 解析命令行参数
    args = parser.parse_args()

    # 验证文件是否存在
    if not os.path.exists(args.filename):
        sys.exit(f"错误: 指定的文件 '{args.filename}' 不存在，请检查路径")

    # 验证文件扩展名
    valid_extensions = ['.txt']
    if not any(args.filename.endswith(ext) for ext in valid_extensions):
        ext_list = ", ".join(valid_extensions)
        sys.exit(f"错误: 不支持的扩展名。请使用以下格式: {ext_list}")

    # 验证输出目录，如果有必要，创建输出目录
    if os.path.exists(args.output):
        if not os.path.isdir(args.output):
            sys.exit(f"错误: 指定的输出目录 '{args.output}' 已存在但不是目录，请检查")
    else:
        os.mkdir(args.output)

    # 打印确认信息
    print(f"准备分析小说: {args.filename}")
    print(f"内容将输出至: {args.output}")

    # 分析小说
    novel = Novel(args.filename, args.output)
    novel.read()
    novel.analysis()
    novel.save()


if __name__ == "__main__":
    main()
