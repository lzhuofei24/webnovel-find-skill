# 书评数据库扫描

书评平台备份可以把模糊找书转化为可枚举的候选筛选，但任何单一备份都有覆盖缺口。使用前核对来源、许可、访问条件、文件结构和更新时间；不要将数据库文件放入 skill 包或公开仓库。

## 可用备份与引用

以下是可用于研究和复现的公开来源。它们由第三方发布，不是本仓库作者制作，也不代表优书网的完整历史数据。下载前请查看源仓库的许可证、发布说明和当前可用性。

1. HeliumOctahelide，[*yousuu-database*：SQLite release](https://github.com/HeliumOctahelide/yousuu-database/releases/tag/sqlite)，提供书目与评论的 SQLite 归档。引用格式：`HeliumOctahelide. yousuu-database, sqlite release. GitHub. 访问日期：YYYY-MM-DD.`
2. Leonerd，[*Chinese Net Novel Rating*](https://www.kaggle.com/datasets/leonerd/chinesenetnovelrating)，Kaggle 数据集，包含书目与评分评论 CSV。其公开下载页也可通过 [Kaggle API 数据集端点](https://www.kaggle.com/api/v1/datasets/download/leonerd/chinesenetnovelrating) 获取。引用格式：`Leonerd. Chinese Net Novel Rating. Kaggle. 访问日期：YYYY-MM-DD.`
3. [Heywhale 数据集页面](https://www.heywhale.com/mw/dataset/5da59acdc83fb40042035ce4/file) 是上述 2019 年数据的另一个可访问页面。使用该页面下载时，应同时注明页面 URL、文件名和访问日期。

本仓库只保存处理方法和来源链接，不重新分发上述数据库文件。研究记录中请同时保存下载 URL、访问日期、文件 SHA-256（如有）、实际 schema、原始记录数和筛选配置，以便他人区分原始数据与后处理结果。

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
