#!/usr/bin/env python3
"""
LeetCode 每日学习分析
分析当天的做题情况，生成学习日报
"""

import os
import re
import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# 做题记录目录（可配置）
NOTES_DIR = os.environ.get("LEETCODE_NOTES_DIR", r"<USER_DIR>\Documents\leetcode")
REPORTS_DIR = os.path.join(NOTES_DIR, "reports")

def ensure_dir():
    """确保目录存在"""
    os.makedirs(REPORTS_DIR, exist_ok=True)

def get_monthly_file():
    """获取当前月份的做题记录文件路径"""
    now = datetime.now()
    filename = f"leetcode-notes-{now.year}-{now.month:02d}.md"
    return os.path.join(NOTES_DIR, filename)

def get_daily_report_path():
    """获取今日日报路径"""
    now = datetime.now()
    filename = f"daily-report-{now.year}-{now.month:02d}-{now.day:02d}.md"
    return os.path.join(REPORTS_DIR, filename)

def parse_problems_from_file(filepath):
    """从做题记录文件中解析题目信息"""
    if not os.path.exists(filepath):
        return []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    problems = []
    # 匹配题目块
    pattern = r'# (\d+\.\s*.+?)\n(.*?)(?=---\n|$)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for title, block in matches:
        problem = {
            'title': title.strip(),
            'difficulty': '',
            'submissions': [],
            'current_status': '',
            'best_runtime': '',
            'tags': []
        }
        
        # 提取难度
        difficulty_match = re.search(r'\*\*难度\*\*[:：]\s*(\S+)', block)
        if difficulty_match:
            problem['difficulty'] = difficulty_match.group(1)
        
        # 提取当前状态
        status_match = re.search(r'\*\*当前状态\*\*[:：]\s*(\[.*?\]|\S+)\s*(.+?)$', block, re.MULTILINE)
        if status_match:
            problem['current_status'] = f"{status_match.group(1)} {status_match.group(2).strip()}"
        
        # 提取最佳用时
        runtime_match = re.search(r'\*\*最佳用时\*\*[:：]\s*(.+?)$', block, re.MULTILINE)
        if runtime_match:
            problem['best_runtime'] = runtime_match.group(1).strip()
        
        # 提取提交历史
        history_pattern = r'\|\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})\s*\|\s*(\[.*?\]\s*.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|'
        history_matches = re.findall(history_pattern, block)
        
        for match in history_matches:
            submission = {
                'date': match[0],
                'status': match[1],
                'runtime': match[2],
                'memory': match[3],
                'note': match[4]
            }
            problem['submissions'].append(submission)
        
        # 提取标签（从代码或笔记中）
        if '数组' in block or 'array' in block.lower():
            problem['tags'].append('数组')
        if '链表' in block or 'linked list' in block.lower():
            problem['tags'].append('链表')
        if '树' in block or 'tree' in block.lower():
            problem['tags'].append('树')
        if '哈希' in block.lower() or 'hash' in block.lower():
            problem['tags'].append('哈希表')
        if '动态规划' in block or 'dp' in block.lower():
            problem['tags'].append('动态规划')
        if '回溯' in block or 'backtrack' in block.lower():
            problem['tags'].append('回溯')
        if '贪心' in block or 'greedy' in block.lower():
            problem['tags'].append('贪心')
        if '二分' in block:
            problem['tags'].append('二分查找')
        if '排序' in block:
            problem['tags'].append('排序')
        if '递归' in block:
            problem['tags'].append('递归')
        
        problems.append(problem)
    
    return problems

def filter_today_submissions(problems, target_date=None):
    """筛选今天的提交"""
    if target_date is None:
        target_date = datetime.now().strftime("%Y-%m-%d")
    
    today_problems = []
    
    for problem in problems:
        today_submissions = []
        for sub in problem['submissions']:
            sub_date = sub['date'].split()[0]
            if sub_date == target_date:
                today_submissions.append(sub)
        
        if today_submissions:
            today_problems.append({
                **problem,
                'today_submissions': today_submissions
            })
    
    return today_problems

