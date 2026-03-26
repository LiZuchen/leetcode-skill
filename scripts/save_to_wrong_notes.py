#!/usr/bin/env python3
"""
LeetCode 做题记录保存脚本
将题目信息保存到本地 Markdown 做题记录文件
"""

import os
import sys
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

def save_problem(title, difficulty, description, code, error_reason, url=""):
    """
    保存题目到做题记录
    
    Args:
        title: 题目名称
        difficulty: 难度 (简单/中等/困难)
        description: 题目描述
        code: 代码内容
        error_reason: 错误原因或备注
        url: 题目链接（可选）
    """
    ensure_dir()
    filepath = get_monthly_file()
    
    lang = detect_language(code)
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    
    content = f"""# {title}

- **难度**：{difficulty}
- **日期**：{date_str}
- **链接**：{url}
- **备注**：{error_reason}

## 题目描述

{description}

## 我的代码

```{lang}
{code}
```

## 正确答案

（待补充）

## 笔记

（待补充）

---
"""
    
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            existing = f.read()
            if f"# {title}\n" in existing or f"# {title} " in existing:
                print(f"[WARN] 题目 '{title}' 已存在于做题记录中")
                return False
    
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[SUCCESS] 题目 '{title}' 已保存到：{filepath}")
    return True

def main():
    if len(sys.argv) < 5:
        print("用法：")
        print("  python save_to_wrong_notes.py <题目名称> <难度> <题目描述> <代码> [错误原因] [URL]")
        print("示例：")
        print("  python save_to_wrong_notes.py \"两数之和\" \"简单\" \"给定一个整数数组...\" \"def twoSum...\" \"哈希表没想到\" \"https://leetcode.cn/problems/two-sum/\"")
        sys.exit(1)
    
    title = sys.argv[1]
    difficulty = sys.argv[2]
    description = sys.argv[3]
    code = sys.argv[4]
    error_reason = sys.argv[5] if len(sys.argv) > 5 else "待补充"
    url = sys.argv[6] if len(sys.argv) > 6 else ""
    
    save_problem(title, difficulty, description, code, error_reason, url)

if __name__ == "__main__":
    main()
