# 学城文档索引

**学城根目录**: https://km.sankuai.com/collabpage/1127183403  
**创建日期**: 2026-04-07

---

## 已完成摘要

| 文档 | contentId | 状态 | 本地文件 |
|------|-----------|------|---------|
| Java API 客户端-Poros Java API（ES8） | 2293336777 | ✅ 完成 | `poros_java_api_client.md` |
| Arts 客户端 | 1235632053 | ✅ 完成 | `arts_client.md` |
| ES7 客户端兼容 ES8 | 2131195847 | ✅ 完成 | `es7_compat_es8.md` |
| 客户端性能测试 | 2542107392 | ⚠️ 学城原文为空页 | `performance_test.md` |
| 客户端特性说明 | 1560978827 | ⚠️ 学城原文为空页 | `client_features.md` |
| 实验性 Poros 客户端（Snapshot 版本） | 1201253124 | ✅ 完成 | `snapshot_client.md` |
| 日志客户端 | 2727344046 | ⚠️ 学城原文为空页 | `log_client.md` |

---

## 注意

- 3 篇文档（性能测试/特性说明/日志客户端）学城原文为空页，摘要文件仅记录从代码和其他文档推断的信息
- Arts 客户端详细信息已移入 `arts_client.md`

---

## Arts 客户端关键信息（从学城 1235632053 提取，详见 arts_client.md）

**两个版本并存**：

| 版本 | 底层依赖 | 最新版本 | 特点 |
|------|---------|---------|------|
| v1 | poros-high-level-client | ES_0.4.22 | 支持慢查询模板限流和高风险 query 拦截 |
| v2 | poros-java-api-client | 6.0.1 | 更轻量，支持 ES7 和 ES8，**不支持**慢查询模板限流和高风险 query 拦截 |

**v1 Maven 依赖**：
```xml
<groupId>com.dp.arts</groupId>
<artifactId>arts-client</artifactId>
```

**poros-high-level-client 直接依赖**：
```xml
<groupId>com.sankuai.meituan</groupId>
<artifactId>poros-high-level-client</artifactId>
```

**Release Note**: https://km.sankuai.com/collabpage/2726292659

---

## 维护规则

| 触发事件 | 动作 |
|----------|------|
| 读完一篇学城文档 | AI 生成摘要 → 存入本目录 `{name}.md` |
| 学城文档更新 | 更新对应摘要文件，更新 INDEX.md 中状态 |
