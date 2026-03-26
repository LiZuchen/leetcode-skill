# LeetCode 做题记录技能

## 📖 功能说明

从 LeetCode 题目页面自动抓取题目信息和提交记录，保存到本地 Markdown 文件。**不仅记录错题，所有做过的题目都会保存**，并自动跟踪每次提交历史。

### 核心特性

- ✅ **自动记录**：HEARTBEAT 每 30 秒检查浏览器，检测到提交自动保存
- ✅ **手动触发**：说"保存"、"记录"等关键词立即检查
- ✅ **全题目记录**：不仅错题，所有做过的题目都保存
- ✅ **提交历史**：自动跟踪每次提交的状态、用时、内存
- ✅ **去重机制**：相同提交不会重复记录
- ✅ **支持 Edge/Chrome**：通过 Browser Relay 扩展连接浏览器

---

## 🚀 快速开始

### 前提条件

1. **安装依赖**
```bash
pip install requests beautifulsoup4
```

2. **配置浏览器**
- Edge 或 Chrome 浏览器
- 安装 OpenClaw Browser Relay 扩展
- 确保扩展图标为 🟢 ON 状态

3. **启动浏览器（Edge 示例）**
```bash
"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=18792 --user-data-dir="C:\\Users\\<USERNAME>\\AppData\\Local\\OpenClaw\\EdgeCDP"
```

---

## 📝 使用方式

### 方式 1：自动记录（推荐）

1. 在浏览器中打开 LeetCode 题目页面
2. 点击"提交"或"运行"按钮
3. 等待页面显示结果
4. **最多 30 秒后自动保存**（HEARTBEAT 检测）

**或者手动触发**：
- 提交后说："保存"、"记录"、"提交"
- 立即检查并记录（0 秒延迟）

### 方式 2：脚本抓取

```bash
# 基本用法
python scripts/fetch_leetcode.py <URL> [备注] [代码文件路径]

# 示例
python scripts/fetch_leetcode.py "https://leetcode.cn/problems/word-search/" "DFS 回溯第一次做" "C:\\code\\solution.py"
```

### 方式 3：Browser 读取

通过 OpenClaw browser tool 读取当前页面：
```
browser snapshot profile="chrome"
```

---

## 📁 文件结构

```
leetcode-wrong-notes/
├── SKILL.md                    # 技能说明
├── README.md                   # 本文档
└── scripts/
    ├── fetch_leetcode.py       # 主脚本：抓取并保存
    ├── record_submission.py    # 记录单次提交
    └── save_to_wrong_notes.py  # 手动保存辅助
```

---

## 📊 记录格式

保存的文件位于：`<USER_DIR>/Documents/leetcode/leetcode-notes-YYYY-MM.md`

### 示例

```markdown
# 560. 和为 K 的子数组

- **难度**: 中等
- **首次日期**: 2026-03-24
- **链接**: https://leetcode.cn/problems/subarray-sum-equals-k/
- **当前状态**: ✅ 已通过
- **最佳用时**: 51 ms

## 提交历史

| 日期 | 状态 | 用时 | 内存 | 备注 |
|------|------|------|------|------|
| 2026-03-26 11:41 | ✅ 通过 | 51 ms | 23.09 MB | 前缀和 + 哈希表，第一次做对 |
| 2026-03-24 | ❌ 解答错误 | N/A | N/A | 使用了动态规划方法，思路错误 |

## 代码版本

### 2026-03-26 11:41 (通过)

```python
class Solution:
    def subarraySum(self, nums: List[int], k: int) -> int:
        cur=0
        rec = defaultdict(int)
        rec[0]=1
        res=0
        for i in range(0,len(nums)):
            cur+=nums[i]
            res+=rec[cur-k]
            rec[cur]+=1
        return res
```

## 笔记

- 这题的关键是理解前缀和的性质
- 用哈希表记录每个前缀和出现的次数
- 时间复杂度：O(n)，空间复杂度：O(n)
```

