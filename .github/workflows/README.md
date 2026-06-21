# GitHub Actions 工作流说明

本目录包含用于自动化检查和维护的 GitHub Actions 工作流。

## 📋 工作流列表

### 1. check-links.yml
**链接检查工作流**

**触发条件**：
- Push 到 main 分支
- Pull Request 到 main 分支
- 手动触发（workflow_dispatch）

**功能**：
- 检查所有 Markdown 文件中的内部链接有效性
- 检查图片链接是否存在
- 使用 `markdown-link-check` 工具进行链接验证

**配置文件**：`.markdown-link-check.json`

**注意事项**：
- 某些链接可能因为网络问题或权限问题无法访问，工作流会继续执行（continue-on-error: true）
- 图片链接检查会验证相对路径的图片文件是否存在

---

### 2. format-check.yml
**文档质量检查工作流**

**触发条件**：Push / PR 到 main、手动触发

**功能**（通过 `tools/check/`）：
- 叶子文档必填字段（关键词、标签）
- 图片引用存在性
- UTF-8 编码、行尾空格、`?raw=true` 警告
- 图片资源审计（缺失/ orphan / 大文件，警告不阻断）

**依赖**：`tools/check/requirements.txt`（PyYAML、Pillow）

---

### 3. generate-index.yml
**索引生成工作流**

**触发条件**：
- Push 到 main 分支，且 `mds/` 目录下的文件有变更
- 工作流文件本身有变更
- 手动触发（workflow_dispatch）

**功能**：
- 自动扫描 `mds/` 目录结构
- 生成 `INDEX.md` 文档索引
- 自动提交更新到仓库

**生成内容**：
- 按能力模块分类的文档索引（1-6 大模块）
- 专题内容索引
- 统计信息（文档数量、最后更新时间）
- 使用建议
- 自动更新 [KEYWORDS.md](../../KEYWORDS.md) 关键词索引

**权限要求**：
- 需要 `contents: write` 权限以提交更改

**注意事项**：
- 索引文件会自动更新，无需手动维护
- 如果索引文件无变化，不会创建新的提交
- 提交信息包含 `[skip ci]` 以避免触发其他工作流

---

## 🔧 配置说明

### markdown-link-check.json
链接检查工具的配置文件，包含：
- 忽略模式（如 localhost、GitHub 仓库链接等）
- 替换模式（将相对路径转换为 GitHub 链接）
- HTTP 请求头配置
- 超时和重试设置

### 工作流权限
- `check-links.yml`: 默认权限（只读）
- `format-check.yml`: 默认权限（只读）
- `generate-index.yml`: 需要 `contents: write` 权限

---

## 📊 工作流状态

工作流运行状态可以在以下位置查看：
- GitHub 仓库的 "Actions" 标签页
- Pull Request 的检查状态
- 工作流运行摘要

---

## 🐛 故障排除

### 链接检查失败
- 检查链接是否可访问
- 确认图片文件是否存在
- 查看工作流日志了解具体错误

### 格式检查失败
- 查看工作流日志了解具体问题
- 修复格式问题后重新提交
- 使用编辑器插件自动修复格式

### 索引生成失败
- 检查 `mds/` 目录结构是否正确
- 确认工作流有写入权限
- 查看工作流日志了解具体错误

---

## 💡 最佳实践

1. **提交前检查**：在提交 PR 前，建议在本地运行格式检查
2. **修复警告**：虽然某些检查不会阻止合并，但建议修复所有警告
3. **定期更新**：索引文件会自动更新，无需手动维护
4. **查看日志**：如果工作流失败，查看详细日志了解原因

---

## 📚 相关资源

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [markdown-link-check 文档](https://github.com/tcort/markdown-link-check)
- [Markdown 格式规范](https://www.markdownguide.org/)

---

*最后更新：2024年*

