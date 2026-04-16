# Eagle CLI 使用示例

## 场景 1：查看集群状态

```bash
# 1. 先登录
eagle sso login

# 2. 查看有哪些集群
eagle cluster list | jq '.content[].clusterName'

# 3. 查看指定集群的实时状态
eagle cluster describe eaglenode_esperf | jq '.clusterStatus'

# 4. 查看集群容量
eagle cluster capacity eaglenode_esperf | jq '.usedDiskPercent'

# 5. 查看集群 ES 版本
eagle cluster es-version eaglenode_esperf

# 6. 查看集群节点
eagle cluster node list eaglenode_esperf | jq '.[].nodeName'

# 7. 查看集群分词器
eagle cluster analyzers eaglenode_esperf
```

## 场景 2：排查索引问题

```bash
# 1. 找到集群下的我的索引
eagle index list eaglenode_esperf | jq '.content[].indexName'

# 1.1 查看集群下所有索引（包括他人的）
eagle index list eaglenode_esperf --all | jq '.content[].indexName'

# 2. 查看索引基本信息
eagle index describe eaglenode_esperf myindex_v1

# 3. 查看索引统计（文档数、存储大小）
eagle index stats eaglenode_esperf myindex_v1 | jq '.primaries.docs, .primaries.store'

# 4. 查看索引段文件（排查 merge 问题）
eagle index segments eaglenode_esperf myindex_v1 | jq '.segments | length'

# 5. 查看索引配置
eagle index json eaglenode_esperf myindex_v1 | jq '.settings'

# 6. 查看索引字段映射
eagle index fields eaglenode_esperf myindex_v1 | jq 'keys'

# 7. 查看索引权限
eagle index auth eaglenode_esperf myindex_v1
```

## 场景 3：检查权限

```bash
# 查看谁有集群权限
eagle cluster owner eaglenode_esperf
eagle cluster user eaglenode_esperf

# 查看索引权限
eagle index auth eaglenode_esperf myindex_v1 --type MANAGE
eagle index auth eaglenode_esperf myindex_v1 --type WRITE
eagle index appkey-auth eaglenode_esperf myindex_v1

# 查看 Appkey 权限列表
eagle appkey auth-list
```

## 场景 4：登录和环境切换

```bash
# 正常登录（自动打开浏览器）- 默认线上环境
eagle sso login

# 登录线下环境
eagle sso login --env test

# 登录海外环境（访问欧洲等海外集群）
eagle sso login --env overseas

# 查看当前登录状态
eagle sso status

# 查看当前环境
eagle env show

# 退出登录
eagle sso logout
```

## 场景 5：快速定位索引

```bash
# 按名称模糊搜索索引
eagle index list eaglenode_esperf -n "order" | jq '.content[].indexName'

# 按别名搜索
eagle index list eaglenode_esperf -a "order_alias" | jq '.content[].indexName'

# 获取所有索引名称列表
eagle index name-list eaglenode_esperf
```

## 场景 6：模板管理

```bash
# 列出集群所有模板
eagle template list eaglenode_esperf

# 查看模板元信息
eagle template meta eaglenode_esperf my_template

# 查看模板 JSON 配置
eagle template json eaglenode_esperf my_template

# 查看模板关联的索引
eagle template related-indices eaglenode_esperf my_template

# 查看模板慢日志配置
eagle template slowlog-config eaglenode_esperf
```

## 场景 7：节点管理

```bash
# 查看集群节点列表
eagle node list eaglenode_esperf

# 查看节点概览
eagle node overview eaglenode_esperf

# 查看指定节点详情
eagle node detail eaglenode_esperf 10.0.0.1

# 使用集群子命令查看节点
eagle cluster node list eaglenode_esperf
eagle cluster node overview eaglenode_esperf
```

## 场景 8：慢日志分析

```bash
# 获取慢日志节点列表
eagle slowlog node-list eaglenode_esperf

# 获取慢日志列表
eagle slowlog list -c eaglenode_esperf

# 获取最近 7 天的慢日志统计
eagle slowlog n-day-before eaglenode_esperf 7

# 获取最近 7 天内的慢日志摘要
eagle slowlog within-n-day eaglenode_esperf 7

# 查看慢日志配置
eagle slowlog config eaglenode_esperf
```

## 场景 9：监控大盘

