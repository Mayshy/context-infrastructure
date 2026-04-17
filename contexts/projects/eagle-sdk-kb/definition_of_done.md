# Definition of Done — Poros (Eagle SDK)

> Poros 所有子模块（poros-common / poros-client / poros-high-level-client / poros-service / poros-elasticsearch-plugin / poros-java-api-client）的验收标准。
> AI 完成任何开发任务前，必须对照本文件确认是否满足对应标准。

---

## 标准验收流程

### 第一步：打包 SNAPSHOT

```bash
mvn deploy -DskipTests
```

**版本号必须向用户（华雨）索取，AI 绝不能自行决定版本号。**

打包产物为 SNAPSHOT 版本，发布到内部 Maven 仓库。

### 第二步：TestEagleClient 集成测试

在项目 `TestEagleClient` 中引用上一步打出的 SNAPSHOT 包，运行相关测试，验证功能符合预期。

---

## 例外情况

`poros-elasticsearch-plugin`（ES 插件模块）**不适用**上述标准：

`TestEagleClient` 接入 ES5 需要较大改造，当前未完成。涉及该模块的改动，验收方式需单独与华雨确认。

---

## 注意事项

- 版本号是强依赖，缺少版本号时必须暂停并询问，不得用占位符或递增猜测。
- `mvn deploy` 会推送到远程仓库，执行前确认版本号和改动范围无误。
