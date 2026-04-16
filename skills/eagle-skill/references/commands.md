# Eagle CLI 命令大全

## SSO 认证管理

```bash
# 登录（自动打开浏览器）- 默认线上环境
eagle sso login

# 登录线下环境
eagle sso login --env test

# 登录海外环境
eagle sso login --env overseas

# 查看登录状态
eagle sso status

# 退出登录
eagle sso logout
```

## 环境管理

```bash
# 查看当前环境（只读）
eagle env show

# 切换环境需重新登录
eagle sso login --env prod     # 线上
eagle sso login --env test     # 线下
eagle sso login --env overseas # 海外
```

## 集群管理命令

### 查看集群列表
```bash
# 列出所有集群
eagle cluster list
eagle cl ls

# 按名称过滤
eagle cluster list -n "esperf"

# 分页查看
eagle cluster list -p 1 -s 20

# 高级列表查询
eagle cluster list-advanced
eagle cl la

# 只获取集群名称列表
eagle cluster name-list
eagle cl nl
```

### 查看集群详情
```bash
# 实时元数据
eagle cluster describe <cluster-name>
eagle cl desc <cluster-name>

# 静态元数据
eagle cluster static <cluster-name>
eagle cl st <cluster-name>

# 容量概况
eagle cluster capacity <cluster-name>
eagle cl cap <cluster-name>

# ES 版本
eagle cluster es-version <cluster-name>
eagle cl ver <cluster-name>

# 集群 Appkey 列表
eagle cluster appkey-list
eagle cl akl

# Falcon 监控 URL
eagle cluster falcon-url <cluster-name>
eagle cl falcon
```

### 查看集群人员
```bash
# 查看 Owner
eagle cluster owner <cluster-name>
eagle cl o <cluster-name>

# 查看 User
eagle cluster user <cluster-name>
eagle cl u <cluster-name>
```

### 查看集群配置
```bash
# 集群配置
eagle cluster configs <cluster-name>
eagle cl cfg <cluster-name>

# 动态配置
eagle cluster dynamic-config <cluster-name>
eagle cl dc <cluster-name>

# 相关 Appkeys
eagle cluster appkeys <cluster-name>
eagle cl app <cluster-name>

# 分词器列表
eagle cluster analyzers <cluster-name>
eagle cl az <cluster-name>
```

### 集群操作日志
```bash
# 查看集群操作日志
eagle cluster op-log <cluster-name>
eagle cl ol <cluster-name>

# 高级操作日志查询
eagle cluster operation-log
eagle cl oplog
```

## 节点管理命令

### 独立节点命令
```bash
# 获取节点列表
eagle node list <cluster>
eagle n ls <cluster>

# 获取节点概览
eagle node overview <cluster>
eagle n ov <cluster>

# 获取节点详情
eagle node detail <cluster> <ip>
eagle n d <cluster> <ip>

# 搜索节点
eagle node search <cluster>
eagle n s <cluster>
```

### 集群节点子命令
```bash
# 查看节点列表
eagle cluster node list <cluster>
eagle cl n ls <cluster>

# 查看节点概览
eagle cluster node overview <cluster>
eagle cl n ov <cluster>

# 查看节点详情
eagle cluster node detail <cluster> <ip>
eagle cl n d <cluster> <ip>
```

## 索引管理命令

### 查看索引列表
```bash
# 列出集群下所有索引（默认只显示我的索引）
eagle index list <cluster-name>
eagle idx ls <cluster-name>

# 显示所有索引（包括他人的）
eagle index list <cluster-name> --all

# 按名称过滤
eagle index list <cluster-name> -n "myindex"

# 按别名过滤
eagle index list <cluster-name> -a "myalias"

# 分页
eagle index list <cluster-name> -p 1 -s 20

# 只获取索引名称列表
eagle index name-list <cluster>
eagle idx nl <cluster>

# 获取原始索引名称列表
eagle index original-name-list <cluster>
eagle idx onl <cluster>
```

### 查看索引详情
```bash
# 基本信息
eagle index describe <cluster> <index>
eagle idx desc <cluster> <index>

# 统计信息
eagle index stats <cluster> <index>
eagle idx st <cluster> <index>

# 段文件信息
eagle index segments <cluster> <index>
eagle idx seg <cluster> <index>

# JSON 完整信息
eagle index json <cluster> <index>
eagle idx j <cluster> <index>

# 元信息
eagle index meta <cluster> <index>
eagle idx m <cluster> <index>

# 监控配置
eagle index monitor <cluster> <index>
eagle idx mon <cluster> <index>
```

### 查看索引字段和类型
```bash
# 字段信息
eagle index fields <cluster> <index>
eagle idx f <cluster> <index>

# 类型信息
eagle index types <cluster> <index>
eagle idx t <cluster> <index>
```

