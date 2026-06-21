# 文档与图片检查工具

本地与 CI 共用的质量检查脚本，配置见 [tools/config.yaml](../config.yaml)。

## 安装

```bash
pip install -r tools/check/requirements.txt
```

## 脚本

| 脚本 | 用途 |
|------|------|
| [check_docs.py](check_docs.py) | 必填字段（关键词/标签）、图片存在性、UTF-8、`?raw=true` 警告 |
| [check_images.py](check_images.py) | 缺失引用、未引用图片、大文件列表；`--compress` 优化 PNG |
| [generate_keywords.py](generate_keywords.py) | 生成根目录 [KEYWORDS.md](../../KEYWORDS.md) |

## 用法

```bash
# 仓库根目录执行
python tools/check/check_docs.py
python tools/check/check_images.py
python tools/check/generate_keywords.py
```

## CI 集成

- [format-check.yml](../../.github/workflows/format-check.yml) — 运行 `check_docs.py`、`check_images.py`
- [generate-index.yml](../../.github/workflows/generate-index.yml) — 索引更新后运行 `generate_keywords.py`

## 相关文档

- [文档命名规范](../../docs/文档命名规范.md)
- [内容审核清单](../../docs/内容审核清单.md)
- [CONTRIBUTING.md](../../CONTRIBUTING.md)
