# LeetCode 做题记录技能

## 📖 功能说明

从 LeetCode 题目页面自动抓取题目信息和提交记录，保存到本地 Markdown 文件。**不仅记录错题，所有做过的题目都会保存**，并自动跟踪每次提交历史。

### 核心特性

- ✅ **自动记录**：HEARTBEAT 每 30 秒检查浏览器，检测到提交自动保存
- ✅ **手动触发**：说"保存"、"记录"等关键词立即检查
- ✅ **每日分析**：每天 23:00 自动生成学习日报
- ✅ **每周分析**：每周日 20:00 生成周报，识别薄弱知识点
- ✅ **全题目记录**：不仅错题，所有做过的题目都保存
- ✅ **提交历史**：自动跟踪每次提交的状态、用时、内存
- ✅ **智能判断**：正确识别通过/解答错误/部分通过
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

### 方式 3：查看学习报告

```bash
# 生成今日日报
python scripts/daily_analysis.py

# 生成本周周报
python scripts/weekly_analysis.py
```

**日报位置**: `<USER_DIR>/Documents/leetcode/reports/daily-report-YYYY-MM-DD.md`

**周报位置**: `<USER_DIR>/Documents/leetcode/reports/weekly-report-YYYY-Www.md`

---

## 📁 文件结构

```
leetcode-wrong-notes/
├── SKILL.md                    # 技能说明
├── README.md                   # 本文档
└── scripts/
    ├── fetch_leetcode.py       # 主脚本：抓取并保存
    ├── record_submission.py    # 记录单次提交
    ├── save_to_wrong_notes.py  # 手动保存辅助
    ├── daily_analysis.py       # 每日学习分析
    └── weekly_analysis.py      # 每周学习分析
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

## 📈 学习报告

### 每日分析（每天 23:00 自动生成）

**包含内容**：
- 📊 今日概览（做题数、通过率）
- 📚 难度分布（简单/中等/困难）
- 🏷️ 知识点分布（数组/链表/树等）
- 📝 题目详情
- 💡 学习建议

**示例**：
```markdown
# 📊 LeetCode 学习日报

**日期**: 2026-03-26 (Wednesday)

## 📈 今日概览
| 指标 | 数值 |
|------|------|
| 做题总数 | 5 道 |
| 通过 | ✅ 4 道 |
| 未通过 | ❌ 1 道 |
| 通过率 | 80.0% |

## 💡 学习建议
- ⚠️ 今天有 1 道题未通过，建议复习错题
- 📖 今天重点练习了 **数组** (3 题)
- 🔥 今天刷题量不错，继续保持！
```

### 每周分析（每周日 20:00 自动生成）

**包含内容**：
- 📊 本周概览（做题总数、提交次数）
- 📅 每日分布（热力图）
- 📚 难度分布
- 🏷️ 知识点分布
- 🔍 薄弱知识点分析（正确率排序）
- 💡 学习建议 + 下周目标
- 📝 本周题目详情

**示例**：
```markdown
# 📊 LeetCode 学习周报

**周期**: 2026-03-24 至 2026-03-30

## 🔍 薄弱知识点分析
| 知识点 | 题目数 | 通过 | 未通过 | 正确率 | 建议 |
|--------|--------|------|--------|--------|------|
| 动态规划 | 5 | 2 | 3 | 40% | 🔴 重点练习 |
| 回溯 | 3 | 1 | 2 | 33% | 🔴 重点练习 |
| 数组 | 8 | 7 | 1 | 88% | 🟢 保持 |

## 🎯 下周学习重点
1. **重点突破**: 动态规划
   - 找 3-5 道动态规划相关题目练习
   - 复习相关知识点和解题模板
2. **保持节奏**: 每天至少 1 道题
3. **复习错题**: 重做本周错题
```

---

## ⚙️ 配置说明

### HEARTBEAT 配置

编辑 `HEARTBEAT.md`：

```markdown
# LeetCode 自动记录 + 学习分析