### 查看索引权限
```bash
# 查看权限（默认 MANAGE）
eagle index auth <cluster> <index>

# 指定权限类型
# 可选值：MANAGE / WRITE / READ
eagle index auth <cluster> <index> --type WRITE
eagle index auth <cluster> <index> --type READ

# 查看 Appkey 权限
eagle index appkey-auth <cluster> <index>
eagle idx app <cluster> <index>
```

### 索引操作日志
```bash
# 查看索引操作日志
eagle index log <cluster> <index>
eagle idx lg <cluster> <index>
```

### 创建索引（写操作）
```bash
# 从 JSON 字符串创建
eagle index create <cluster> <index> --source '{"settings":{...}}' --appkeys key1,key2

# 从文件创建
eagle index create <cluster> <index> --file ./index-config.json --appkeys key1,key2

eagle idx c <cluster> <index> --file ./index-config.json --appkeys key1,key2
```

## 索引模板管理

### 查看模板列表
```bash
# 列出集群下所有模板
eagle template list <cluster>
eagle tpl ls <cluster>

# 只获取模板名称列表
eagle template name-list <cluster>
eagle tpl nl <cluster>
```

### 查看模板详情
```bash
# 查看模板元信息
eagle template meta <cluster> <template>
eagle tpl m <cluster> <template>

# 查看模板 JSON
eagle template json <cluster> <template>
eagle tpl j <cluster> <template>

# 查看模板关联索引
eagle template related-indices <cluster> <template>
eagle tpl ri <cluster> <template>

# 查看模板监控信息
eagle template monitor <cluster> <template>
eagle tpl mon <cluster> <template>
```

### 慢日志配置
```bash
# 查看模板慢日志配置
eagle template slowlog-config <cluster>
eagle tpl sc <cluster>
```

### 模板操作日志
```bash
# 查看模板操作日志
eagle template log <cluster> <template>
eagle tpl l <cluster> <template>
```

### 创建模板（写操作）
```bash
# 从 JSON 字符串创建
eagle template create <cluster> <template> --source '{...}' --appkeys key1,key2

# 从文件创建
eagle template create <cluster> <template> --file ./template.json --appkeys key1,key2

# 创建 Composable 模板
eagle template create <cluster> <template> --file ./template.json --appkeys key1,key2 --type COMPOSABLE
```

## 别名管理

```bash
# 列出集群别名
eagle alias name-list <cluster>
eagle al nl <cluster>

# 列出原始别名
eagle alias original-alias-list <cluster>
eagle al oal <cluster>
```

## Appkey 管理

```bash
# 获取 Appkey 权限列表
eagle appkey auth-list
eagle ak al

# 检查 Appkey 是否属于 Eagle
eagle appkey belongs-to-eagle <appkey>
eagle ak bte <appkey>

# 获取 Appkey 关联的集群组
eagle appkey related-cluster-group <appkey>
eagle ak rcg <appkey>

# 获取 Appkey IDC 分布
eagle appkey idc-distribution <appkey>
eagle ak idc <appkey>

# 获取集群关联客户端版本记录
eagle appkey client-version
eagle ak cv
```

## 权限认证

```bash
# 获取 ES 权限列表
eagle auth es-list
eagle auth el

# 获取系统权限列表
eagle auth system-list <resource> <type>
eagle auth sl <resource> <type>
```

## 文档搜索

```bash
# 专家模式搜索（执行原始 ES DSL）
eagle search expert -c <cluster> -i <index>
eagle s e -c <cluster> -i <index>

# 从文件读取查询
eagle search expert -c <cluster> -i <index> -f ./query.json

# Profile 搜索
eagle search profile -c <cluster> -i <index> -q '{"match_all":{}}'
eagle s p -c <cluster> -i <index> -q '{...}'

# 简单搜索
eagle search simple -c <cluster> -i <index> -q "search text"
eagle s s -c <cluster> -i <index> -q "text"

# SQL 搜索
eagle search sql <cluster> -s "SELECT * FROM myindex"
```

## 慢日志管理

```bash
# 获取慢日志节点列表
eagle slowlog node-list <cluster>
eagle sl nl <cluster>

# 获取慢日志列表
eagle slowlog list -c <cluster>
eagle sl ls -c <cluster>

# 获取慢日志详情
eagle slowlog detail -c <cluster> -i <index> --start-time "2024-01-01T00:00:00" --end-time "2024-01-02T00:00:00" --shard-id 0 --slow-log-type INDEX --slow-log-id xxx
eagle sl d -c <cluster> -i <index> ...

# 获取慢日志配置
eagle slowlog config <cluster>
eagle sl cfg <cluster>

# 根据 ID 获取慢日志
eagle slowlog by-id <id>
eagle sl id <id>

# 获取 N 天前的慢日志统计
eagle slowlog n-day-before <cluster> [day]
eagle sl ndb <cluster> 7

# 获取 N 天内的慢日志摘要
eagle slowlog within-n-day <cluster> [day]
eagle sl wnd <cluster> 7
```

