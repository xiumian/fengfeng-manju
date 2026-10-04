#!/usr/bin/env python3
"""
视频数据分析脚本
用于分析抖音视频的数据表现并给出优化建议
"""

import json
import sys
from typing import Dict, List, Tuple

# 抖音视频数据指标基准值
BENCHMARKS = {
    "完播率": {
        "优秀": 60,
        "良好": 45,
        "及格": 30,
        "单位": "%"
    },
    "点赞率": {
        "优秀": 5,
        "良好": 3,
        "及格": 1,
        "单位": "%"
    },
    "评论率": {
        "优秀": 1,
        "良好": 0.5,
        "及格": 0.1,
        "单位": "%"
    },
    "转发率": {
        "优秀": 0.5,
        "良好": 0.3,
        "及格": 0.1,
        "单位": "%"
    },
    "关注转化率": {
        "优秀": 0.5,
        "良好": 0.2,
        "及格": 0.1,
        "单位": "%"
    }
}

def calculate_rate(numerator: int, denominator: int) -> float:
    """计算比率"""
    if denominator == 0:
        return 0.0
    return (numerator / denominator) * 100

def evaluate_metric(metric_name: str, value: float) -> Tuple[str, str]:
    """评估指标表现"""
    benchmark = BENCHMARKS.get(metric_name, {})
    
    if not benchmark:
        return "未知", "无基准数据"
    
    if value >= benchmark["优秀"]:
        return "优秀", "表现很好，保持！"
    elif value >= benchmark["良好"]:
        return "良好", "表现不错，还有提升空间"
    elif value >= benchmark["及格"]:
        return "及格", "需要优化"
    else:
        return "较差", "急需优化"

def analyze_video_data(data: Dict) -> Dict:
    """
    分析视频数据
    
    Args:
        data: 包含视频数据的字典
            - views: 播放量
            - likes: 点赞数
            - comments: 评论数
            - shares: 转发数
            - followers_gained: 新增粉丝
            - completion_rate: 完播率（可选，如果没提供则计算）
    
    Returns:
        分析结果字典
    """
    views = data.get("views", 0)
    likes = data.get("likes", 0)
    comments = data.get("comments", 0)
    shares = data.get("shares", 0)
    followers_gained = data.get("followers_gained", 0)
    completion_rate = data.get("completion_rate", None)
    
    # 计算指标
    results = {}
    
    # 完播率（如果没提供则跳过）
    if completion_rate is not None:
        level, suggestion = evaluate_metric("完播率", completion_rate)
        results["完播率"] = {
            "value": f"{completion_rate}%",
            "level": level,
            "suggestion": suggestion
        }
    
    # 点赞率
    like_rate = calculate_rate(likes, views)
    level, suggestion = evaluate_metric("点赞率", like_rate)
    results["点赞率"] = {
        "value": f"{like_rate:.2f}%",
        "level": level,
        "suggestion": suggestion
    }
    
    # 评论率
    comment_rate = calculate_rate(comments, views)
    level, suggestion = evaluate_metric("评论率", comment_rate)
    results["评论率"] = {
        "value": f"{comment_rate:.2f}%",
        "level": level,
        "suggestion": suggestion
    }
    
    # 转发率
    share_rate = calculate_rate(shares, views)
    level, suggestion = evaluate_metric("转发率", share_rate)
    results["转发率"] = {
        "value": f"{share_rate:.2f}%",
        "level": level,
        "suggestion": suggestion
    }
    
    # 关注转化率
    follow_rate = calculate_rate(followers_gained, views)
    level, suggestion = evaluate_metric("关注转化率", follow_rate)
    results["关注转化率"] = {
        "value": f"{follow_rate:.2f}%",
        "level": level,
        "suggestion": suggestion
    }
    
    return results

