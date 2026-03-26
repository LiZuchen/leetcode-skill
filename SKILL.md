---
name: leetcode-wrong-notes
description: 从 LeetCode 网页爬取题目和代码，整理到本地做题记录 Markdown 文件。支持 Chrome/Edge 浏览器，自动记录每次提交，跟踪做题进度和提交历史。
---

# LeetCode 做题记录技能

## 功能

从 LeetCode 题目页面爬取题目信息，整理到本地 Markdown 做题记录。**不仅记录错题，所有做过的题目都会保存**，并自动跟踪每次提交历史。支持 **Chrome 和 Edge 浏览器**。

### 浏览器支持

- **Edge**（推荐）: 使用 `profile="chrome"`，CDP 端口 18792
- **Chrome**: 使用 `profile="chrome"`，CDP 端口 18792

> **注意**: 需要将浏览器重启并添加 `--remote-debugging-port=18792` 参数，Browser Relay 扩展才能正常工作。详见 README.md。

## 触发场景

当用户提到以下关键词时触发：
- "LeetCode 题目"
- "保存这道题"
- "记录做题"
- "爬取 LeetCode"
- "记录题目"
- "更新提交"
- "保存"
- "记录"
- "提交"

## 工作流程

### 方式 A：自动检测（推荐）

HEARTBEAT 自动检查浏览器中的 LeetCode 页面，检测到提交时自动记录：
1. 定期检查 Chrome/Edge 浏览器标签页（每 30 秒）
2. 检测 LeetCode 页面（leetcode.cn/problems/）
3. 提取测试结果和代码
4. 自动保存到做题记录

### 方式 B：脚本抓取

1. 用户提供 LeetCode 题目 URL
2. 运行脚本抓取页面：
```bash
python scripts/fetch_leetcode.py <URL> [备注] [代码文件路径]
```
3. 脚本自动提取题目信息并保存到做题记录

### 方式 C：Browser 读取

1. 使用 `browser snapshot` 读取当前 LeetCode 页面内容
2. 提取字段（题目名称、难度、状态、代码、测试结果）
3. 保存到做题记录，自动记录提交历史

## 做题记录格式

```markdown
# 79. 单词搜索

- **难度**：中等
- **首次日期**：2026-03-26
- **链接**：https://leetcode.cn/problems/word-search/
- **当前状态**：✅ 已通过
- **最佳用时**：0 ms

## 题目描述

（题目内容）

## 提交历史

| 日期 | 状态 | 用时 | 内存 | 备注 |
|------|------|------|------|------|
| 2026-03-26 11:34 | ✅ 通过 | 0 ms | - | 第一次做，DFS 回溯 |

## 代码版本

### 2026-03-26 11:34 (通过)

```python
class Solution:
    def exist(self, board: List[List[str]], word: str) -> bool:
        # 代码内容
```

## 笔记

（待补充）

---
```

## 脚本使用

### 方式 1：抓取 URL 并保存

```bash
# 基本用法
python scripts/fetch_leetcode.py <URL> [备注] [代码文件路径]

# 示例
python scripts/fetch_leetcode.py "https://leetcode.cn/problems/word-search/" "已通过" "C:\\code\\solution.py"
```

### 方式 2：记录提交（更新已有题目）

```bash
python scripts/record_submission.py <URL> <状态> <用时> <内存> [代码文件路径] [备注]

# 示例
python scripts/record_submission.py "https://leetcode.cn/problems/word-search/" "解答错误" "N/A" "N/A" "C:\\code\\wrong.py" "边界条件没处理好"
```

## 自动记录

HEARTBEAT 会定期检查浏览器中的 LeetCode 页面：
- 检测到测试结果变化时自动记录提交
- 首次通过的题目自动保存
- 解答错误的题目自动保存并标记

## 注意事项

1. 首次运行需要安装依赖：`pip install requests beautifulsoup4`
2. 做题记录自动按月组织文件：`leetcode-notes-2026-03.md`
3. 支持 LeetCode 中国（leetcode.cn）和国际版（leetcode.com）
4. 代码可以手动提供或从文件读取
5. 如果题目已存在，会**更新提交历史**而不是跳过