## 任务
### 1. 自动记录（每 30 秒）
- 检查浏览器中的 LeetCode 题目页面
- 检测页面中的测试结果变化
- 自动记录每次提交

### 2. 每日分析（每天 23:00）
- 分析当天的做题情况
- 生成学习日报

### 3. 每周分析（每周日 20:00）
- 分析一周的做题情况
- 识别薄弱知识点
- 给出学习建议

## 触发关键词
### 记录题目
- "保存"
- "记录"
- "提交"

### 查看报告
- "今日总结"
- "本周总结"
- "我的薄弱点"
- "学习建议"
```

### 环境变量（可选）

```bash
# 自定义做题记录目录
set LEETCODE_NOTES_DIR=C:\Users\<USERNAME>\Documents\leetcode
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

### Q: 日报和周报什么时候生成？
A: 
- **日报**：每天 23:00 自动生成
- **周报**：每周日 20:00 自动生成
- 也可以手动运行 `daily_analysis.py` 和 `weekly_analysis.py`

### Q: 薄弱知识点是如何识别的？
A: 系统会统计每个知识点的做题数量和正确率，正确率低于 50% 的标记为"重点练习"，50%-70% 的标记为"加强"。

### Q: 部分通过的测试用例会如何记录？
A: 会正确标记为"解答错误"，并显示具体通过数量，例如 `[ERR] 解答错误 (50/100)`。

### Q: "已解答"页面会被记录吗？
A: 
- **题目页面**（只有"已解答"，没有测试用例数据）→ 跳过
- **提交结果页面**（有"XX/XX 个通过的测试用例"）→ 记录

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

**功能**：
- ✅ 自动识别题目名称、难度
- ✅ 提取提交状态（通过/解答错误/超出时限）
- ✅ 提取执行用时和内存
- ✅ 智能判断：全部通过 vs 部分通过
- ✅ 更新已有题目的提交历史

### record_submission.py

记录单次提交（更新已有题目）。

```bash
# 用法
python record_submission.py <URL> <状态> <用时> [内存] [代码文件路径] [备注]

# 示例
python record_submission.py "https://leetcode.cn/problems/xxx/" "解答错误" "N/A" "N/A" "C:\\code\\wrong.py" "边界条件没处理"
```

### daily_analysis.py

生成每日学习报告。

```bash
# 用法
python daily_analysis.py

# 输出
reports/daily-report-YYYY-MM-DD.md
```

### weekly_analysis.py

生成每周学习报告，识别薄弱知识点。

```bash
# 用法
python weekly_analysis.py

# 输出
reports/weekly-report-YYYY-Www.md
```

---

## 📝 日志文件

| 文件 | 路径 | 说明 |
|------|------|------|
| **做题记录** | `<USER_DIR>/Documents/leetcode/leetcode-notes-YYYY-MM.md` | 按月组织的做题记录 |
| **状态缓存** | `<USER_DIR>/Documents/leetcode/leetcode-state.json` | 避免重复记录的状态缓存 |
| **日报** | `<USER_DIR>/Documents/leetcode/reports/daily-report-YYYY-MM-DD.md` | 每日学习报告 |
| **周报** | `<USER_DIR>/Documents/leetcode/reports/weekly-report-YYYY-Www.md` | 每周学习报告 |

---

## 🔄 更新日志

### v1.2 - 2026-03-26
- ✅ 修复：正确判断部分通过的测试用例（显示 `解答错误 (50/100)`）
- ✅ 修复："已解答"页面不再被错误跳过
- ✅ 优化：通过测试用例数量推断提交状态
- ✅ 清理：移除无用的后台监听进程和日志

### v1.1 - 2026-03-26
- ✅ 新增：每日学习分析（`daily_analysis.py`）
- ✅ 新增：每周学习分析（`weekly_analysis.py`）
- ✅ 新增：薄弱知识点识别
- ✅ 新增：前瞻性学习建议
- ✅ 新增：学习报告自动生成

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