def generate_daily_report(problems, date=None):
    """生成每日学习报告"""
    if date is None:
        date = datetime.now()
    
    date_str = date.strftime("%Y-%m-%d")
    weekday = date.strftime("%A")
    
    # 统计
    total_count = len(problems)
    solved_count = sum(1 for p in problems if '通过' in p.get('current_status', ''))
    error_count = total_count - solved_count
    
    # 难度分布
    difficulty_dist = defaultdict(int)
    for p in problems:
        diff = p.get('difficulty', '未知')
        difficulty_dist[diff] += 1
    
    # 知识点分布
    tag_dist = defaultdict(int)
    for p in problems:
        for tag in p.get('tags', []):
            tag_dist[tag] += 1
    
    # 生成报告
    report = f"""# 📊 LeetCode 学习日报

**日期**: {date_str} ({weekday})
**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

## 📈 今日概览

| 指标 | 数值 |
|------|------|
| 做题总数 | {total_count} 道 |
| 通过 | ✅ {solved_count} 道 |
| 未通过 | ❌ {error_count} 道 |
| 通过率 | {solved_count/total_count*100:.1f}% (如有题目) |

---

## 📚 难度分布

| 难度 | 数量 |
|------|------|
| 简单 | {difficulty_dist.get('简单', 0)} |
| 中等 | {difficulty_dist.get('中等', 0)} |
| 困难 | {difficulty_dist.get('困难', 0)} |
| 未知 | {difficulty_dist.get('未知', 0)} |

---

## 🏷️ 知识点分布

"""
    
    if tag_dist:
        report += "| 知识点 | 题目数 |\n|--------|--------|\n"
        for tag, count in sorted(tag_dist.items(), key=lambda x: -x[1]):
            report += f"| {tag} | {count} |\n"
    else:
        report += "*暂无知识点标记*\n"
    
    report += "\n---\n\n## 📝 题目详情\n\n"
    
    for i, p in enumerate(problems, 1):
        status_icon = "✅" if '通过' in p.get('current_status', '') else "❌"
        report += f"### {i}. {p['title']}\n\n"
        report += f"- **难度**: {p.get('difficulty', '未知')}\n"
        report += f"- **状态**: {status_icon} {p.get('current_status', '未知')}\n"
        report += f"- **最佳用时**: {p.get('best_runtime', 'N/A')}\n"
        
        if p.get('tags'):
            report += f"- **知识点**: {', '.join(p['tags'])}\n"
        
        if p.get('today_submissions'):
            report += f"- **今日提交**: {len(p['today_submissions'])} 次\n"
            for sub in p['today_submissions']:
                report += f"  - {sub['date']}: {sub['status']} ({sub['runtime']})\n"
        
        report += "\n"
    
    report += f"""---

## 💡 学习建议

"""
    
    # 生成建议
    suggestions = []
    
    if error_count > 0:
        suggestions.append(f"- ⚠️ 今天有 {error_count} 道题未通过，建议复习错题")
    
    if difficulty_dist.get('简单', 0) > 3:
        suggestions.append("- 💪 简单题较多，可以尝试挑战中等难度")
    
    if difficulty_dist.get('困难', 0) > 0:
        suggestions.append("- 🎯 挑战了困难题，继续保持！")
    
    if tag_dist:
        top_tag = max(tag_dist.items(), key=lambda x: x[1])
        suggestions.append(f"- 📖 今天重点练习了 **{top_tag[0]}** ({top_tag[1]} 题)")
    
    if total_count >= 5:
        suggestions.append("- 🔥 今天刷题量不错，继续保持！")
    elif total_count > 0:
        suggestions.append("- 📈 每天坚持刷题，积少成多！")
    else:
        suggestions.append("- ⏰ 今天还没有刷题记录，加油！")
    
    report += "\n".join(suggestions)
    
    report += f"""

---

## 📅 明日目标

- [ ] 继续刷题，保持手感
- [ ] 复习今日错题
- [ ] 尝试新的知识点

---

*报告由 LeetCode Wrong Notes Skill 自动生成*
"""
    
    return report

def main():
    """主函数"""
    print("=" * 50)
    print("LeetCode 每日学习分析")
    print("=" * 50)
    
    # 解析题目
    filepath = get_monthly_file()
    print(f"读取做题记录：{filepath}")
    
    problems = parse_problems_from_file(filepath)
    print(f"找到 {len(problems)} 道题目")
    
    # 筛选今天的提交
    today = datetime.now().strftime("%Y-%m-%d")
    today_problems = filter_today_submissions(problems, today)
    
    # 如果没有今天的，尝试昨天
    if not today_problems:
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        today_problems = filter_today_submissions(problems, yesterday)
        print(f"今日无记录，使用昨日数据 ({yesterday})")
    
    print(f"今日/昨日提交：{len(today_problems)} 道题")
    
    # 生成报告
    ensure_dir()
    report_path = get_daily_report_path()
    
    report = generate_daily_report(today_problems)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 日报已生成：{report_path}")
    print("=" * 50)

if __name__ == "__main__":
    main()