```bash
# 系统指标大盘
eagle dashboard system-metric

# 服务器概览（最近 7 天）
eagle dashboard server-overview 2

# 历史趋势（最近 7 天）
eagle dashboard history-trend 2

# 集群状态列表
eagle dashboard cluster-status

# 集群实时监控
eagle realtime indices-stats eaglenode_esperf
eagle realtime node-stats eaglenode_esperf
```

## 场景 10：指标排行

```bash
# 慢查询平均耗时 Top10
eagle metrics slow-query-avg

# 查询 QPS 平均 Top10
eagle metrics query-qps-avg

# 磁盘使用率 Top10
eagle metrics disk-usage-percent

# 堆内存使用率 Top10
eagle metrics heap-usage-percent

# 查看指定集群指标
eagle metrics cluster eaglenode_esperf
```

## 场景 11：文档搜索

```bash
# 专家模式搜索（执行原始 ES DSL）
eagle search expert -c eaglenode_esperf -i myindex_v1

# 从文件读取查询
eagle search expert -c eaglenode_esperf -i myindex_v1 -f ./query.json

# 简单搜索
eagle search simple -c eaglenode_esperf -i myindex_v1 -q "搜索关键词"

# SQL 搜索
eagle search sql eaglenode_esperf -s "SELECT * FROM myindex_v1 LIMIT 10"
```

## 场景 12：诊断分析

```bash
# 获取集群诊断报告列表
eagle diagnostic reports eaglenode_esperf
```

## 场景 13：创建索引（写操作）

```bash
# 从 JSON 字符串创建索引
eagle index create eaglenode_esperf mynewindex \
  --source '{"settings":{"number_of_shards":3},"mappings":{"properties":{"field1":{"type":"text"}}}}' \
  --appkeys myappkey1,myappkey2

# 从文件创建索引
eagle index create eaglenode_esperf mynewindex \
  --file ./index-config.json \
  --appkeys myappkey1,myappkey2
```

## 场景 14：创建模板（写操作）

```bash
# 从文件创建模板
eagle template create eaglenode_esperf my_template \
  --file ./template.json \
  --appkeys myappkey1,myappkey2

# 创建 Composable 模板
eagle template create eaglenode_esperf my_template \
  --file ./composable-template.json \
  --appkeys myappkey1,myappkey2 \
  --type COMPOSABLE
```

## 场景 15：Appkey 管理

```bash
# 查看 Appkey 权限列表
eagle appkey auth-list

# 查看指定 Appkey 关联的集群组
eagle appkey related-cluster-group myappkey

# 查看 Appkey IDC 分布
eagle appkey idc-distribution myappkey

# 检查 Appkey 是否属于 Eagle
eagle appkey belongs-to-eagle myappkey
```

## 场景 16：多环境集群确认流程

```bash
# 当不确定集群在哪个环境时，按以下步骤确认：

# 1. 先检查当前环境
eagle sso status
eagle env show

# 2. 在当前环境尝试查询集群
eagle cluster describe my-cluster 2>&1

# 3. 如果不存在，切换到线下环境尝试
eagle sso login --env test
eagle cluster describe my-cluster 2>&1

# 4. 如果还不存在，切换到海外环境尝试
eagle sso login --env overseas
eagle cluster describe my-cluster 2>&1

# 5. 确认环境后，再执行后续操作
eagle index list my-cluster
```

## 常用管道组合

```bash
# 只看索引名列表
eagle index list <cluster> | jq -r '.content[].indexName'

# 只看集群名列表
eagle cluster list | jq -r '.content[].clusterName'

# 格式化输出到文件
eagle index describe <cluster> <index> | jq '.' > index_info.json

# 查看字段列表
eagle index fields <cluster> <index> | jq 'keys'

# 统计集群索引数量
eagle index list <cluster> -s 100 | jq '.totalElements'

# 查看索引健康状态分布
eagle index list <cluster> -s 100 | jq '.content | group_by(.health) | map({health: .[0].health, count: length})'

# 查找大索引（按存储大小排序）
eagle index list <cluster> -s 100 | jq '.content | sort_by(.storeSize) | reverse | .[0:5] | map({name: .indexName, size: .storeSize})'

# 查看集群节点 IP 列表
eagle node list <cluster> | jq -r '.[].ip'

# 查看 Top 10 慢查询集群
eagle metrics slow-query-avg | jq '.[0:10]'
```
