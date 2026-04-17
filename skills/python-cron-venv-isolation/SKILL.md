---
name: python-cron-venv-isolation
description: |
  Python cron 任务使用虚拟环境（.venv）的正确配置指南。
  当遇到 cron 任务因 ModuleNotFoundError 静默失败、或需要配置依赖 .venv 的定时脚本时使用。

  触发场景：
  - "cron 任务报 ModuleNotFoundError"
  - "定时脚本在终端能跑，cron 里失败"
  - "cron 无法找到 Python 包"
  - "配置 Python cron 任务使用 venv"
  - "observer/heartbeat 脚本静默失败"
---

## 根因

cron 使用系统 Python（`/usr/bin/python3`），不继承用户 shell 的 PATH 和 virtualenv 激活状态。`.venv` 中安装的包对系统 Python 不可见。

## 修复方案

**方案 1：直接指定解释器（推荐）**

```crontab
# 错误
30 10 * * * /usr/bin/env python3 /path/to/script.py

# 正确
30 10 * * * /path/to/project/.venv/bin/python /path/to/script.py
```

**方案 2：激活 venv 后执行**

```crontab
30 10 * * * cd /path/to/project && source .venv/bin/activate && python script.py
```

## 诊断步骤

1. 查 cron 日志：`grep CRON /var/log/syslog`
2. 验证解释器存在：`ls /path/to/project/.venv/bin/python`
3. 验证包可用：`/path/to/project/.venv/bin/python -c "import dotenv; print('ok')"`
4. 检查 crontab：`crontab -l`

## 注意事项

- `.venv` 路径必须是绝对路径，cron 不支持 `~` 展开
- `.venv` 重建后 cron 配置无需改动（路径不变）
- 建议脚本内写日志：`logging.basicConfig(filename='/abs/path/to/script.log', ...)`
