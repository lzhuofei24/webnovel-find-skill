# 书评数据库扫描

书评平台备份可以把模糊找书转化为可枚举的候选筛选，但任何单一备份都有覆盖缺口。使用前核对来源、许可、访问条件、文件结构和更新时间；不要将数据库文件放入 skill 包或公开仓库。

## 数据准备

优先寻找包含作品 ID、书名、作者、分类或标签、简介、目录链接、状态和字数的书目数据；评论数据至少需要作品 ID、评论 ID、正文和时间。不同来源的 ID 规则可能不同，必须从实际字段或 URL 证实连接关系。

合并多个来源时保留原始来源和冲突记录。相同评论跨库出现时按规范化正文哈希去重，不增加证据强度。

## 扫描器

`scripts/scan_reviews.py` 只使用 Python 标准库，读取 SQLite 或 CSV，输出 `candidates.json` 与 `coverage.json`。字段变化时应显式失败并先调整适配，不要静默丢弃记录。

运行格式：

    python <skill-path>/scripts/scan_reviews.py --sqlite <database.sqlite> --old-dir <csv-directory> --config <clues.json> --out <output-directory>

配置中的 `clues` 是线索列表，每个线索有 `id`、`weight` 和 `groups`；同一线索内所有正则都要匹配同一条文本。下面只展示占位格式，不包含任何具体作品线索：

    {"clues":[{"id":"线索 A","weight":12,"groups":["关键词 A1|同义词 A1","关键词 A2|同义词 A2"]},{"id":"线索 B","weight":10,"groups":["关键词 B1|同义词 B1","关键词 B2|同义词 B2"]}],"candidate_when":[["线索 A"],["线索 B"]]}

扫描结果只表示评论或元数据出现了相关词，必须回到目录、章节或可靠原文来源逐项核验。
