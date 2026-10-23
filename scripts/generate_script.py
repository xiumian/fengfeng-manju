#!/usr/bin/env python3
"""
视频脚本生成辅助脚本
用于生成符合抖音风格的视频脚本
"""

import json
import sys
from typing import Dict, List

# 视频类型模板
VIDEO_TYPE_TEMPLATES = {
    "教程": {
        "structure": ["开头展示成果", "引入问题", "分步演示", "成果展示", "关注引导"],
        "duration": "30-60秒",
        "hook_types": ["成果展示", "痛点提问", "颠覆认知"]
    },
    "种草": {
        "structure": ["痛点引入", "产品介绍", "使用演示", "优缺点总结", "购买建议"],
        "duration": "30-45秒",
        "hook_types": ["痛点场景", "之前/之后对比", "真实体验"]
    },
    "剧情": {
        "structure": ["快速进入场景", "冲突展开", "反转/高潮", "结尾金句/悬念"],
        "duration": "15-30秒",
        "hook_types": ["直接冲突", "悬念设置", "反转预告"]
    },
    "Vlog": {
        "structure": ["精彩预告", "时间线叙事", "亮点/感悟", "结尾引导"],
        "duration": "30-45秒",
        "hook_types": ["精彩片段合集", "好奇心引诱", "情感共鸣"]
    },
    "测评": {
        "structure": ["引入话题", "测评过程", "结果公布", "推荐指数"],
        "duration": "45-60秒",
        "hook_types": ["悬念设置", "好奇提问", "挑战引入"]
    },
    "知识分享": {
        "structure": ["抛出观点", "解释原因", "给出方法", "总结升华"],
        "duration": "30-45秒",
        "hook_types": ["颠覆认知", "直击痛点", "数字吸引"]
    }
}

# 开头Hook模板
HOOK_TEMPLATES = {
    "成果展示": [
        "用了这个方法，{result}",
        "没想到{result}",
        "教你{result}，超简单！"
    ],
    "痛点提问": [
        "你是不是也{problem}？",
        "有没有{problem}的？",
        "谁懂啊，{problem}"
    ],
    "悬念设置": [
        "没想到竟然...",
        "你绝对不知道...",
        "真相竟然是..."
    ],
    "颠覆认知": [
        "90%的人都不知道...",
        "这件事你可能一直做错了",
        "别再{mistake}了！"
    ],
    "数字吸引": [
        "3个技巧让你...",
        "花{amount}元搞定...",
        "{number}天见效..."
    ]
}

# 标题模板
TITLE_TEMPLATES = [
    "{number}个{method}，让你{result}",
    "{problem}？教你{solution}",
    "没想到{method}竟然{result}",
    "终于找到{solution}的方法了！",
    "{product}测评，到底值不值得买？",
    "{number}天{did_something}，结果...",
    "谁懂啊，{emotion}",
    "建议收藏！{reason}"
]

# 标签推荐
HASHTAG_CATEGORIES = {
    "热门": ["#抖音热门", "#涨粉", "#爆款", "#热门话题"],
    "垂直": {
        "美食": ["#美食教程", "#家常菜", "#美食分享", "#吃货"],
        "美妆": ["#美妆教程", "#化妆技巧", "#平价好物", "#护肤"],
        "穿搭": ["#穿搭分享", "#OOTD", "#平价穿搭", "#显瘦穿搭"],
        "健身": ["#健身教程", "#减肥", "#居家健身", "#运动"],
        "知识": ["#干货分享", "#知识科普", "#职场技巧", "#学习方法"],
        "生活": ["#生活记录", "#Vlog", "#日常", "#生活方式"],
        "搞笑": ["#搞笑视频", "#笑死我了", "#日常搞笑", "#沙雕"]
    }
}

def generate_hook(video_type: str, topic: str) -> List[str]:
    """生成开头Hook建议"""
    hooks = []

    if video_type in VIDEO_TYPE_TEMPLATES:
        hook_types = VIDEO_TYPE_TEMPLATES[video_type]["hook_types"]

        for hook_type in hook_types:
            if hook_type in HOOK_TEMPLATES:
                templates = HOOK_TEMPLATES[hook_type]
                for template in templates[:2]:  # 每个类型取2个
                    hooks.append(template)

    return hooks[:5]  # 返回前5个

