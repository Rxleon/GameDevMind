# 用 Cursor 设计 GM 后台 RBAC 权限模型

> **一句话总结：** GM 后台「运营能改别人号、客服能看全服流水」的权限灾难，靠 AI 帮忙梳理 RBAC 模型很快，但「谁能审批高危操作」必须人定——AI 默认给所有人 admin。

---

## 背景

我们 SLG 要自建 GM 后台（Go + Vue），功能包括：查号、发道具、封禁、改活动配置、查流水。团队 3 个运营、5 个客服、2 个策划，之前用 Excel 登记「谁可以点哪个按钮」，已经失控两次（实习生误发全服邮件）。

我用 Cursor 设计 RBAC，目标：**角色-权限-资源三元模型 + 高危操作二次审批**。

---

## 对话记录

### 第一轮：描述需求

> **我：**
> ```
> 游戏 GM 后台需要 RBAC。功能：查玩家、发道具、封禁、改活动表、导出流水。
> 角色：运营、客服、策划、超级管理员。
> 技术栈 Go + Vue，请设计数据库表结构和 API 鉴权中间件思路。
> ```

> **Cursor（摘要）：**
>
> 给出经典四表模型：
> - `users` / `roles` / `permissions` / `role_permissions`
> - 中间件：JWT 解析 → 查用户角色 → 查 permission code → 403
> - 权限码示例：`player:read`, `item:grant`, `ban:execute`, `activity:write`, `finance:export`

方向正确，但**把所有 write 权限都默认赋给了「运营」**，包括 `activity:write`（改活动表）和 `item:grant`（无上限发道具）。

---

### 第二轮：补充业务约束

> **我：**
> ```
> 修正：
> 1. 客服只能 player:read + ban:execute（仅禁言，不能封号）
> 2. 运营可以 item:grant 但单次上限 1000 钻石，超额要走审批
> 3. 改 activity 表只有策划 + 超管
> 4. finance:export 需要超管 + 操作日志留存 180 天
> 5. 所有写操作要 audit_log
> ```

> **Cursor（摘要）：**
>
> 扩展设计：
> - `permissions` 加 `resource` + `action` + `conditions`（JSON，如 `{"max_diamond":1000}`）
> - 新增 `approval_requests` 表：超额发道具创建 pending 审批，超管 approve 后执行
> - `audit_logs`：who / what / when / ip / payload_hash
> - 中间件链：`Auth → RBAC → ConditionCheck → Audit`

**我的修正：** AI 建议审批流用「任意超管 approve」，我们改成**双超管或运营主管 + 超管**，防止单人滥权。

---

### 第三轮：生成 Go 鉴权骨架

> **我：**
> ```
> 用 Go 写一个 RBAC 中间件骨架：
> - permission code 从 route 注解读取
> - 支持 conditions 校验（发道具数量）
> - 返回统一 403 JSON
> ```

AI 生成的 `RequirePermission("item:grant")` + `CheckGrantLimit(userID, amount)` 框架可直接落地，我补了 Redis 缓存角色权限（TTL 5min，变更时 pub/sub 失效）。

---

## 最终成果

- 四表 + 审批表 + audit 表上线
- 误操作工单从月均 4 单降到 0
- 所有高危操作可追溯，合规审计通过

---

## 关键收获

1. **先列「谁绝对不能做什么」**，比列「谁能做什么」更安全
2. AI 擅长 CRUD 型 RBAC 脚手架，**审批链、上限、双因素**必须人补
3. GM 后台和游戏服要**分权限域**，GM 账号泄露不能等于游戏服 root

---

## 图谱知识点映射

- [6.2.1 GM后台](../mds/6.运营能力/6.2.1.GM后台.md)
- [6.3.1 游戏安全](../mds/6.运营能力/6.3.1.游戏安全.md)
- [3.2.4 服务端基础功能](../mds/3.研发能力/3.2.4.服务端基础功能.md)
