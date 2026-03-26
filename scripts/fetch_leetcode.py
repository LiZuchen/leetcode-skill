#!/usr/bin/env python3
"""
LeetCode 题目抓取脚本
从指定的 LeetCode URL 抓取题目信息并保存到做题记录
支持更新已有题目的提交历史
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import re

# 做题记录目录（可配置）
NOTES_DIR = os.environ.get("LEETCODE_NOTES_DIR", r"<USER_DIR>/Documents/leetcode")

def ensure_dir():
    """确保做题记录目录存在"""
    os.makedirs(NOTES_DIR, exist_ok=True)

def get_monthly_file():
    """获取当前月份的做题记录文件路径"""
    now = datetime.now()
    filename = f"leetcode-notes-{now.year}-{now.month:02d}.md"
    return os.path.join(NOTES_DIR, filename)

def detect_language(code):
    """简单检测代码语言"""
    code_lower = code.lower()
    if 'public class' in code_lower or 'public static void' in code_lower:
        return 'java'
    elif 'func ' in code or 'package ' in code:
        return 'go'
    elif 'import ' in code and ('std::' in code or '#include' in code):
        return 'cpp'
    elif 'def ' in code or 'import ' in code:
        return 'python'
    elif 'function ' in code or 'const ' in code or 'let ' in code:
        return 'javascript'
    elif 'var ' in code or '=>' in code:
        return 'javascript'
    else:
        return 'python'  # 默认

def fetch_leetcode_problem(url):
    """
    从 LeetCode URL 抓取题目信息
    
    Args:
        url: LeetCode 题目页面 URL
    
    Returns:
        dict: 包含题目信息的字典
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] 抓取页面失败：{e}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 提取题目信息
    problem = {
        'title': '',
        'difficulty': '',
        'description': '',
        'url': url,
        'status': '',
        'runtime': '',
        'memory': '',
    }
    
    # 提取题目名称（从 title 标签或页面内容）
    title_tag = soup.find('title')
    if title_tag:
        title_text = title_tag.get_text().strip()
        # 清理标题格式："560. 和为 K 的子数组 - 力扣（LeetCode）"
        match = re.match(r'(\d+\.\s*.+?)\s*[-–]', title_text)
        if match:
            problem['title'] = match.group(1).strip()
        else:
            problem['title'] = title_text.replace('- 力扣（LeetCode）', '').replace('- LeetCode', '').strip()
    
    # 提取难度（从页面内容中查找）
    difficulty_keywords = ['简单', '中等', '困难', 'Easy', 'Medium', 'Hard']
    for kw in difficulty_keywords:
        if kw in response.text:
            problem['difficulty'] = kw
            break
    
    # 尝试提取测试结果
    # 查找"通过"、"解答错误"、"超出时限"等状态
    status_keywords = [
        ('通过', '[OK]'),
        ('解答错误', '[ERR]'),
        ('超出时限', '[TLE]'),
        ('内存溢出', '[MLE]'),
        ('执行出错', '[ERR]'),
    ]
    
    has_status = False
    for status_text, icon in status_keywords:
        if status_text in response.text:
            problem['status'] = f"{icon} {status_text}"
            has_status = True
            break
    
    # 尝试提取执行用时和内存（多种格式）
    runtime_patterns = [
        r'执行用时 [：:]\s*(\d+)\s*ms',
        r'执行用时 [：:]\s*(\d+)\s*毫秒',
        r'(\d+)\s*ms\s*击败',
    ]
    for pattern in runtime_patterns:
        runtime_match = re.search(pattern, response.text)
        if runtime_match:
            problem['runtime'] = f"{runtime_match.group(1)} ms"
            break
    
    memory_patterns = [
        r'内存消耗 [：:]\s*(\d+\.\d+)\s*MB',
        r'内存消耗 [：:]\s*(\d+)\s*MB',
        r'(\d+\.\d+)\s*MB\s*击败',
    ]
    for pattern in memory_patterns:
        memory_match = re.search(pattern, response.text)
        if memory_match:
            problem['memory'] = f"{memory_match.group(1)} MB"
            break
    
    # 检测提交结果并判断状态（通过测试用例数量）
    test_match = re.search(r'(\d+)\s*/\s*(\d+)\s*个通过的测试用例', response.text)
    
    if test_match:
        passed = int(test_match.group(1))
        total = int(test_match.group(2))
        
        if passed == total and not has_status:
            # 全部通过但没有明确状态文本
            problem['status'] = "[OK] 通过"
            has_status = True
        elif passed < total and not has_status:
            # 只通过部分 → 解答错误
            problem['status'] = f"[ERR] 解答错误 ({passed}/{total})"
            has_status = True
        
        has_submission_result = True
    else:
        has_submission_result = False
    
    # 如果没有找到具体状态，但有"已解答"且没有提交结果，说明是题目页面而非提交结果页面
    if not has_status and '已解答' in response.text and not has_submission_result:
        print(f"[SKIP] 检测到'已解答'题目页面，但没有提交结果，跳过记录")
        return None
    
    # 提取题目描述
    # 尝试提取示例
    examples = []
    example_pattern = r'示例\s*\d+[^\n]*\n(.+?)(?=示例|提示|输入：|$)'
    example_matches = re.findall(example_pattern, response.text, re.DOTALL)
    if example_matches:
        examples = [m.strip() for m in example_matches[:2]]
    
    # 提取题目正文
    text_content = soup.get_text(separator='\n', strip=True)
    
    # 简化处理：使用找到的示例
    if examples:
        problem['description'] = '\n\n'.join(examples)
    else:
        # 备用：提取前 1000 字
        problem['description'] = text_content[:1000] + '...' if len(text_content) > 1000 else text_content
    
    return problem

