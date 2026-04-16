---
name: file-download
description: 下载文件和图片到本地。当用户消息中包含任何 URL 链接指向文件或图片时，必须使用此 skill 通过 curl 命令下载到本地，禁止使用 web_fetch 工具获取文件和图片。适用场景包括但不限于：下载图片、下载文件、保存图片、保存文件、识别图片、查看图片、读取图片、分析图片、处理图片、打开图片、读取文件、打开文件、处理文件、OCR、图片内容、文件内容、查看文档、预览文件。
---

# File Download - 文件下载规范

## ⛔ 禁止事项（最高优先级）

1. **禁止使用 `web_fetch` 工具下载或读取任何文件和图片** — `web_fetch` 会拦截内网地址导致失败
2. **禁止直接将远程 URL 传给其他工具处理** — 必须先下载到本地
3. **唯一允许的下载方式是 `curl` 命令**

## 存储路径

所有下载的文件统一存放到：

```
/tmp/files/
```

首次使用时创建目录：`mkdir -p /tmp/files`

## 文件命名

使用下载时的 **Unix 时间戳** 作为文件名，不要使用上传文件的自身的文件名，保留原始扩展名：

```
/tmp/files/{timestamp}.{ext}
```

### 示例

- 图片：`/tmp/files/1709697600.png`
- 文档：`/tmp/files/1709697600.docx`
- PDF：`/tmp/files/1709697600.pdf`

### 获取时间戳

```bash
date +%s
```

### 扩展名推断优先级

1. URL 中的 `filename=` 参数
2. URL 路径中的文件扩展名
3. 下载后用 `file` 命令检测 MIME 类型推断

## 下载方式

**必须使用 `curl` 下载，不要使用 `web_fetch`：**

```bash
mkdir -p /tmp/files
TIMESTAMP=$(date +%s)
curl -sL -o /tmp/files/${TIMESTAMP}.png "图片URL"
```

## 下载后验证

```bash
file /tmp/files/${TIMESTAMP}.png
ls -la /tmp/files/${TIMESTAMP}.png
```

确认文件类型和大小符合预期。

## 衍生文件（帧/页面）

> 这样原始文件和衍生文件分开存放，便于管理和清理。

PDF 渲染的页面图片、视频截取的帧等单个文件的**衍生文件**，统一存放到：

```
/tmp/files/frames/
```

首次使用时创建目录： `mkdir -p /tmp/files/frames`

命名规则：`{原文件时间戳}_{序号}.{扩展名}`

### 示例

- PDF 第 1 页：`/tmp/files/frames/1709697600_1.png`
- 视频第 10 帧：`/tmp/files/frames/1709697600_10.jpg`

## 完整流程

1. 从消息中提取文件 URL
2. `mkdir -p /tmp/files`
3. `TIMESTAMP=$(date +%s)`
4. 从 URL 推断扩展名
5. `curl -sL -o /tmp/files/${TIMESTAMP}.{ext} "URL"`
6. 验证文件完整性
7. 使用 `read` 工具读取（如需识别图片内容）
