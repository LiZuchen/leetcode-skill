#!/usr/bin/env python3
"""
LeetCode 提交记录脚本
记录每次提交到做题记录，支持更新已有题目的提交历史
"""

import os
import sys
import re
from datetime import datetime
from pathlib import Path

# 做题记录目录（可配置）
NOTES_DIR = os.environ.get("LEETCODE_NOTES_DIR", r"<USER_DIR>\Documents\leetcode")

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

def extract_problem_slug(url):
    """从 URL 提取题目 slug"""
    match = re.search(r'/problems/([^/]+)/', url)
    if match:
        return match.group(1)
    return None

def parse_existing_file(filepath):
    """解析现有文件，返回题目列表和内容"""
    if not os.path.exists(filepath):
        return {}, ""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    problems = {}
    pattern = r'(# \d+\.\s*.+?\n.*?)(?=\n# \d+\.\s*|$)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for match in matches:
        title_match = re.match(r'# (\d+\.\s*.+?)\n', match)
        if title_match:
            title = title_match.group(1).strip()
            problems[title] = match
    
    return problems, content

def update_or_create_problem(filepath, title, difficulty, url, status, runtime, memory, code, note=""):
    """更新或创建题目记录"""
    ensure_dir()
    
    problems, existing_content = parse_existing_file(filepath)
    
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M")
    date_str = now.strftime("%Y-%m-%d")
    lang = detect_language(code) if code else "python"
    
    status_icon = "✅" if "通过" in status else "❌" if "错误" in status else "⏱️"
    
    if title in problems:
        old_block = problems[title]
        
        if "通过" in status and "当前状态" in old_block:
            old_block = re.sub(
                r'\*\*当前状态\*\*：.*',
                f'**当前状态**：{status_icon} {status}',
                old_block
            )
            if runtime and runtime != "N/A" and "最佳用时" in old_block:
                old_block = re.sub(
                    r'\*\*最佳用时\*\*：.*',
                    f'**最佳用时**：{runtime}',
                    old_block
                )
        
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
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pattern = r'# ' + re.escape(title.split('. ')[1] if '. ' in title else title) + r'.*?(?=\n# \d+\.\s*|$)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            content = content[:match.start()] + old_block + content[match.end():]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[UPDATE] 题目 '{title}' 已更新提交记录")
        return True
    else:
        content = f"""# {title}

- **难度**：{difficulty}
- **首次日期**：{date_str}
- **链接**：{url}
- **当前状态**：{status_icon} {status}
- **最佳用时**：{runtime if runtime and runtime != "N/A" else "待更新"}

## 题目描述

（待补充）

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

def main():
    if len(sys.argv) < 4:
        print("用法：")
        print("  python record_submission.py <URL> <状态> <用时> [内存] [代码文件路径] [备注]")
        print("示例：")
        print("  python record_submission.py https://leetcode.cn/problems/word-search/ 已通过 0ms 16MB C:\\code\\sol.py DFS 回溯")
        print("  python record_submission.py https://leetcode.cn/problems/xxx/ 解答错误 N/A N/A C:\\code\\wrong.py 边界条件没处理")
        sys.exit(1)
    
    url = sys.argv[1]
    status = sys.argv[2]
    runtime = sys.argv[3]
    memory = sys.argv[4] if len(sys.argv) > 4 else "N/A"
    code_file = sys.argv[5] if len(sys.argv) > 5 else None
    note = sys.argv[6] if len(sys.argv) > 6 else ""
    
    slug = extract_problem_slug(url)
    title = slug.replace('-', ' ').title() if slug else "未知题目"
    difficulty = "未知"
    
    code = ""
    if code_file and os.path.exists(code_file):
        with open(code_file, 'r', encoding='utf-8') as f:
            code = f.read()
    
    filepath = get_monthly_file()
    update_or_create_problem(
        filepath=filepath,
        title=title,
        difficulty=difficulty,
        url=url,
        status=status,
        runtime=runtime,
        memory=memory,
        code=code,
        note=note
    )

if __name__ == "__main__":
    main()