def generate_optimization_suggestions(data: Dict, analysis: Dict) -> List[str]:
    """根据分析结果生成优化建议"""
    suggestions = []
    
    # 完播率优化
    completion = analysis.get("完播率", {})
    if completion.get("level") in ["较差", "及格"]:
        suggestions.append("【完播率优化】前3秒必须吸引人，缩短视频时长至15-30秒，增加节奏感")
    
    # 点赞率优化
    like = analysis.get("点赞率", {})
    if like.get("level") in ["较差", "及格"]:
        suggestions.append("【点赞率优化】增强情感共鸣或实用价值，使用热门BGM，增加视觉冲击")
    
    # 评论率优化
    comment = analysis.get("评论率", {})
    if comment.get("level") in ["较差", "及格"]:
        suggestions.append("【评论率优化】视频中提问引导，文案设置悬念，主动回复评论区")
    
    # 转发率优化
    share = analysis.get("转发率", {})
    if share.get("level") in ["较差", "及格"]:
        suggestions.append("【转发率优化】提供实用干货，打造社交货币内容，@朋友互动")
    
    # 关注转化率优化
    follow = analysis.get("关注转化率", {})
    if follow.get("level") in ["较差", "及格"]:
        suggestions.append("【关注转化率优化】明确账号价值主张，系列内容引导关注，固定片尾关注引导")
    
    # 播放量分析
    views = data.get("views", 0)
    if views < 500:
        suggestions.append("【流量池突破】视频未突破初始流量池，检查内容质量、标题、封面是否吸引人")
    elif views < 5000:
        suggestions.append("【内容优化】视频进入二级流量池但未继续突破，优化完播率和互动率")
    
    return suggestions

def print_analysis_report(data: Dict, analysis: Dict, suggestions: List[str]):
    """打印分析报告"""
    print("=" * 60)
    print("📊 抖音视频数据分析报告")
    print("=" * 60)
    
    print("\n【基础数据】")
    print(f"播放量: {data.get('views', 0):,}")
    print(f"点赞数: {data.get('likes', 0):,}")
    print(f"评论数: {data.get('comments', 0):,}")
    print(f"转发数: {data.get('shares', 0):,}")
    print(f"新增粉丝: {data.get('followers_gained', 0):,}")
    if data.get("completion_rate"):
        print(f"完播率: {data.get('completion_rate')}%")
    
    print("\n【指标评估】")
    for metric, result in analysis.items():
        print(f"{metric}: {result['value']} - {result['level']} ({result['suggestion']})")
    
    print("\n【优化建议】")
    if suggestions:
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")
    else:
        print("✅ 数据表现优秀，继续保持当前内容策略！")
    
    print("\n【下期内容建议】")
    if data.get("likes", 0) > data.get("views", 1) * 0.05:
        print("- 延续本期内容方向，点赞率很高")
    if data.get("comments", 0) > data.get("views", 1) * 0.01:
        print("- 评论区互动很好，下期可以回应评论区问题")
    print("- 尝试相似选题，测试是否可复制成功")
    print("=" * 60)

def main():
    """主函数"""
    # 示例数据（实际使用时会从文件或API读取）
    if len(sys.argv) > 1:
        # 从文件读取数据
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        # 使用示例数据
        data = {
            "views": 10000,
            "likes": 300,
            "comments": 50,
            "shares": 20,
            "followers_gained": 15,
            "completion_rate": 35.5
        }
        print("⚠️  使用示例数据，传入JSON文件可获得真实分析")
        print("用法: python analyze_video_data.py data.json\n")
    
    # 分析数据
    analysis = analyze_video_data(data)
    
    # 生成优化建议
    suggestions = generate_optimization_suggestions(data, analysis)
    
    # 打印报告
    print_analysis_report(data, analysis, suggestions)
    
    # 输出JSON格式结果（供其他程序调用）
    output = {
        "data": data,
        "analysis": analysis,
        "suggestions": suggestions
    }
    
    with open("analysis_result.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 分析结果已保存到 analysis_result.json")

if __name__ == "__main__":
    main()
