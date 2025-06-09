import argparse
import logging
import os
import sys
from datetime import datetime
from openai import OpenAI


def chat_with_llm(model, temperature, message):
    client = OpenAI(api_key=os.getenv("API_KEY"), base_url=os.getenv("BASE_URL"))
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=message,
        stream=True
    )
    full_content = ""
    logging.info("大语言模型思考中...")
    # 遍历流式响应，实时输出到终端
    for chunk in response:
        if chunk.choices[0].delta.content:
            delta_content = chunk.choices[0].delta.content
            print(delta_content, end='', flush=True)
            full_content += delta_content
    print()
    return full_content


class Novel:

    def __init__(self, novel_path, output_dir, magazine):
        self.novel_path = novel_path
        self.output_dir = output_dir
        self.magazine = magazine
        self.title = str()
        self.text = list()
        self.critical = str()
        self.core = str()
        self.plot_and_rhythm = str()
        self.character = str()

    def read(self):
        logging.info("正在读取小说内容...")
        lines = list()
        with open(self.novel_path) as f:
            for line in f:
                line = line.strip()
                if line != "":
                    lines.append(line)
        title = lines[0].replace("《", "").replace("》", "")
        text = lines[1:]
        logging.info(f"小说标题为：{title}")
        logging.info(f"小说正文共有 {len(text)} 个自然段")
        logging.info(f"小说正文约有 {len(''.join(text))} 字")
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

    def critical_analysis(self):
        logging.info("正在分析最严重问题...")
        messages = [
            {"role": "system", "content": f"你是《{self.magazine}》杂志的资深编辑，对投稿有着严苛的要求。"
                                          "你不会强调自己的身份，你会直接开始讨论用户投稿的小说。"
                                          "你会仔细完整阅读用户投稿的小说，不强调自己的身份，向用户一针见血地指出小说存在的最严重问题。"},
            {"role": "user", "content": f"下面是我创作的短篇小说《{self.get_title()}》的全文：\n\n\n{self.get_text()}"},
        ]
        self.critical = chat_with_llm("deepseek-chat", 0.2, messages)

    def core_analysis(self):
        logging.info("正在分析核心问题...")
        messages = [
            {"role": "system", "content": f"你是《{self.magazine}》杂志的资深编辑，对投稿有着严苛的要求。"
                                          "你不会强调自己的身份，你会直接开始讨论用户投稿的小说。"
                                          "你会仔细完整阅读用户投稿的小说，认真思考用户投稿的小说在下列议题中的表现。"
                                          "如果表现不好，你会毫不留情的指出，以帮助用户更快成长；"
                                          "如果表现好，你会给予客观的评价，但不会夸赞，以免用户骄傲。"
                                          "1. 故事的核心概念/主题是否清晰、有力？"
                                          "2. 整体感觉如何？节奏是拖沓还是仓促？情绪是否连贯？"
                                          "3. 开头是否立刻抓住读者？结尾是否令人满意、余韵悠长？是否呼应了开头和主题？"
                                          "4. 主角的目标、动机、冲突是否明确且贯穿始终？"
                                          "5. 故事的主要脉络是否清晰？是否有逻辑断裂或突兀的转折？"},
            {"role": "user", "content": f"下面是我创作的短篇小说《{self.get_title()}》的全文：\n\n\n{self.get_text()}"},
        ]
        self.core = chat_with_llm("deepseek-chat", 0.2, messages)

    def plot_and_rhythm_analysis(self):
        logging.info("正在检查情节结构与节奏...")
        messages = [
            {"role": "system", "content": f"你是《{self.magazine}》杂志的资深编辑，对投稿有着严苛的要求。"
                                          "你不会强调自己的身份，你会直接开始讨论用户投稿的小说。"
                                          "你会仔细完整阅读用户投稿的小说，认真思考用户投稿的小说的情节结构与节奏在下列议题中的表现。"
                                          "如果表现不好，你会毫不留情的指出，以帮助用户更快成长；"
                                          "如果表现好，你会给予客观的评价，但不会夸赞，以免用户骄傲。"
                                          "1. 情节骨架是否完整？是否能清晰地提炼出“开端（设定期望、引入主角、触发事件）-> 发展（冲突升级、尝试解决、挫折、转折点）-> 高潮（最大冲突、决战/抉择）-> 结局（解决、后果、新常态）”的脉络？"
                                          "2. 节奏把控如何？哪些部分进展太慢（信息冗余、描写过多、无关情节）？哪些部分太快（关键情感/转折没展开）？高潮部分是否足够分量？结局是否仓促？"
                                          "3. 情节是否由冲突驱动？每个场景是否都有明确的冲突（外部或内部）在推动？冲突是否在合理升级？"
                                          "4. 情节是否保持悬念与张力？是否能持续吸引读者想知道接下来发生什么？转折点是否有效？"},
            {"role": "user", "content": f"下面是我创作的短篇小说《{self.get_title()}》的全文：\n\n\n{self.get_text()}"},
        ]
        self.plot_and_rhythm = chat_with_llm("deepseek-chat", 0.2, messages)

    def character_analysis(self):
        logging.info("正在分析人物...")
        logging.info("正在检查情节结构与节奏...")
        messages = [
            {"role": "system", "content": f"你是《{self.magazine}》杂志的资深编辑，对投稿有着严苛的要求。"
                                          "你不会强调自己的身份，你会直接开始讨论用户投稿的小说。"
                                          "你会仔细完整阅读用户投稿的小说，认真审视小说主要角色的人物弧光在下列议题中的表现。"
                                          "如果表现不好，你会毫不留情的指出，以帮助用户更快成长；"
                                          "如果表现好，你会给予客观的评价，但不会夸赞，以免用户骄傲。"
                                          "1. 主角是否经历了有意义的成长或转变？这个转变是否可信？动机是否充分？"
                                          "2. 主要配角是否立体？他们的存在是否服务于主角的成长或情节的推进？他们的动机是否清晰？"
                                          "3. 人物关系的发展是否自然、有张力？"},
            {"role": "user", "content": f"下面是我创作的短篇小说《{self.get_title()}》的全文：\n\n\n{self.get_text()}"},
        ]
        self.character = chat_with_llm("deepseek-chat", 0.2, messages)

    def analysis(self):
        self.critical_analysis()
        self.core_analysis()
        self.plot_and_rhythm_analysis()
        self.character_analysis()

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

