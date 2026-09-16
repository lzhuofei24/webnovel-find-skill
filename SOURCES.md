# 数据来源与引用

本仓库中的扫描器可以处理公开的书评平台备份。下面列出示例数据来源；来源由第三方维护，本仓库不声称拥有这些数据，也不保证链接永久有效。

| 来源 | 内容 | 建议引用 |
| --- | --- | --- |
| [HeliumOctahelide/yousuu-database SQLite release](https://github.com/HeliumOctahelide/yousuu-database/releases/tag/sqlite) | 书目与评论 SQLite 归档 | HeliumOctahelide. *yousuu-database*, sqlite release. GitHub. 访问日期：YYYY-MM-DD. |
| [Leonerd/Chinese Net Novel Rating](https://www.kaggle.com/datasets/leonerd/chinesenetnovelrating) | 书目与评分评论 CSV | Leonerd. *Chinese Net Novel Rating*. Kaggle. 访问日期：YYYY-MM-DD. |
| [Heywhale 数据集页面](https://www.heywhale.com/mw/dataset/5da59acdc83fb40042035ce4/file) | 另一处公开数据集页面 | Heywhale 数据集页面，文件名与访问日期：YYYY-MM-DD. |

## 复现记录

不要把完整数据库直接提交到仓库。使用者应在本地保存下载文件，并记录：

- 下载 URL、访问日期和文件名；
- SHA-256 校验值（如适用）；
- 实际表结构和原始记录数；
- 使用的线索配置、脚本版本和输出目录；
- 去重规则、人工核验范围和正文来源。

这样可以明确区分第三方原始数据、脚本生成的候选结果和人工确认的剧情证据。
