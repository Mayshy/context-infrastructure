---
name: pdf
description: Comprehensive PDF manipulation toolkit for extracting text and tables, creating new PDFs, merging/splitting documents, and handling forms. When Claude needs to fill in a PDF form or programmatically process, generate, or analyze PDF documents at scale.
license: Proprietary. LICENSE.txt has complete terms
---

# PDF Processing Guide

## ⚠️ 中文/日文/韩文 (CJK) 字符支持 - 必读！

**创建 PDF 时如果内容包含中文、日文、韩文等 CJK 字符，必须先注册 CJK 字体！**

reportlab 默认字体（Helvetica 等）**不支持** CJK 字符，直接使用会导致：
- 中文显示为空白或乱码
- PDF 生成成功但内容缺失

**解决方案**：使用下方的 `find_cjk_font()` 函数自动查找并注册系统 CJK 字体，然后在所有 `setFont()` 和 `ParagraphStyle` 中使用 `'CJKFont'`。

详见下方 [Create PDF with CJK/Chinese Support](#create-pdf-with-cjkchinese-support-中文支持) 章节。

---


## Overview

This guide covers essential PDF processing operations using Python libraries and command-line tools. For advanced features, JavaScript libraries, and detailed examples, see REFERENCE.md. If you need to fill out a PDF form, read FORMS.md and follow its instructions.

## Quick Start

### 读取和提取 PDF 文本（支持中文）

```python
from pypdf import PdfReader, PdfWriter

# Read a PDF (pypdf 读取时自动支持中文)
reader = PdfReader("document.pdf")
print(f"Pages: {len(reader.pages)}")

# Extract text (中文内容可以正常提取)
text = ""
for page in reader.pages:
    text += page.extract_text()
```

### 创建中文 PDF（Quick Start 版本）

```python
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os, glob, platform

def find_cjk_font():
    """自动查找系统中支持 CJK 字符的字体文件（跨平台）"""
    system = platform.system()
    font_dirs = {
        'Darwin': ['/System/Library/Fonts', '/Library/Fonts', os.path.expanduser('~/Library/Fonts')],
        'Windows': [os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')],
    }.get(system, ['/usr/share/fonts', '/usr/local/share/fonts', os.path.expanduser('~/.fonts')])
    
    cjk_keywords = ['pingfang', 'hiragino', 'heiti', 'yahei', 'msyh', 'noto', 'source han',
                    'simsun', 'simhei', 'wqy', 'droid', 'arial unicode']
    font_files = []
    for d in font_dirs:
        if os.path.exists(d):
            for ext in ['*.ttf', '*.ttc', '*.otf', '*.TTC', '*.TTF', '*.OTF']:
                font_files.extend(glob.glob(os.path.join(d, '**', ext), recursive=True))
    for kw in cjk_keywords:
        for f in font_files:
            if kw.lower() in os.path.basename(f).lower():
                return f
    return font_files[0] if font_files else None

# 1. 查找并注册 CJK 字体（必须！）
font_path = find_cjk_font()
if not font_path:
    raise Exception("未找到 CJK 字体！请安装支持中文的字体。")
pdfmetrics.registerFont(TTFont('CJKFont', font_path))

# 2. 创建 PDF 并使用 CJKFont
c = canvas.Canvas("output.pdf", pagesize=A4)
c.setFont('CJKFont', 16)  # 必须使用注册的 CJKFont！
c.drawString(100, 750, "中文标题 - Chinese Title")
c.setFont('CJKFont', 12)
c.drawString(100, 720, "这是中文内容，支持中英文混排。")
c.save()
```

## Python Libraries

### pypdf - Basic Operations

#### Merge PDFs
```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

with open("merged.pdf", "wb") as output:
    writer.write(output)
```

#### Split PDF
```python
reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{i+1}.pdf", "wb") as output:
        writer.write(output)
```

#### Extract Metadata
```python
reader = PdfReader("document.pdf")
meta = reader.metadata
print(f"Title: {meta.title}")
print(f"Author: {meta.author}")
print(f"Subject: {meta.subject}")
print(f"Creator: {meta.creator}")
```

#### Rotate Pages
```python
reader = PdfReader("input.pdf")
writer = PdfWriter()

page = reader.pages[0]
page.rotate(90)  # Rotate 90 degrees clockwise
writer.add_page(page)

with open("rotated.pdf", "wb") as output:
    writer.write(output)
```

### pdfplumber - Text and Table Extraction

#### Extract Text with Layout
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

#### Extract Tables
```python
with pdfplumber.open("document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            print(f"Table {j+1} on page {i+1}:")
            for row in table:
                print(row)
```

#### Advanced Table Extraction
```python
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    all_tables = []
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table:  # Check if table is not empty
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

# Combine all tables
if all_tables:
    combined_df = pd.concat(all_tables, ignore_index=True)
    combined_df.to_excel("extracted_tables.xlsx", index=False)
```

### reportlab - Create PDFs

> **重要提示**: reportlab 默认使用的字体（如 Helvetica）不支持中文/日文/韩文等 CJK 字符。如果 PDF 内容包含这些字符，**必须**注册并使用支持 CJK 的字体，否则会显示乱码。


#### Basic PDF Creation (English Only)
```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("hello.pdf", pagesize=letter)
width, height = letter

# Add text
c.drawString(100, height - 100, "Hello World!")
c.drawString(100, height - 120, "This is a PDF created with reportlab")

# Add a line
c.line(100, height - 140, 400, height - 140)

# Save
c.save()
```

#### Create PDF with CJK/Chinese Support (中文支持)

使用 `fontTools` 自动扫描系统中所有可用的 CJK 字体，跨平台兼容：

```python
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import subprocess
import os
import glob

def find_cjk_font():
    """
    自动查找系统中支持 CJK 字符的字体文件。
    跨平台兼容 macOS、Windows、Linux。
    """
    # 定义各平台的字体搜索目录
    import platform
    system = platform.system()
    
    font_dirs = []
    if system == 'Darwin':  # macOS
        font_dirs = [
            '/System/Library/Fonts',
            '/Library/Fonts',
            os.path.expanduser('~/Library/Fonts'),
        ]
    elif system == 'Windows':
        font_dirs = [
            os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts'),
            os.path.expanduser('~\\AppData\\Local\\Microsoft\\Windows\\Fonts'),
        ]
    else:  # Linux
        font_dirs = [
            '/usr/share/fonts',
            '/usr/local/share/fonts',
            os.path.expanduser('~/.fonts'),
            os.path.expanduser('~/.local/share/fonts'),
        ]
    
    # CJK 字体的常见关键字（按优先级排序）
    cjk_font_keywords = [
        'pingfang', 'hiragino', 'heiti', 'yahei', 'msyh',  # 优先：现代黑体
        'noto', 'source han', 'sourcehans',                 # Google/Adobe 开源字体
        'simsun', 'simhei', 'kaiti', 'fangsong',           # Windows 中文字体
        'wqy', 'wenquanyi', 'droid',                        # Linux 常见字体
        'arial unicode', 'unifont',                         # 通用 Unicode 字体
    ]
    
    # 扫描所有字体目录
    font_files = []
    for font_dir in font_dirs:
        if os.path.exists(font_dir):
            for ext in ['*.ttf', '*.ttc', '*.otf', '*.TTC', '*.TTF', '*.OTF']:
                font_files.extend(glob.glob(os.path.join(font_dir, '**', ext), recursive=True))
    
    # 按关键字优先级查找
    for keyword in cjk_font_keywords:
        for font_path in font_files:
            if keyword.lower() in os.path.basename(font_path).lower():
                return font_path
    
    # 如果没有找到，返回第一个可用的字体文件（可能不支持中文）
    return font_files[0] if font_files else None

# 查找并注册 CJK 字体
font_path = find_cjk_font()
if not font_path:
    raise Exception("未找到可用字体！请安装支持中文的字体。")

pdfmetrics.registerFont(TTFont('CJKFont', font_path))

# 创建支持中文的 PDF
c = canvas.Canvas("chinese_doc.pdf", pagesize=A4)
width, height = A4

c.setFont('CJKFont', 16)
c.drawString(100, height - 100, "中文标题 - Chinese Title")
c.setFont('CJKFont', 12)
c.drawString(100, height - 130, "这是使用 reportlab 创建的中文 PDF 文档。")
c.drawString(100, height - 150, "支持中英文混排 with mixed Chinese and English.")

c.save()
print(f"PDF 创建成功，使用字体: {font_path}")
```

#### Create PDF with Multiple Pages (with CJK/Chinese Support)
```python
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import glob
import platform

def find_cjk_font():
    """自动查找系统中支持 CJK 字符的字体文件"""
    system = platform.system()
    font_dirs = []
    if system == 'Darwin':
        font_dirs = ['/System/Library/Fonts', '/Library/Fonts', os.path.expanduser('~/Library/Fonts')]
    elif system == 'Windows':
        font_dirs = [os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')]
    else:
        font_dirs = ['/usr/share/fonts', '/usr/local/share/fonts', os.path.expanduser('~/.fonts')]
    
    cjk_keywords = ['pingfang', 'hiragino', 'heiti', 'yahei', 'msyh', 'noto', 'source han', 
                    'simsun', 'simhei', 'wqy', 'droid', 'arial unicode']
    
    font_files = []
    for font_dir in font_dirs:
        if os.path.exists(font_dir):
            for ext in ['*.ttf', '*.ttc', '*.otf', '*.TTC', '*.TTF', '*.OTF']:
                font_files.extend(glob.glob(os.path.join(font_dir, '**', ext), recursive=True))
    
    for keyword in cjk_keywords:
        for font_path in font_files:
            if keyword.lower() in os.path.basename(font_path).lower():
                return font_path
    return font_files[0] if font_files else None

# 注册字体
font_path = find_cjk_font()
if not font_path:
    raise Exception("未找到可用字体！")
pdfmetrics.registerFont(TTFont('CJKFont', font_path))

# 创建支持中文的样式
styles = getSampleStyleSheet()
chinese_title = ParagraphStyle('ChineseTitle', parent=styles['Title'], fontName='CJKFont', fontSize=18)
chinese_heading = ParagraphStyle('ChineseHeading', parent=styles['Heading1'], fontName='CJKFont', fontSize=14)
chinese_body = ParagraphStyle('ChineseBody', parent=styles['Normal'], fontName='CJKFont', fontSize=12, leading=18)

doc = SimpleDocTemplate("report_chinese.pdf", pagesize=A4)
story = []

# 添加中文内容
story.append(Paragraph("报告标题 - Report Title", chinese_title))
story.append(Spacer(1, 12))
story.append(Paragraph("这是报告的正文内容。支持中英文混排。This is the body content." * 5, chinese_body))
story.append(PageBreak())

# 第二页
story.append(Paragraph("第二页 - Page 2", chinese_heading))
story.append(Paragraph("第二页的内容 - Content for page 2", chinese_body))

doc.build(story)
print(f"PDF 创建成功，使用字体: {font_path}")
```

#### Create PDF with Multiple Pages (English Only)
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

# Add content
title = Paragraph("Report Title", styles['Title'])
story.append(title)
story.append(Spacer(1, 12))

body = Paragraph("This is the body of the report. " * 20, styles['Normal'])
story.append(body)
story.append(PageBreak())

# Page 2
story.append(Paragraph("Page 2", styles['Heading1']))
story.append(Paragraph("Content for page 2", styles['Normal']))

# Build PDF
doc.build(story)
```

## Command-Line Tools

### pdftotext (poppler-utils)
```bash
# Extract text
pdftotext input.pdf output.txt

# Extract text preserving layout
pdftotext -layout input.pdf output.txt

# Extract specific pages
pdftotext -f 1 -l 5 input.pdf output.txt  # Pages 1-5
```

### qpdf
```bash
# Merge PDFs
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf

# Split pages
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf
qpdf input.pdf --pages . 6-10 -- pages6-10.pdf

# Rotate pages
qpdf input.pdf output.pdf --rotate=+90:1  # Rotate page 1 by 90 degrees

# Remove password
qpdf --password=mypassword --decrypt encrypted.pdf decrypted.pdf
```

### pdftk (if available)
```bash
# Merge
pdftk file1.pdf file2.pdf cat output merged.pdf

# Split
pdftk input.pdf burst

# Rotate
pdftk input.pdf rotate 1east output rotated.pdf
```

## Common Tasks

### Extract Text from Scanned PDFs
```python
# Requires: pip install pytesseract pdf2image
import pytesseract
from pdf2image import convert_from_path

# Convert PDF to images
images = convert_from_path('scanned.pdf')

# OCR each page
text = ""
for i, image in enumerate(images):
    text += f"Page {i+1}:\n"
    text += pytesseract.image_to_string(image)
    text += "\n\n"

print(text)
```

### Add Watermark
```python
from pypdf import PdfReader, PdfWriter

# Create watermark (or load existing)
watermark = PdfReader("watermark.pdf").pages[0]

# Apply to all pages
reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)

