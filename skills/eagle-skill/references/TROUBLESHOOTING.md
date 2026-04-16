# Eagle CLI 常见问题

## 登录问题

### 未登录错误
```
请先登录
使用 eagle sso login 进行登录
```
**解决**: 执行 `eagle sso login` 完成 SSO 认证

### 认证过期
如果 API 返回认证失败错误：
**解决**:
```bash
eagle sso logout
eagle sso login
```

### 切换环境后需要重新登录
```
错误: 当前环境为 test，但 token 为 prod 环境，请先登录
```
**解决**: 使用对应环境重新登录
```bash
eagle sso login --env test    # 切换到测试环境
eagle sso login --env prod    # 切换到线上环境
eagle sso login --env overseas # 切换到海外环境
```

## 环境相关问题

### 集群不存在
```
错误: 获取集群详情失败: Cluster not found
```
**可能原因和解决**:
1. **集群名称错误**: 确认集群名称拼写正确
   ```bash
   eagle cluster list | jq '.content[].clusterName'
   ```

2. **集群在其他环境**: 使用环境确认流程
   ```bash
   # 检查当前环境
   eagle sso status
   eagle env show

   # 切换到其他环境尝试
   eagle sso login --env test
eagle cluster describe <cluster>

   eagle sso login --env overseas
   eagle cluster describe <cluster>
   ```

3. **使用 eagle cluster list 有分页限制**: 如果集群不在第一页，使用 name-list
   ```bash
   eagle cluster name-list | grep <keyword>
   ```

### 海外集群访问
欧洲等海外集群需要通过海外环境访问：
```bash
# 登录海外环境
eagle sso login --env overseas

# 然后访问海外集群
eagle cluster describe <overseas-cluster>
```

## 命令错误

### 缺少必需参数
```
错误: 请提供有效的集群名称
使用 eagle cluster describe <cluster-name>
```
**解决**: 按照提示提供必需的参数

### 集群/索引不存在
```
错误: 获取集群详情失败: Cluster not found
```
**解决**:
```bash
# 先确认集群名称正确
eagle cluster list | jq '.content[].clusterName'

# 或搜索相近名称
eagle cluster list -n <keyword>
```

## JSON 输出问题

### 输出不是 JSON
部分命令可能返回空或错误页面。检查：
1. 是否已登录
2. 集群/索引名称是否正确
3. 网络连接是否正常

### 中文乱码
确保终端使用 UTF-8 编码：
```bash
export LANG=zh_CN.UTF-8
```

## 性能问题

### 索引列表加载慢
索引数量多时，增加分页大小：
```bash
eagle index list <cluster> -s 100
```

### 频繁超时
检查网络连接，或使用 VPN

## 权限问题

### 无法查看某些索引
默认只显示"我的索引"，使用 `--all` 查看全部：
```bash
eagle index list <cluster> --all
```

### 权限不足
某些操作需要特定权限，联系集群 Owner 申请

### 创建索引/模板后未生效
创建操作需要审批：
1. 创建后会返回审批链接
2. 前往审批页面完成审批
3. 审批通过后配置才会生效

## 调试技巧

### 查看完整错误
```bash
# 不使用 jq，查看原始输出
eagle cluster describe <cluster>

# 检查 HTTP 状态
eagle cluster describe <cluster> 2>&1 | head

# 查看详细错误信息
eagle cluster describe <cluster> --debug 2>&1
```

### 测试 CLI 是否正常工作
```bash
# 检查登录状态
eagle sso status

# 尝试列出集群
eagle cluster list

# 查看当前环境
eagle env show
```

## 安装问题

### 命令未找到 (command not found)
```bash
# 确保 npm 全局 bin 目录在 PATH 中
npm bin -g

# 或使用 npx 运行
npx eagle <command>

# 或检查是否正确安装
npm list -g @mtfe/eagle-cli
```

### 构建失败
```bash
# 清理依赖重新安装
rm -rf node_modules
npm install
npm run build
```

## 环境确认流程

当不确定集群在哪个环境时，按以下步骤排查：

```bash
# 1. 查看当前登录状态和环境
eagle sso status
eagle env show

# 2. 在当前环境尝试
eagle cluster describe <cluster> 2>&1

# 3. 如果失败，切换到线下环境
eagle sso login --env test
eagle cluster describe <cluster> 2>&1

# 4. 如果还失败，切换到海外环境
eagle sso login --env overseas
eagle cluster describe <cluster> 2>&1

# 5. 如果所有环境都找不到，使用模糊搜索确认集群名称
eagle cluster list -n <keyword>
```

## 写操作注意事项

### 创建索引/模板
- 必须提供 `--appkeys` 参数
- 创建后需要审批才能生效
- 会返回审批链接

### 变更操作确认
涉及创建、修改、删除等变更操作前，需要确认：
- 当前环境（线上/线下/海外）
- 操作的影响范围
- 是否需要审批

## 代理设置

如果需要通过代理访问：
```bash
export http_proxy=http://proxy.example.com:8080
export https_proxy=http://proxy.example.com:8080
```

Eagle CLI 会自动读取这些环境变量。