---

## ⚙️ 配置说明

### HEARTBEAT 配置

编辑 `HEARTBEAT.md`：

```markdown
# LeetCode 自动记录

## 任务
- **每 30 秒检查**浏览器中的 LeetCode 题目页面
- 检测页面中的测试结果变化
- **自动记录每次提交**，不需要用户手动触发
- 用户说"保存"、"记录"等关键词时**立即检查**

## 检查频率
- **有 LeetCode 页面时**: 每 30 秒检查一次
- **无 LeetCode 页面时**: 每 2 分钟检查一次
- **手动触发时**: 立即检查

## 触发关键词
- "保存"
- "记录"
- "提交"
- "记一下"
- "保存这道题"
```

### 浏览器配置

**Edge 浏览器**：
```bash
"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" \
  --remote-debugging-port=18792 \
  --user-data-dir="C:\\Users\\<USERNAME>\\AppData\\Local\\OpenClaw\\EdgeCDP"
```

**Chrome 浏览器**：
```bash
"C:\Program Files\Google\Chrome\Application\chrome.exe" \
  --remote-debugging-port=18792 \
  --user-data-dir="C:\\Users\\<USERNAME>\\AppData\\Local\\OpenClaw\\ChromeCDP"
```

---

## 🔍 常见问题

### Q: 为什么抓取被阻止（403 Forbidden）？
A: LeetCode 有反爬虫机制。本技能通过浏览器读取页面（使用你的登录状态），不会触发反爬虫。不要直接用 requests 抓取 LeetCode URL。

### Q: 如何查看已记录的题目？
A: 打开 `<USER_DIR>/Documents/leetcode/leetcode-notes-YYYY-MM.md` 文件。

### Q: 如何避免重复记录？
A: 脚本会自动检测相同 URL+ 状态 + 代码的组合，30 秒冷却时间内不会重复记录。

### Q: 提交后多久会被记录？
A: 
- **自动记录**：最多 30 秒（HEARTBEAT 轮询）
- **手动触发**：立即（说"保存"等关键词）

### Q: 切换题目会丢失记录吗？
A: 如果在 30 秒内切换，可能错过。建议提交后说"保存"，立即记录。

---

## 🛠️ 脚本说明

### fetch_leetcode.py

主脚本，用于抓取 LeetCode 页面并保存。

```bash
# 用法
python fetch_leetcode.py <URL> [备注] [代码文件路径]

# 示例
python fetch_leetcode.py "https://leetcode.cn/problems/xxx/" "前缀和没想到" "C:\\code\\solution.py"
```

### record_submission.py

记录单次提交（更新已有题目）。

```bash
# 用法
python record_submission.py <URL> <状态> <用时> [内存] [代码文件路径] [备注]

# 示例
python record_submission.py "https://leetcode.cn/problems/xxx/" "解答错误" "N/A" "N/A" "C:\\code\\wrong.py" "边界条件没处理"
```

---

## 📝 日志文件

| 文件 | 路径 | 说明 |
|------|------|------|
| **做题记录** | `<USER_DIR>/Documents/leetcode/leetcode-notes-YYYY-MM.md` | 按月组织的做题记录 |
| **状态缓存** | `<USER_DIR>/Documents/leetcode/leetcode-state.json` | 避免重复记录的状态缓存 |

---

## 🔄 更新日志

### v1.0 - 2026-03-26
- ✅ 基础功能：抓取 LeetCode 页面并保存
- ✅ 自动记录：HEARTBEAT 每 30 秒检查
- ✅ 手动触发：关键词立即检查
- ✅ 提交历史：跟踪每次提交
- ✅ 去重机制：避免重复记录
- ✅ 精简架构：移除后台监听进程

---

## 📞 联系

问题反馈：在 GitHub Issues 中提出

---

## 📄 许可证

MIT License