with open("watermarked.pdf", "wb") as output:
    writer.write(output)
```

### Extract Images
```bash
# Using pdfimages (poppler-utils)
pdfimages -j input.pdf output_prefix

# This extracts all images as output_prefix-000.jpg, output_prefix-001.jpg, etc.
```

### Password Protection
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

# Add password
writer.encrypt("userpassword", "ownerpassword")

with open("encrypted.pdf", "wb") as output:
    writer.write(output)
```

## Quick Reference

| Task | Best Tool | Command/Code |
|------|-----------|--------------|
| Merge PDFs | pypdf | `writer.add_page(page)` |
| Split PDFs | pypdf | One page per file |
| Extract text | pdfplumber | `page.extract_text()` |
| Extract tables | pdfplumber | `page.extract_tables()` |
| Create PDFs | reportlab | Canvas or Platypus |
| Command line merge | qpdf | `qpdf --empty --pages ...` |
| OCR scanned PDFs | pytesseract | Convert to image first |
| Fill PDF forms | pdf-lib or pypdf (see FORMS.md) | See FORMS.md |

## Code Style Guidelines

**IMPORTANT**: When generating Python scripts that contain Chinese string literals:
- Never embed Chinese characters directly in Python string literals
- Use Unicode escapes to avoid encoding issues and quote conflicts (Chinese curly quotes `"` `"` break Python syntax)
  - ✅ `"\u7f8e\u56e2\u5916\u5356"` (美团外卖)
  - ❌ `"美团外卖"` or `"美团外卖"` (中文引号会导致 SyntaxError)
- This applies to all string contexts: `drawString()`, `Paragraph()`, cell values, variable assignments, etc.
- Exception: comments (`#`) are safe to write in Chinese

## Next Steps

- For advanced pypdfium2 usage, see REFERENCE.md
- For JavaScript libraries (pdf-lib), see REFERENCE.md
- If you need to fill out a PDF form, follow the instructions in FORMS.md
- For troubleshooting guides, see REFERENCE.md
