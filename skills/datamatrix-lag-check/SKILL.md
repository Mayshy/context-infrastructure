---
name: datamatrix-lag-check
description: "DataMatrix 建模应用积压快速诊断。给定建模应用名（processName），查询其近 1h 所有消费组的积压量（MSS 建模层 + Mirror pontos 层），判断是否有积压及积压在哪个消费组。触发词：积压、backlog、消费组积压、建模应用积压、查一下 xxx 积压、xxx 有没有积压。"
allowed-tools:
  - Bash
---

# DataMatrix 建模应用积压诊断

给定建模应用名（`processName`），快速判断近 1h 是否有积压，以及积压在哪个消费组。

## 重要限制

- **时间范围：近 1h（每分钟一个点，共 60 个点）**
- Flink 消费组不向 Mafka SDK 上报 offset，因此 `mafka-cli` 的 `backlog`/`clients`/`offset` 命令对 DataMatrix 消费组**无效**（全返回 -1），不要使用
- 积压数据来源：DataMatrix API 的 `msgReadyRows`（底层是 Mafka `messageReadyAndRate` 接口）

## 执行步骤

### Step 1：获取数据源列表

```bash
curl -s "https://datamatrix.sankuai.com/hermes/api/v1/process/realtimeRunInfo?processName={processName}" \
  -H 'PORTAL-PROXY-USER: eyJsb2dpbiI6InNoZW5odWF5dSJ9'
```

返回字段：
- `processState`：任务状态（正常状态 / 异常）
- `datasourceList`：数据源名称列表
- `rtJobLink`：Flink 任务链接

**如果 `processState` 不是"正常状态"，直接报告任务异常，不需要继续查积压。**

### Step 2：并行查询每个数据源的积压

对每个数据源并行调用：

```bash
curl -s "https://datamatrix.sankuai.com/hermes/api/v1/process/realtimeRunInfo/dataSourceRealtimeInfo?processName={processName}&datasourceName={datasourceName}" \
  -H 'PORTAL-PROXY-USER: eyJsb2dpbiI6InNoZW5odWF5dSJ9'
```

从返回中提取：

| 字段路径 | 含义 |
|---------|------|
| `hermesRealtimeInfo.topic` | MSS 层消费的 topic |
| `hermesRealtimeInfo.consumerGroup` | MSS 层消费组名 |
| `hermesRealtimeInfo.msgReadyRows` | MSS 层近 1h 积压量（每分钟，按机房） |
| `pontosRealtimeInfo.topic` | Mirror 层消费的 topic（DM-DTS-* 开头） |
| `pontosRealtimeInfo.consumerGroup` | Mirror 层消费组名 |
| `pontosRealtimeInfo.msgReadyRows` | Mirror 层近 1h 积压量 |

### Step 3：计算积压量

对每个 `msgReadyRows`，每个时间点的总积压 = 所有机房（列）的值之和：

```python
# msgReadyRows 格式示例：
# [{"time": "15:30", "yg-mafka2-octo": 0, "hh-mafka2-octo": 0}, ...]

idcs = [col for col in msgReadyColumns if col != "time"]
time_lags = [(row["time"], sum(row.get(idc, 0) or 0 for idc in idcs)) for row in msgReadyRows]
current_lag = time_lags[-1][1]  # 最新一分钟
peak_lag = max(lag for _, lag in time_lags)
peak_time = next(t for t, lag in time_lags if lag == peak_lag)
```

### Step 4：输出报告

```
{processName} 积压报告（近 1h，查询时间: HH:MM）
Flink 任务状态: 正常 / 异常

数据源                    层级    当前积压    1h峰值    峰值时刻  状态
─────────────────────────────────────────────────────────────────
exhibit_snapshot          MSS          0         0     15:30   🟢 正常
exhibit_snapshot          Mirror       0         0     15:30   🟢 正常
...

结论: 近 1h 无积压 / 存在积压（详见上表）
```

**积压判定阈值：**
- `peak > 100,000`：🔴 严重积压
- `peak > 10,000`：🟡 轻微积压
- `peak ≤ 10,000`：🟢 正常

## 常见问题

### msgReadyRows 为空或全为 0
- 可能是数据源刚创建，Mafka 监控还没有数据
- 可能是该消费组近 1h 没有消息生产（正常）

### 任务状态异常但无积压
- Flink 任务可能已停止，但 topic 里也没有新消息，所以积压为 0
- 需要结合 `rtJobLink` 到 Flink 控制台确认任务状态

### 需要查超过 1h 的积压
- **当前没有接口支持**。Flink 消费组不向 Mafka 上报 offset，所有积压监控接口（Mafka API、mafka-cli、DataMatrix API）的底层都是同一个 `messageReadyAndRate` 接口，只有近 1h 数据
- 替代方案：查看 Mafka 控制台页面 `mafka.mws.sankuai.com` 的积压图（手动查看）

## 鉴权说明

DataMatrix API 使用 Portal 代理鉴权：
```
PORTAL-PROXY-USER: eyJsb2dpbiI6InNoZW5odWF5dSJ9
```
（base64 解码为 `{"login":"shenhuayu"}`，如换用户需重新生成）

## 示例

```
查一下 mpmctexhibit-merchant-index 的积压
```

按上述步骤执行，输出类似：

```
mpmctexhibit-merchant-index 积压报告（近 1h，查询时间: 16:51）
Flink 任务状态: 正常

数据源                              层级    当前积压    1h峰值  状态
exhibit_relation_snapshot           MSS          0         0   🟢 正常
exhibit_relation_snapshot           Mirror       0         0   🟢 正常
exhibit_audit_info                  MSS          0         0   🟢 正常
exhibit_audit_info                  Mirror       0         0   🟢 正常
exhibit_snapshot                    MSS          0         0   🟢 正常
exhibit_snapshot                    Mirror       0         0   🟢 正常
exhibit_owner                       MSS          0         0   🟢 正常
exhibit_owner                       Mirror       0         0   🟢 正常
exhibit_attribute_snapshot          MSS          0         0   🟢 正常
exhibit_attribute_snapshot          Mirror       0         0   🟢 正常

结论: ✅ 近 1h 无积压，所有消费组正常。
```
