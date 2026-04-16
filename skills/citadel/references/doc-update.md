# 编辑/更新/插入新内容到学城文档指南

编辑/更新/插入新内容到学城文档是一个高危操作。学城文档的底层数据是基于 ProseMirror 生成的 JSON 结构，其中可能包含大量 Markdown 语法无法描述的特殊定制宏（如：包含合并单元格的表格，表格嵌套表格，特定的卡片、嵌入的第三方组件、文字颜色/背景色/对齐方式、展开卡片等）。

## 强势使用方式：CitadelMD 安全更新（零数据丢失）

**CitadelMD** 是一种基于 ProseMirror JSON 的扩展 Markdown 格式，通过 `:::tag{attrs}` 语法完整编码所有自定义宏节点，**100% 保留文档结构**，不会产生任何数据丢失。

### 完整工作流

#### 第一步：获取文档的 CitadelMD 内容

```bash
# 直接打印到终端
oa-skills citadel getDocumentCitadelMd --contentId <id>

# 保存到文件（推荐，便于编辑）
oa-skills citadel getDocumentCitadelMd --contentId <id> --output doc.citadelmd
```

#### 第二步：修改 CitadelMD 内容

直接编辑 `.citadelmd` 文件，或者由 AI 对内容进行增、删、改操作。

CitadelMD 是学城专用的扩展 Markdown 格式，完整语法见 [doc-syntax.md](doc-syntax.md)。

---

### 编辑注意事项

1. **保留所有宏节点**：任何 `:::tag{...}:::` 或 `:[tag]{...}` 节点，若不需要修改则原样保留
2. **不要修改 id 字段**：`gantt`、`drawio`、`minder`、`xtable` 等节点的 `id` 是服务端资源标识，必须保留
3. **合并单元格表格**：`:::table` 块内的 JSON 只改 `content` 字段内的文字，不要改 `colspan`/`rowspan` 结构；
4. **每个单元格的 `content` 字段不能为空字符串，若单元格为空则保留 `"content": ""`**（转换时会自动生成一个空 paragraph）；
5. **新增表格时第一行必须是表头行（`type: "table_header"`），不能全部使用 `table_cell`**
6. **空行分隔块**：不同的块元素之间需要有空行分隔，列表项之间不加空行
7. **行内宏不换行**：所有 `:[tag]{...}` 行内宏必须写在同一行内，不能跨行

#### 第三步：回传更新

```bash
# 从文件更新
oa-skills citadel updateDocumentByMd --contentId <id> --file doc.citadelmd

# 同时更新标题
oa-skills citadel updateDocumentByMd --contentId <id> --file doc.citadelmd --title "新标题"
```

#### 调试：查看 CitadelMD 转换为 JSON 的结果

如需验证转换是否正确，可以先转换为 JSON 检查：

```bash
oa-skills citadel convertMdToJson --file doc.citadelmd --output doc.json
```

---

## 总结

| 方式 | 命令 | 数据安全 | 推荐 |
|------|------|----------|------|
| CitadelMD 更新 | `updateDocumentByMd` | ✅ 完全安全 | ✅ 推荐 |

**优先使用 CitadelMD 方式进行文档更新。保护用户的数据完整性是第一原则。**

**输出** 完成编辑后返回用户文档链接，让用户可以直接点击查看文档变更的内容