## 核心问题

{self.core}

## 情节结构与节奏

{self.plot_and_rhythm}

## 任务

{self.character}

"""
        with open(report_path, "w") as f:
            f.write(report)


def main():
    # 设置命令行参数解析器
    parser = argparse.ArgumentParser(
        description='小说批改工具 - 输入小说文件进行批改分析',
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # 添加必需的文件名参数
    parser.add_argument(
        'filename',
        type=str,
        help='''输入要分析的小说文件名，仅支持纯文本文件''',
    )

    # 添加可选输出参数
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='reports',
        help='指定输出目录（（默认值：reports）',
    )

    # 添加可选的杂志参数
    parser.add_argument(
        '-m', '--magazine',
        type=str,
        default='科幻世界',
        help='指定想要投稿的杂志。不同杂志接收不同风格、类型的稿件，对稿件有不同要求，指定杂志有助于做出更有针对性的分析。（默认值：科幻世界）',
    )

    # 添加可选的日志级别参数
    parser.add_argument('-l', '--log-level',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='INFO',
                        help='设置日志级别（默认值：INFO）')

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

    # 检查日志级别
    numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(numeric_level, int):
        sys.exit(f"错误: 无效的日志级别 '{args.log_level}'")

    # 配置日志系统
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # 打印确认信息
    logging.info(f"准备分析小说: {args.filename}")
    logging.info(f"内容将输出至: {args.output}")

    # 分析小说
    novel = Novel(args.filename, args.output, args.magazine)
    novel.read()
    novel.analysis()
    novel.save()


if __name__ == "__main__":
    main()
