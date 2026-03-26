#!/usr/bin/env python3
"""
LeetCode 每周学习分析
分析一周的做题情况，识别薄弱知识点，给出学习建议
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

def get_weekly_report_path():
    """获取周报路径"""
    now = datetime.now()
    # 获取本周的周一
    monday = now - timedelta(days=now.weekday())
    filename = f"weekly-report-{monday.year}-W{monday.isocalendar()[1]:02d}.md"
    return os.path.join(REPORTS_DIR, filename)

def parse_problems_from_file(filepath):
    """从做题记录文件中解析题目信息"""
    if not os.path.exists(filepath):
        return []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    problems = []
    pattern = r'# (\d+\.\s*.+?)\n(.*?)(?=---\n|$)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for title, block in matches:
        problem = {
            'title': title.strip(),
            'difficulty': '',
            'submissions': [],
            'current_status': '',
            'best_runtime': '',
            'tags': [],
            'first_date': '',
            'last_date': ''
        }
        
        # 提取难度
        difficulty_match = re.search(r'\*\*难度\*\*[:：]\s*(\S+)', block)
        if difficulty_match:
            problem['difficulty'] = difficulty_match.group(1)
        
        # 提取首次日期
        first_date_match = re.search(r'\*\*首次日期\*\*[:：]\s*(\S+)', block)
        if first_date_match:
            problem['first_date'] = first_date_match.group(1)
        
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
        if '树' in block or 'tree' in block.lower() or '二叉树' in block:
            problem['tags'].append('树')
        if '哈希' in block.lower() or 'hash' in block.lower():
            problem['tags'].append('哈希表')
        if '动态规划' in block or 'dp' in block.lower() or '背包' in block:
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
        if '栈' in block or 'stack' in block.lower():
            problem['tags'].append('栈')
        if '队列' in block or 'queue' in block.lower():
            problem['tags'].append('队列')
        if '滑动窗口' in block:
            problem['tags'].append('滑动窗口')
        if '前缀和' in block:
            problem['tags'].append('前缀和')
        if 'dfs' in block.lower() or '深度优先' in block:
            problem['tags'].append('DFS')
        if 'bfs' in block.lower() or '广度优先' in block:
            problem['tags'].append('BFS')
        
        # 提取最后提交日期
        if problem['submissions']:
            problem['last_date'] = problem['submissions'][-1]['date'].split()[0]
        
        problems.append(problem)
    
    return problems

def filter_week_submissions(problems, week_start=None):
    """筛选本周的提交"""
    if week_start is None:
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    week_end = week_start + timedelta(days=7)
    
    week_problems = []
    week_start_str = week_start.strftime("%Y-%m-%d")
    week_end_str = week_end.strftime("%Y-%m-%d")
    
    for problem in problems:
        week_submissions = []
        for sub in problem['submissions']:
            sub_date = sub['date'].split()[0]
            if week_start_str <= sub_date < week_end_str:
                week_submissions.append(sub)
        
        if week_submissions:
            week_problems.append({
                **problem,
                'week_submissions': week_submissions
            })
    
    return week_problems, week_start_str, week_end_str

def analyze_weaknesses(problems):
    """分析薄弱知识点"""
    tag_stats = defaultdict(lambda: {'total': 0, 'solved': 0, 'failed': 0})
    
    for problem in problems:
        tags = problem.get('tags', [])
        is_solved = '通过' in problem.get('current_status', '')
        
        if not tags:
            tags = ['未分类']
        
        for tag in tags:
            tag_stats[tag]['total'] += 1
            if is_solved:
                tag_stats[tag]['solved'] += 1
            else:
                tag_stats[tag]['failed'] += 1
    
    # 计算正确率
    weakness_list = []
    for tag, stats in tag_stats.items():
        if stats['total'] >= 2:  # 至少做过 2 道题才分析
            accuracy = stats['solved'] / stats['total'] * 100
            weakness_list.append({
                'tag': tag,
                'total': stats['total'],
                'solved': stats['solved'],
                'failed': stats['failed'],
                'accuracy': accuracy
            })
    
    # 按正确率排序（低的在前）
    weakness_list.sort(key=lambda x: x['accuracy'])
    
    return weakness_list, tag_stats

def generate_learning_suggestions(weakness_list, week_problems):
    """生成学习建议"""
    suggestions = []
    
    # 薄弱知识点建议
    if weakness_list:
        weakest = weakness_list[:3]  # 最薄弱的 3 个
        suggestions.append("### 🔴 薄弱知识点")
        for w in weakest:
            if w['accuracy'] < 50:
                suggestions.append(f"- **{w['tag']}**: 正确率 {w['accuracy']:.0f}% ({w['solved']}/{w['total']})，建议重点练习")
            elif w['accuracy'] < 70:
                suggestions.append(f"- **{w['tag']}**: 正确率 {w['accuracy']:.0f}% ({w['solved']}/{w['total']})，可以加强")
    
    # 难度建议
    difficulty_dist = defaultdict(int)
    for p in week_problems:
        difficulty_dist[p.get('difficulty', '未知')] += 1
    
    suggestions.append("\n### 📊 难度建议")
    if difficulty_dist.get('简单', 0) > difficulty_dist.get('中等', 0) * 2:
        suggestions.append("- 简单题占比较高，建议增加中等难度题目")
    if difficulty_dist.get('困难', 0) > 0:
        suggestions.append("- 有挑战困难题，保持这个节奏！")
    if difficulty_dist.get('中等', 0) > 5:
        suggestions.append("- 中等题练习充足，可以尝试困难题")
    
    # 数量建议
    total = len(week_problems)
    suggestions.append("\n### 📈 刷题量建议")
    if total < 5:
        suggestions.append(f"- 本周 {total} 道题，建议下周增加到 10 道以上")
    elif total < 10:
        suggestions.append(f"- 本周 {total} 道题，保持这个节奏！")
    elif total < 20:
        suggestions.append(f"- 本周 {total} 道题，非常棒！继续保持")
    else:
        suggestions.append(f"- 本周 {total} 道题，刷题狂魔！注意劳逸结合")
    
    # 前瞻性指导
    suggestions.append("\n### 🎯 下周学习重点")
    
    if weakness_list:
        top_weak = weakness_list[0]['tag']
        suggestions.append(f"1. **重点突破**: {top_weak}")
        suggestions.append(f"   - 找 3-5 道 {top_weak} 相关题目练习")
        suggestions.append(f"   - 复习相关知识点和解题模板")
    
    suggestions.append("2. **保持节奏**: 每天至少 1 道题")
    suggestions.append("3. **复习错题**: 重做本周错题")
    suggestions.append("4. **总结模板**: 整理解题模板和技巧")
    
    return suggestions

def generate_weekly_report(week_problems, week_start_str, week_end_str):
    """生成周报"""
    # 基础统计
    total_count = len(week_problems)
    solved_count = sum(1 for p in week_problems if '通过' in p.get('current_status', ''))
    
    # 难度分布
    difficulty_dist = defaultdict(int)
    for p in week_problems:
        difficulty_dist[p.get('difficulty', '未知')] += 1
    
    # 每日分布
    daily_dist = defaultdict(int)
    for p in week_problems:
        for sub in p.get('week_submissions', []):
            day = sub['date'].split()[0]
            daily_dist[day] += 1
    
    # 薄弱知识点分析
    weakness_list, tag_stats = analyze_weaknesses(week_problems)
    
    # 生成报告
    report = f"""# 📊 LeetCode 学习周报