def generate_script(outline: Dict) -> Dict:
    """
    根据大纲生成详细脚本

    Args:
        outline: 脚本大纲
            - type: 视频类型
            - topic: 主题
            - duration: 目标时长
            - key_points: 关键点列表

    Returns:
        完整脚本字典
    """
    video_type = outline.get("type", "教程")
    topic = outline.get("topic", "")
    duration = outline.get("duration", 30)
    key_points = outline.get("key_points", [])

    # 获取类型模板
    template = VIDEO_TYPE_TEMPLATES.get(video_type, VIDEO_TYPE_TEMPLATES["教程"])

    # 生成脚本结构
    script = {
        "title": f"【{video_type}】{topic}",
        "type": video_type,
        "target_duration": f"{duration}秒",
        "hook_suggestions": generate_hook(video_type, topic),
        "structure": []
    }

    # 根据结构生成详细内容
    structure = template["structure"]
    time_per_section = duration // len(structure)

    for i, section in enumerate(structure):
        section_script = {
            "section": section,
            "time": f"{i * time_per_section}-{((i + 1) * time_per_section)}秒",
            "visual": "",  # 画面描述
            "audio": "",  # 音频/文案
            "text_overlay": "",  # 字幕/文字
            "tips": ""  # 技巧提示
        }

        # 根据不同部分和视频类型填充内容
        if i == 0:  # 开头部分
            section_script["visual"] = "吸引人的画面/动作"
            section_script["audio"] = f"{generate_hook(video_type, topic)[0] if generate_hook(video_type, topic) else '开头吸引人'}"
            section_script["tips"] = "前3秒决定完播率，必须吸引人！"

        script["structure"].append(section_script)

    # 生成标题建议
    script["title_suggestions"] = generate_titles(topic, video_type)

    # 生成标签建议
    script["hashtag_suggestions"] = generate_hashtags(topic, video_type)

    # 生成文案建议
    script["caption_suggestions"] = generate_captions(topic, video_type)

    return script

def generate_titles(topic: str, video_type: str) -> List[str]:
    """生成标题建议"""
    titles = []

    for template in TITLE_TEMPLATES[:3]:
        try:
            title = template.format(
                number="3",
                method=topic,
                result="效果惊人",
                problem=f"为{topic}烦恼",
                solution=topic,
                product=topic,
                did_something=topic,
                emotion=f"这个{topic}太绝了",
                reason=f"{topic}太实用了"
            )
            titles.append(title)
        except:
            pass

    return titles if titles else [f"【{video_type}】{topic}"]

def generate_hashtags(topic: str, video_type: str) -> Dict[str, List[str]]:
    """生成标签建议"""
    hashtags = {
        "热门标签": HASHTAG_CATEGORIES["热门"][:2],
        "垂直标签": [],
        "长尾标签": [f"#{topic}", f"#{video_type}{topic}"]
    }

    # 根据视频类型推荐垂直标签
    for category, tags in HASHTAG_CATEGORIES["垂直"].items():
        if category in video_type or category in topic:
            hashtags["垂直标签"] = tags[:3]
            break

    if not hashtags["垂直标签"]:
        hashtags["垂直标签"] = HASHTAG_CATEGORIES["垂直"]["生活"][:3]

    return hashtags

def generate_captions(topic: str, video_type: str) -> List[str]:
    """生成文案建议"""
    captions = [
        f"今天教大家{topic}，超级简单！\n\n#标签1 #标签2 #标签3\n\n你学会了吗？评论区告诉我～",
        f"关于{topic}，你可能一直都做错了！\n\n正确做法在视频里👆\n\n#标签1 #标签2\n\n关注我学更多干货！",
        f"没想到{topic}竟然这么简单！\n\n学会的扣1🙋\n\n#标签1 #标签2 #标签3"
    ]

    return captions

def print_script(script: Dict):
    """打印脚本"""
    print("=" * 60)
    print(f"📝 视频脚本：{script['title']}")
    print("=" * 60)

    print(f"\n【视频类型】{script['type']}")
    print(f"【目标时长】{script['target_duration']}")

    print("\n【开头Hook建议】")
    for i, hook in enumerate(script["hook_suggestions"], 1):
        print(f"{i}. {hook}")

    print("\n【脚本结构】")
    for section in script["structure"]:
        print(f"\n--- {section['section']} ({section['time']}) ---")
        print(f"画面: {section['visual']}")
        print(f"音频: {section['audio']}")
        print(f"字幕: {section['text_overlay']}")
        print(f"提示: {section['tips']}")

    print("\n【标题建议】")
    for i, title in enumerate(script["title_suggestions"], 1):
        print(f"{i}. {title}")

    print("\n【标签建议】")
    hashtags = script["hashtag_suggestions"]
    print(f"热门: {', '.join(hashtags['热门标签'])}")
    print(f"垂直: {', '.join(hashtags['垂直标签'])}")
    print(f"长尾: {', '.join(hashtags['长尾标签'])}")

    print("\n【文案建议】")
    for i, caption in enumerate(script["caption_suggestions"], 1):
        print(f"\n文案{i}:\n{caption}")

    print("\n" + "=" * 60)

def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 从文件读取大纲
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            outline = json.load(f)
    else:
        # 交互式输入
        print("📝 视频脚本生成器")
        print("=" * 60)

        outline = {
            "type": input("视频类型 (教程/种草/剧情/Vlog/测评/知识分享): ") or "教程",
            "topic": input("视频主题: "),
            "duration": int(input("目标时长(秒, 默认30): ") or 30),
            "key_points": []
        }

        print("请输入关键点（每行一个，空行结束）:")
        while True:
            point = input()
            if not point:
                break
            outline["key_points"].append(point)

    # 生成脚本
    script = generate_script(outline)

    # 打印脚本
    print_script(script)

    # 保存为JSON
    with open("generated_script.json", "w", encoding="utf-8") as f:
        json.dump(script, f, ensure_ascii=False, indent=2)

    print("\n✅ 脚本已保存到 generated_script.json")

if __name__ == "__main__":
    main()
