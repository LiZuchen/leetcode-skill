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

# 做题记录目录（可通过环境变量配置，默认使用用户文档目录）
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

def extract_problem_number(url):
    """从 URL 提取题目编号和名称"""
    # 匹配 leetcode.cn/problems/xxx/ 或 leetcode.cn/problems/xxx
    match = re.search(r'/problems/([^/]+)/', url)
    if match:
        slug = match.group(1)
        return slug
    return None

def parse_existing_file(filepath):
    """解析现有文件，返回题目列表和内容"""
    if not os.path.exists(filepath):
        return {}, ""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    problems = {}
    # 匹配题目块：从 # 题目名称 到下一个 ---
    pattern = r'(# \d+\.\s*.+?\n.*?)(?=\n# \d+\.\s*|$)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for match in matches:
        # 提取题目编号
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
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    date_str = now.strftime("%Y-%m-%d")
    lang = detect_language(code) if code else "python"
    
    # 状态图标
    status_icon = "✅" if "通过" in status else "❌" if "错误" in status else "⏱️"
    
    # 检查题目是否已存在
    if title in problems:
        # 更新现有题目
        old_block = problems[title]
        
        # 去重检查：检查是否已存在相同时间戳的记录
        existing_timestamps = re.findall(r'\| (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) \|', old_block)
        if timestamp in existing_timestamps:
            print(f"[SKIP] 题目 '{title}' 在 {timestamp} 已有记录，跳过重复提交")
            return False
        
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
            # 在表格中添加新行
            history_match = re.search(r'(## 提交历史\n\n\| 日期 \| 状态 \| 用时 \| 内存 \| 备注 \|\n\|------\|------\|------\|------\|------\|\n)', old_block)
            if history_match:
                new_row = f"| {timestamp} | {status_icon} {status} | {runtime} | {memory} | {note} |\n"
                insert_pos = history_match.end()
                old_block = old_block[:insert_pos] + new_row + old_block[insert_pos:]
        else:
            # 添加提交历史部分
            history_section = f"""
## 提交历史

| 日期 | 状态 | 用时 | 内存 | 备注 |
|------|------|------|------|------|
| {timestamp} | {status_icon} {status} | {runtime} | {memory} | {note} |
"""
            # 在题目描述后插入
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
            # 在"我的代码"或"代码版本"后插入
            if "## 代码版本" in old_block:
                old_block += code_section + "\n"
            elif "## 我的代码" in old_block:
                # 在"我的代码"部分后添加
                code_match = re.search(r'(## 我的代码\n.*?```.*?```)', old_block, re.DOTALL)
                if code_match:
                    old_block = old_block[:code_match.end()] + "\n" + code_section + old_block[code_match.end():]
        
        # 更新题目块
        problems[title] = old_block
        
        # 重建文件内容
        new_content = existing_content
        # 找到旧块的位置并替换
        old_escaped = re.escape(old_block.split('\n')[0])  # 只匹配标题行
        for key, block in problems.items():
            if key == title:
                # 找到并替换整个块
                pattern = r'# ' + re.escape(title.split('. ')[1] if '. ' in title else title) + r'.*?(?=\n# \d+\.\s*|$)'
                match = re.search(pattern, new_content, re.DOTALL)
                if match:
                    new_content = new_content[:match.start()] + block + new_content[match.end():]
                break
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"[UPDATE] 题目 '{title}' 已更新提交记录")
        return True
    else:
        # 创建新题目
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
        
        # 追加到文件
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
    
    # 从 URL 提取题目信息（简化版，实际应该抓取页面）
    slug = extract_problem_number(url)
    title = slug.replace('-', ' ').title() if slug else "未知题目"
    difficulty = "未知"
    
    # 读取代码文件
    code = ""
    if code_file and os.path.exists(code_file):
        with open(code_file, 'r', encoding='utf-8') as f:
            code = f.read()
    
    # 记录提交
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