**周期**: {week_start_str} 至 {week_end_str}
**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

## 📈 本周概览

| 指标 | 数值 |
|------|------|
| 做题总数 | {total_count} 道 |
| 通过 | ✅ {solved_count} 道 |
| 未通过 | ❌ {total_count - solved_count} 道 |
| 通过率 | {solved_count/total_count*100:.1f}% (如有题目) |
| 提交总次数 | {sum(len(p.get('week_submissions', [])) for p in week_problems)} 次 |

---

## 📅 每日分布

| 日期 | 做题数 |
|------|--------|
"""
    
    # 生成本周每天的统计
    from datetime import date
    start = datetime.strptime(week_start_str, "%Y-%m-%d").date()
    for i in range(7):
        day = start + timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        weekday = day.strftime("%A")
        count = daily_dist.get(day_str, 0)
        bar = "🟩" * min(count, 5)  # 最多 5 个方块
        report += f"| {day_str} ({weekday}) | {count} {bar} |\n"
    
    report += f"""
---

## 📚 难度分布

| 难度 | 数量 | 占比 |
|------|------|------|
| 简单 | {difficulty_dist.get('简单', 0)} | {difficulty_dist.get('简单', 0)/max(total_count,1)*100:.1f}% |
| 中等 | {difficulty_dist.get('中等', 0)} | {difficulty_dist.get('中等', 0)/max(total_count,1)*100:.1f}% |
| 困难 | {difficulty_dist.get('困难', 0)} | {difficulty_dist.get('困难', 0)/max(total_count,1)*100:.1f}% |

