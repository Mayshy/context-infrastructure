# BestPractice: 外部系统集成前的 KB 验证

## When to Use

任何涉及以下场景时，必须触发此 best practice：

- 调用下游服务 API（REST/RPC/消息队列）
- 实现字段映射（本地字段 → 外部系统字段）
- 依赖第三方服务行为（响应格式、错误码、幂等性）
- 为外部系统构建 payload 或 schema

## 核心规则

**先查 KB，再写代码。不能假设字段名存在或有效。**

失败案例（已发生）：实现 pontos approvers 字段时，未查 worksheet 子服务文档，不知道下游是否支持该字段，直接实现后被用户指出逻辑错误。

## 步骤

1. **定位 KB**：查 `rules/WORKSPACE.md` 活跃项目路由，找到对应服务的 KB 本地路径
2. **查 API 契约**：读取 KB 中该子服务的 design.md 或 API 文档，确认：
   - 字段名和类型
   - 必填/可选
   - 枚举值范围
   - 请求/响应格式
3. **有疑问时问用户**：KB 文档缺失或不确定时，先问，不要猜

## KB 路径速查

- DataMatrix（pontos/athena/hermes/kugget/worksheet）：`~/.config/opencode/contexts/projects/datamatrix-kb/01_services/<service>/`
- Poros：`~/.config/opencode/contexts/projects/poros-kb/01_modules/<module>/`

## 为什么重要

外部系统 API 契约是实现的真正边界。没有它，任何实现都是在猜测。猜测的代价：返工、用户信任损失、潜在的生产事故。
