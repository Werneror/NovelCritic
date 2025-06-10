import argparse
import json
import logging
import os
import sys
from datetime import datetime
from openai import OpenAI


def chat_with_llm(model, temperature, message, response_format):
    client = OpenAI(api_key=os.getenv("API_KEY"), base_url=os.getenv("BASE_URL"))
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=message,
        stream=True,
        response_format={
            'type': response_format,
        },
    )
    full_content = ""
    logging.info(f"{model} 思考中...")
    # 遍历流式响应，实时输出到终端
    for chunk in response:
        if chunk.choices[0].delta.content:
            delta_content = chunk.choices[0].delta.content
            print(delta_content, end='', flush=True)
            full_content += delta_content
    print()
    return full_content


class Scene:

    def __init__(self, magazine, title, paragraphs):
        self.magazine = magazine
        self.title = title
        self.paragraphs = paragraphs
        self.validity = str()
        self.show_and_tell = str()
        self.dialogue = str()

    def get_title(self):
        return self.title

    def get_text(self):
        return "\n\n".join(self.paragraphs)

    def get_system_prompt(self):
        return f"""你是《{self.magazine}》杂志的编辑，具有丰富的审稿经验，同时也是资深xx编剧与小说家，熟悉故事创作原理，具有丰富的故事创作经验。
现在，你受邀成为小说写作课的特聘教授，负责批改学生作业。对这项工作，你非常认真负责。
你总是毫不留情，一针见血，直击要害，指出学生提交的小说中的问题。你总是非常吝啬自己的赞美，除非遇到非常优秀的作品，否则你不会给出任何好的评价。"""

    def validity_analysis(self):
        logging.info("正在分析该场景的有效性...")
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user",
             "content": f"老师您好，我的小说题目是《{self.get_title()}》，下面的内容是我的小说中的一个场景：\n\n\n{self.get_text()}"},
            {"role": "assistant", "content": "收到，我会仔细阅读。就你给我的这个场景，你关注哪方面的问题？"},
            {"role": "user", "content": "我关注这个场景有效性的问题。想请老师点评："
                                        "1. 场景是否有明确的目的？（例如：展示人物性格、推进情节、制造冲突、揭示信息、建立氛围）"
                                        "2. 场景是否遵循“目标 -> 冲突 -> 挫折/结果”的基本结构？"
                                        "3. 场景的开头和结尾是否有力？是否能自然过渡到下一场景？"
                                        "4. 场景中的视角是否清晰一致？（如果是单一视角，确保没有“越界”）"},
        ]
        self.validity = chat_with_llm("deepseek-chat", 0.2, messages, "text")

    def show_and_tell_analysis(self):
        logging.info("正在分析该场景的展示与讲述...")
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user",
             "content": f"老师您好，我的小说题目是《{self.get_title()}》，下面的内容是我的小说中的一个场景：\n\n\n{self.get_text()}"},
            {"role": "assistant", "content": "收到，我会仔细阅读。就你给我的这个场景，你关注哪方面的问题？"},
            {"role": "user", "content": "我关注这个场景的“展示”与“讲述”问题。想请老师点评："
                                        "1. 否存在大量“讲述”而非“展示”的地方？"
                                        "2. 关键的情感和信息是否通过人物的行动、对话、感官细节等来“展示”？"},
        ]
        self.show_and_tell = chat_with_llm("deepseek-chat", 0.2, messages, "text")

    def dialogue_analysis(self):
        logging.info("正在分析该场景的对话...")
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user",
             "content": f"老师您好，我的小说题目是《{self.get_title()}》，下面的内容是我的小说中的一个场景：\n\n\n{self.get_text()}"},
            {"role": "assistant", "content": "收到，我会仔细阅读。就你给我的这个场景，你关注哪方面的问题？"},
            {"role": "user", "content": "我关注这个场景中的对话。想请老师点评："
                                        "1. 对话是否推动情节或揭示人物性格？是否存在无效的闲聊式对话？"
                                        "2. 对话是否符合人物身份、性格、所处情境？每个人的说话方式是否有区分度？"
                                        "3. 对话是否自然流畅？是否存在书面化的对话，或是信息倾泻？"
                                        "4. 对话标签（“他说”、“她问道” 等）是否清晰简洁？是否能适当融入动作描写代替标签？"},
        ]
        self.dialogue = chat_with_llm("deepseek-chat", 0.2, messages, "text")

    def analysis(self):
        self.validity_analysis()
        self.show_and_tell_analysis()
        self.dialogue_analysis()

    def report(self):
        return f"""
#### 场景有效性分析

{self.validity}

#### 展示与讲述分析

{self.show_and_tell}

#### 对话分析

{self.dialogue}

"""


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
        self.theme = str()
        self.scenes = list()

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

    def get_text_with_no(self):
        text_with_no = list()
        for i, p in enumerate(self.text):
            p = f"【{i + 1}】{p}"
            text_with_no.append(p)
        return "\n\n".join(text_with_no)

    def get_paragraphs_by_scene(self, scene):
        paragraphs = list()
        for i, p in enumerate(self.text):
            if scene["paragraphs_start"] <= i + 1 <= scene["paragraphs_end"]:
                paragraphs.append(p)
        return paragraphs

    def get_system_prompt(self):
        return f"""你是《{self.magazine}》杂志的编辑，具有丰富的审稿经验，同时也是资深xx编剧与小说家，熟悉故事创作原理，具有丰富的故事创作经验。
现在，你受邀成为小说写作课的特聘教授，负责批改学生作业。对这项工作，你非常认真负责。
你总是毫不留情，一针见血，直击要害，指出学生提交的小说中的问题。你总是非常吝啬自己的赞美，除非遇到非常优秀的作品，否则你不会给出任何好的评价。"""

    def critical_analysis(self):
        logging.info("正在分析最严重问题...")
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user",
             "content": f"老师您好。下面是我创作的短篇小说《{self.get_title()}》的全文：\n\n\n{self.get_text()}"},
            {"role": "assistant", "content": "收到，我会仔细阅读。就你给我的这篇小说，你关注哪方面的问题？"},
            {"role": "user", "content": "我关注这篇小说最严重的问题。想请老师点评，这篇小说中存在的最严重问题是什么？"},
        ]
        self.critical = chat_with_llm("deepseek-chat", 0.2, messages, "text")

    def core_analysis(self):
        logging.info("正在分析核心问题...")
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user",
             "content": f"老师您好。下面是我创作的短篇小说《{self.get_title()}》的全文：\n\n\n{self.get_text()}"},
            {"role": "assistant", "content": "收到，我会仔细阅读。就你给我的这篇小说，你关注哪方面的问题？"},
            {"role": "user", "content": "我关注这篇小说的一些核心问题。想请老师点评："
                                        "1. 故事的核心概念/主题是否清晰、有力？"
                                        "2. 整体感觉如何？节奏是拖沓还是仓促？情绪是否连贯？"
                                        "3. 开头是否立刻抓住读者？结尾是否令人满意、余韵悠长？是否呼应了开头和主题？"
                                        "4. 主角的目标、动机、冲突是否明确且贯穿始终？"
                                        "5. 故事的主要脉络是否清晰？是否有逻辑断裂或突兀的转折？"},
        ]
        self.core = chat_with_llm("deepseek-chat", 0.2, messages, "text")

    def plot_and_rhythm_analysis(self):
        logging.info("正在检查情节结构与节奏...")
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user",
             "content": f"老师您好。下面是我创作的短篇小说《{self.get_title()}》的全文：\n\n\n{self.get_text()}"},
            {"role": "assistant", "content": "收到，我会仔细阅读。就你给我的这篇小说，你关注哪方面的问题？"},
            {"role": "user", "content": "我关注这篇小说的情节结构与节奏。想请老师点评："
                                        "1. 情节骨架是否完整？是否能清晰地提炼出“开端（设定期望、引入主角、触发事件）-> 发展（冲突升级、尝试解决、挫折、转折点）-> 高潮（最大冲突、决战/抉择）-> 结局（解决、后果、新常态）”的脉络？"
                                        "2. 节奏把控如何？哪些部分进展太慢（信息冗余、描写过多、无关情节）？哪些部分太快（关键情感/转折没展开）？高潮部分是否足够分量？结局是否仓促？"
                                        "3. 情节是否由冲突驱动？每个场景是否都有明确的冲突（外部或内部）在推动？冲突是否在合理升级？"
                                        "4. 情节是否保持悬念与张力？是否能持续吸引读者想知道接下来发生什么？转折点是否有效？"},
        ]
        self.plot_and_rhythm = chat_with_llm("deepseek-chat", 0.2, messages, "text")

    def character_analysis(self):
        logging.info("正在分析人物弧光...")
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user",
             "content": f"老师您好。下面是我创作的短篇小说《{self.get_title()}》的全文：\n\n\n{self.get_text()}"},
            {"role": "assistant", "content": "收到，我会仔细阅读。就你给我的这篇小说，你关注哪方面的问题？"},
            {"role": "user", "content": "我关注这篇小说中的人物弧光。想请老师点评："
                                        "1. 主角是否经历了有意义的成长或转变？这个转变是否可信？动机是否充分？"
                                        "2. 主要配角是否立体？他们的存在是否服务于主角的成长或情节的推进？他们的动机是否清晰？"
                                        "3. 人物关系的发展是否自然、有张力？"},
        ]
        self.character = chat_with_llm("deepseek-chat", 0.2, messages, "text")

    def theme_analysis(self):
        logging.info("正在分析故事主旨...")
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user",
             "content": f"老师您好。下面是我创作的短篇小说《{self.get_title()}》的全文：\n\n\n{self.get_text()}"},
            {"role": "assistant", "content": "收到，我会仔细阅读。就你给我的这篇小说，你关注哪方面的问题？"},
            {"role": "user", "content": "我关注这篇小说的主题与核心。想请老师点评："
                                        "1. 故事想表达的核心思想是什么？是否贯穿始终？是否通过情节和人物自然地展现出来，而不是强行说教？"
                                        "2. 结局是否强化或反思了这个主题？"},
        ]
        self.theme = chat_with_llm("deepseek-chat", 0.2, messages, "text")

    def scenes_analysis(self):
        logging.info("正在分析故事场景...")
        messages = [
            {"role": "system",
             "content": f"你是一名非常负责的文学编辑，你会仔细完整阅读用户投稿的小说，认真分析小说具有哪些场景，"
                        "然后以 JSON 格式输出一份场景列表。示例输出如下："
                        ""
                        '{"total": 2, "scenes": [{"scene": 1, "summary": "场景 1 的概述", "paragraphs_start": 1, "paragraphs_end": 4}, {"scene": 2, "summary": "场景 2 的概述", "paragraphs_start": 5, "paragraphs_end": 7}]}'
                        ""
                        "含义是：共有 2 个场景。第 1 个场景包含第 1~4 自然段，第 2 个场景包含第 5~7 自然段。"},
            {"role": "user",
             "content": f"下面是我创作的短篇小说《{self.get_title()}》的全文，每一自然段开头用括号括起来的数字是自然段编号：\n\n\n{self.get_text_with_no()}"},
        ]
        result = json.loads(chat_with_llm("deepseek-chat", 0.2, messages, "json_object"))
        logging.info(f"共有 {result['total']} 个场景")
        self.scenes = result["scenes"]

    def analysis(self):
        # 对全文的分析
        self.critical_analysis()
        self.core_analysis()
        self.plot_and_rhythm_analysis()
        self.character_analysis()
        self.theme_analysis()
        # 对场景的分析
        self.scenes_analysis()
        for scene in self.scenes:
            logging.info(
                f"正在分析场景 {scene['scene']}（{scene['paragraphs_start']}~{scene['paragraphs_end']}）: {scene['summary']}")
            s = Scene(self.magazine, self.get_title(), self.get_paragraphs_by_scene(scene))
            s.analysis()
            scene["report"] = s.report()

    def save(self):
        report_filename = f"小说《{self.get_title()}》分析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path = os.path.join(self.output_dir, report_filename)
        scenes = str()
        for i, scene in enumerate(self.scenes):
            scenes += f"""
### 场景 {i + 1}

范围：从第 {scene['paragraphs_start']} 到第 {scene['paragraphs_end']} 个自然段。

主要内容：{scene['summary']}

对于该场景的具体分析如下。

{scene['report']}

"""
        report = f"""
# 小说《{self.get_title()}》分析报告

本文是小说《{self.get_title()}》的分析报告，由大语言模型于 {datetime.now().strftime('%Y 年 %m 月 %d 日 %H 时 %M 分 %S 秒')}生成。

## 小说概括

- 字数：越 {len(self.get_text())}
- 自然段：共 {len(self.text)} 个
- 场景：共 {len(self.scenes)} 个

## 最严重问题

{self.critical}

## 核心问题

{self.core}

## 情节结构与节奏

{self.plot_and_rhythm}

## 人物弧光

{self.character}

## 故事主旨

{self.theme}

## 场景分析

{scenes}

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