## 实时监控

```bash
# 索引实时统计
eagle realtime indices-stats <cluster>
eagle rt is <cluster>

# 指定索引实时统计
eagle realtime indices-stats <cluster> -i index1,index2

# 节点实时统计
eagle realtime node-stats <cluster>
eagle rt ns <cluster>

# Top N 统计
eagle realtime indices-stats <cluster> -t 10
eagle realtime node-stats <cluster> -t 10
```

## 大盘监控

```bash
# 系统指标大盘
eagle dashboard system-metric
eagle db sm

# 服务器概览（时间范围：1=3天, 2=7天, 3=1月, 4=6月, 5=1年）
eagle dashboard server-overview 2
eagle db so 2

# 历史趋势
eagle dashboard history-trend 2
eagle db ht 2

# 资源分布统计
eagle dashboard res-dist 2 <type>
eagle db rd 2 <type>

# 集群状态列表
eagle dashboard cluster-status
eagle db cs
```

## 指标监控

```bash
# 集群监控指标
eagle metrics cluster <cluster>
eagle m cl <cluster>

# 慢查询平均耗时 Top10
eagle metrics slow-query-avg
eagle m sqa

# 查询 QPS 平均 Top10
eagle metrics query-qps-avg
eagle m qqa

# 写入 QPS 平均 Top10
eagle metrics index-qps-avg
eagle m iqa

# 文档数 Top10
eagle metrics top-docs
eagle m td

# 索引数 Top10
eagle metrics top-indices
eagle m ti

# 分片数 Top10
eagle metrics top-shards
eagle m ts

# 磁盘使用率 Top10
eagle metrics disk-usage-percent
eagle m dup

# IO 使用率平均 Top10
eagle metrics io-util-avg
eagle m iua

# 堆内存使用率 Top10
eagle metrics heap-usage-percent
eagle m hup
```

## 诊断分析

```bash
# 获取诊断报告列表
eagle diagnostic reports <cluster>
eagle diag r <cluster>
```

## 常用别名速查

| 完整命令 | 别名 |
|---------|------|
| `eagle cluster list` | `eagle cl ls` |
| `eagle cluster describe` | `eagle cl desc` |
| `eagle cluster static` | `eagle cl st` |
| `eagle cluster capacity` | `eagle cl cap` |
| `eagle cluster owner` | `eagle cl o` |
| `eagle cluster user` | `eagle cl u` |
| `eagle cluster configs` | `eagle cl cfg` |
| `eagle cluster dynamic-config` | `eagle cl dc` |
| `eagle cluster es-version` | `eagle cl ver` |
| `eagle cluster appkeys` | `eagle cl app` |
| `eagle cluster name-list` | `eagle cl nl` |
| `eagle cluster op-log` | `eagle cl ol` |
| `eagle cluster analyzers` | `eagle cl az` |
| `eagle cluster node list` | `eagle cl n ls` |
| `eagle index list` | `eagle idx ls` |
| `eagle index describe` | `eagle idx desc` |
| `eagle index stats` | `eagle idx st` |
| `eagle index segments` | `eagle idx seg` |
| `eagle index json` | `eagle idx j` |
| `eagle index meta` | `eagle idx m` |
| `eagle index fields` | `eagle idx f` |
| `eagle index types` | `eagle idx t` |
| `eagle index appkey-auth` | `eagle idx app` |
| `eagle index name-list` | `eagle idx nl` |
| `eagle index create` | `eagle idx c` |
| `eagle template list` | `eagle tpl ls` |
| `eagle template meta` | `eagle tpl m` |
| `eagle template json` | `eagle tpl j` |
| `eagle template create` | `eagle tpl c` |
| `eagle alias name-list` | `eagle al nl` |
| `eagle node list` | `eagle n ls` |
| `eagle node overview` | `eagle n ov` |
| `eagle node detail` | `eagle n d` |
| `eagle search expert` | `eagle s e` |
| `eagle search profile` | `eagle s p` |
| `eagle search simple` | `eagle s s` |
| `eagle slowlog node-list` | `eagle sl nl` |
| `eagle slowlog list` | `eagle sl ls` |
| `eagle slowlog detail` | `eagle sl d` |
| `eagle slowlog config` | `eagle sl cfg` |
| `eagle realtime indices-stats` | `eagle rt is` |
| `eagle realtime node-stats` | `eagle rt ns` |
| `eagle dashboard system-metric` | `eagle db sm` |
| `eagle dashboard server-overview` | `eagle db so` |
| `eagle metrics cluster` | `eagle m cl` |
| `eagle diagnostic reports` | `eagle diag r` |
| `eagle appkey auth-list` | `eagle ak al` |
| `eagle auth es-list` | `eagle auth el` |