---

## 🏷️ 知识点分布

| 知识点 | 题目数 | 通过数 | 正确率 |
|--------|--------|--------|--------|
"""
    
    sorted_tags = sorted(tag_stats.items(), key=lambda x: -x[1]['total'])
    for tag, stats in sorted_tags[:10]:  # 前 10 个
        accuracy = stats['solved'] / stats['total'] * 100 if stats['total'] > 0 else 0
        report += f"| {tag} | {stats['total']} | {stats['solved']} | {accuracy:.0f}% |\n"
    
    report += "\n---\n\n## 🔍 薄弱知识点分析\n\n"
    
    if weakness_list:
        report += "| 知识点 | 题目数 | 通过 | 未通过 | 正确率 | 建议 |\n"
        report += "|--------|--------|------|--------|--------|------|\n"
        
        for w in weakness_list[:5]:  # 最薄弱的 5 个
            if w['accuracy'] < 50:
                suggestion = "🔴 重点练习"
            elif w['accuracy'] < 70:
                suggestion = "🟡 加强"
            else:
                suggestion = "🟢 保持"
            
            report += f"| {w['tag']} | {w['total']} | {w['solved']} | {w['failed']} | {w['accuracy']:.0f}% | {suggestion} |\n"
    else:
        report += "*本周做题数量不足，暂无法分析*\n"
    
    report += "\n---\n\n## 💡 学习建议\n\n"
    
    suggestions = generate_learning_suggestions(weakness_list, week_problems)
    report += "\n".join(suggestions)
    
    report += f"""

---

## 📝 本周题目详情

"""
    
    for i, p in enumerate(week_problems, 1):
        status_icon = "✅" if '通过' in p.get('current_status', '') else "❌"
        report += f"### {i}. {p['title']}\n\n"
        report += f"- **难度**: {p.get('difficulty', '未知')}\n"
        report += f"- **状态**: {status_icon} {p.get('current_status', '未知')}\n"
        report += f"- **最佳用时**: {p.get('best_runtime', 'N/A')}\n"
        
        if p.get('tags'):
            report += f"- **知识点**: {', '.join(p['tags'])}\n"
        
        if p.get('week_submissions'):
            report += f"- **本周提交**: {len(p['week_submissions'])} 次\n"
        
        report += "\n"
    
    report += f"""---

## 🎯 下周目标

- [ ] 重点突破薄弱知识点：**{weakness_list[0]['tag'] if weakness_list else '待定'}**
- [ ] 完成至少 10 道题目
- [ ] 保持每天刷题习惯
- [ ] 复习本周错题
- [ ] 总结解题模板

---

*报告由 LeetCode Wrong Notes Skill 自动生成*
"""
    
    return report

def main():
    """主函数"""
    print("=" * 50)
    print("LeetCode 每周学习分析")
    print("=" * 50)
    
    # 解析题目
    filepath = get_monthly_file()
    print(f"读取做题记录：{filepath}")
    
    problems = parse_problems_from_file(filepath)
    print(f"找到 {len(problems)} 道题目")
    
    # 筛选本周的提交
    week_problems, week_start_str, week_end_str = filter_week_submissions(problems)
    print(f"本周提交：{len(week_problems)} 道题")
    
    if not week_problems:
        print("⚠️ 本周暂无记录")
        return
    
    # 生成报告
    ensure_dir()
    report_path = get_weekly_report_path()
    
    report = generate_weekly_report(week_problems, week_start_str, week_end_str)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 周报已生成：{report_path}")
    print("=" * 50)

if __name__ == "__main__":
    main()