def parse_existing_file(filepath):
    """解析现有文件，返回题目字典"""
    if not os.path.exists(filepath):
        return {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    problems = {}
    # 匹配题目块
    pattern = r'(# \d+\.\s*.+?\n.*?)(?=\n# \d+\.\s*|$)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for match in matches:
        title_match = re.match(r'# (\d+\.\s*.+?)\n', match)
        if title_match:
            title = title_match.group(1).strip()
            problems[title] = match
    
    return problems

def save_or_update_problem(problem, code, note=""):
    """
    保存或更新题目到做题记录
    
    Args:
        problem: 题目信息字典
        code: 代码内容
        note: 备注信息
    """
    ensure_dir()
    filepath = get_monthly_file()
    
    lang = detect_language(code) if code else "python"
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M")
    date_str = now.strftime("%Y-%m-%d")
    
    # 状态图标
    status = problem.get('status', '')
    # 如果状态已经包含图标（如 [OK] 通过），则不再添加
    if status.startswith('['):
        status_icon = status.split(']')[0] + ']'
    else:
        status_icon = "[OK]" if "通过" in status else "[ERR]" if "错误" in status else "[TLE]"
    if not status:
        status = "待完成"
        status_icon = "[TODO]"
    
    runtime = problem.get('runtime', 'N/A')
    memory = problem.get('memory', 'N/A')
    
    # 检查是否已存在
    problems = parse_existing_file(filepath)
    title = problem['title']
    
    if title in problems:
        # 更新现有题目
        old_block = problems[title]
        
        # 更新状态（如果新状态更好）
        if "通过" in status and "当前状态" in old_block:
            old_block = re.sub(
                r'\*\*当前状态\*\*：.*',
                f'**当前状态**：{status_icon} {status}',
                old_block
            )
            # 更新最佳用时
            if runtime and runtime != "N/A" and "最佳用时" in old_block:
                old_block = re.sub(
                    r'\*\*最佳用时\*\*：.*',
                    f'**最佳用时**：{runtime}',
                    old_block
                )
        
        # 添加提交历史
        if "## 提交历史" in old_block:
            history_match = re.search(r'(## 提交历史\n\n\| 日期 \| 状态 \| 用时 \| 内存 \| 备注 \|\n\|------\|------\|------\|------\|------\|\n)', old_block)
            if history_match:
                new_row = f"| {timestamp} | {status_icon} {status} | {runtime} | {memory} | {note} |\n"
                insert_pos = history_match.end()
                old_block = old_block[:insert_pos] + new_row + old_block[insert_pos:]
        else:
            history_section = f"""
## 提交历史

| 日期 | 状态 | 用时 | 内存 | 备注 |
|------|------|------|------|------|
| {timestamp} | {status_icon} {status} | {runtime} | {memory} | {note} |
"""
            desc_match = re.search(r'(## 题目描述\n.*?)(\n## )', old_block, re.DOTALL)
            if desc_match:
                old_block = old_block[:desc_match.end()-3] + history_section + old_block[desc_match.end()-3:]
        
        # 添加代码版本
        if code and code != "# 待补充代码":
            code_section = f"""
### {timestamp} ({status})

```{lang}
{code}
```
"""
            if "## 代码版本" in old_block:
                old_block += code_section + "\n"
            elif "## 我的代码" in old_block:
                code_match = re.search(r'(## 我的代码\n.*?```.*?```)', old_block, re.DOTALL)
                if code_match:
                    old_block = old_block[:code_match.end()] + "\n" + code_section + old_block[code_match.end():]
        
        problems[title] = old_block
        
        # 重建文件内容
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 找到并替换整个块
        pattern = r'# ' + re.escape(title.split('. ')[1] if '. ' in title else title) + r'.*?(?=\n# \d+\.\s*|$)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            content = content[:match.start()] + old_block + content[match.end():]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[UPDATE] 题目 '{title}' 已更新提交记录")
        return True
    else:
        # 创建新题目
        content = f"""# {title}

- **难度**：{problem.get('difficulty', '未知')}
- **首次日期**：{date_str}
- **链接**：{problem.get('url', '')}
- **当前状态**：{status_icon} {status}
- **最佳用时**：{runtime if runtime and runtime != "N/A" else "待更新"}

## 题目描述

{problem.get('description', '（待补充）')}

## 提交历史

| 日期 | 状态 | 用时 | 内存 | 备注 |
|------|------|------|------|------|
| {timestamp} | {status_icon} {status} | {runtime} | {memory} | {note} |

## 代码版本

### {timestamp} ({status})

```{lang}
{code if code else "# 待补充代码"}
```

## 笔记

（待补充）

---

"""
        
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[NEW] 题目 '{title}' 已添加到做题记录")
        return True

def read_from_html_file(html_path):
    """从本地 HTML 文件读取题目信息"""
    if not os.path.exists(html_path):
        print(f"[ERROR] 文件不存在：{html_path}")
        return None
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    problem = {
        'title': '',
        'difficulty': '',
        'description': '',
        'url': '',
        'status': '',
        'runtime': '',
        'memory': '',
    }
    
    # 提取标题
    title_tag = soup.find('title')
    if title_tag:
        title_text = title_tag.get_text().strip()
        match = re.match(r'(\d+\.\s*.+?)\s*[-–]', title_text)
        if match:
            problem['title'] = match.group(1).strip()
        else:
            problem['title'] = title_text.replace('- 力扣（LeetCode）', '').replace('- LeetCode', '').strip()
    
    # 提取难度
    difficulty_keywords = ['简单', '中等', '困难', 'Easy', 'Medium', 'Hard']
    for kw in difficulty_keywords:
        if kw in html:
            problem['difficulty'] = kw
            break
    
    # 提取状态
    status_keywords = [
        ('通过', '✅'),
        ('解答错误', '❌'),
        ('超出时限', '⏱️'),
    ]
    for status_text, icon in status_keywords:
        if status_text in html:
            problem['status'] = f"{icon} {status_text}"
            break
    
    # 提取示例
    examples = []
    example_pattern = r'示例\s*\d+[^\n]*\n(.+?)(?=示例|提示|输入：|$)'
    example_matches = re.findall(example_pattern, html, re.DOTALL)
    if example_matches:
        examples = [m.strip() for m in example_matches[:2]]
        problem['description'] = '\n\n'.join(examples)
    else:
        text_content = soup.get_text(separator='\n', strip=True)
        problem['description'] = text_content[:1000] if len(text_content) > 1000 else text_content
    
    return problem

def main():
    if len(sys.argv) < 2:
        print("用法：")
        print("  方式 1 (URL): python fetch_leetcode.py <URL> [备注] [代码文件路径]")
        print("  方式 2 (本地 HTML): python fetch_leetcode.py --html <HTML 文件路径> [备注] [代码文件路径]")
        print("示例：")
        print("  python fetch_leetcode.py https://leetcode.cn/problems/word-search/ DFS 回溯第一次做 C:\\code\\sol.py")
        print("  python fetch_leetcode.py --html page.html 前缀和没想到 solution.py")
        sys.exit(1)
    
    # 解析参数
    if sys.argv[1] == '--html':
        html_path = sys.argv[2]
        note = sys.argv[3] if len(sys.argv) > 3 else ""
        code_file = sys.argv[4] if len(sys.argv) > 4 else None
        url = ""
        
        print(f"[READ] 正在读取本地文件：{html_path}")
        problem = read_from_html_file(html_path)
        
        if not problem:
            print("[ERROR] 读取失败")
            sys.exit(1)
    else:
        url = sys.argv[1]
        note = sys.argv[2] if len(sys.argv) > 2 else ""
        code_file = sys.argv[3] if len(sys.argv) > 3 else None
        
        # 抓取题目信息
        print(f"[FETCH] 正在抓取：{url}")
        problem = fetch_leetcode_problem(url)
        
        if not problem:
            print("[ERROR] 抓取失败，请尝试手动保存页面为 HTML 后使用 --html 参数")
            print("[HINT] 在浏览器中按 Ctrl+S 保存页面为 HTML 文件")
            sys.exit(1)
    
    print(f"[INFO] 题目：{problem['title']}")
    print(f"[INFO] 难度：{problem['difficulty']}")
    print(f"[INFO] 状态：{problem.get('status', '未知')}")
    
    # 读取代码文件
    code = ""
    if code_file and os.path.exists(code_file):
        with open(code_file, 'r', encoding='utf-8') as f:
            code = f.read()
    else:
        code = "# 待补充代码"
    
    # 保存或更新到做题记录
    save_or_update_problem(
        problem=problem,
        code=code,
        note=note
    )

if __name__ == "__main__":
    main()
