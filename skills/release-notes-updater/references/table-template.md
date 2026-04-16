# Release Notes Table Template

## Standard 4-column header

```citadelmd
:::table{borderColor="#cccccc" borderStyle="solid" borderWidth=1 responsive=false}
[
  [
    {
      "type": "table_header",
      "attrs": {
        "colspan": 1,
        "rowspan": 1,
        "colwidth": [
          207
        ],
        "textAlign": null,
        "verticalAlign": null,
        "bgColor": null,
        "color": null,
        "numCell": 0
      },
      "content": ":::paragraph{align=center indent=0}\n:[font]{size=14}版本变化[/font]\n:::"
    },
    {
      "type": "table_header",
      "attrs": {
        "colspan": 1,
        "rowspan": 1,
        "colwidth": [
          480
        ],
        "textAlign": null,
        "verticalAlign": null,
        "bgColor": null,
        "color": null,
        "numCell": 0
      },
      "content": ":::paragraph{align=center indent=0}\n:[font]{size=14}新功能[/font]\n:::"
    },
    {
      "type": "table_header",
      "attrs": {
        "colspan": 1,
        "rowspan": 1,
        "colwidth": [
          480
        ],
        "textAlign": null,
        "verticalAlign": null,
        "bgColor": null,
        "color": null,
        "numCell": 0
      },
      "content": ":::paragraph{align=center indent=0}\n:[font]{size=14}BugFix 和其他注意事项[/font]\n:::"
    },
    {
      "type": "table_header",
      "attrs": {
        "colspan": 1,
        "rowspan": 1,
        "colwidth": [
          351
        ],
        "textAlign": null,
        "verticalAlign": null,
        "bgColor": null,
        "color": null,
        "numCell": 0
      },
      "content": ":::paragraph{align=center indent=0}\n:[font]{size=14}更新时间[/font]\n:::"
    }
  ],
  ... INSERT NEW DATA ROW HERE (before existing rows) ...
]
:::
```

## New data row template

Replace `{...}` placeholders with actual content.

```json
[
  {
    "type": "table_cell",
    "attrs": {
      "colspan": 1,
      "rowspan": 1,
      "colwidth": [
        207
      ],
      "textAlign": null,
      "verticalAlign": null,
      "bgColor": null,
      "color": null,
      "numCell": 0
    },
    "content": "{版本变化，e.g. **common** 0.0.9 → **0.0.10**\n\n**dal** 0.0.7 → **0.0.8**}"
  },
  {
    "type": "table_cell",
    "attrs": {
      "colspan": 1,
      "rowspan": 1,
      "colwidth": [
        480
      ],
      "textAlign": null,
      "verticalAlign": null,
      "bgColor": null,
      "color": null,
      "numCell": 0
    },
    "content": "{新功能，e.g. **① Feature title** [[abc1234](https://git.sankuai.com/org/repo/commits/abc1234)]\nDescription.\n\n**② Feature title** [[def5678](https://git.sankuai.com/org/repo/commits/def5678)]\nDescription.}"
  },
  {
    "type": "table_cell",
    "attrs": {
      "colspan": 1,
      "rowspan": 1,
      "colwidth": [
        480
      ],
      "textAlign": null,
      "verticalAlign": null,
      "bgColor": null,
      "color": null,
      "numCell": 0
    },
    "content": "{BugFix，e.g. ① Fix description [[abc1234](https://git.sankuai.com/org/repo/commits/abc1234)]\n\n② Fix description [[def5678](https://git.sankuai.com/org/repo/commits/def5678)]}"
  },
  {
    "type": "table_cell",
    "attrs": {
      "colspan": 1,
      "rowspan": 1,
      "colwidth": [
        351
      ],
      "textAlign": null,
      "verticalAlign": null,
      "bgColor": null,
      "color": null,
      "numCell": 0
    },
    "content": ":[font]{size=14}{时间范围，e.g. 2026.04.01 ～ 2026.04.30}[/font]"
  }
]
```

## Insertion logic (Python snippet)

```python
import json, re

with open('/tmp/rn_update.citadelmd', 'r') as f:
    content = f.read()

# Find the :::table block
table_start = content.find(':::table{')
table_end = content.find('\n:::', table_start) + 4  # includes closing \n:::

block = content[table_start:table_end]

# Extract the JSON array (between first [ and last ])
json_start = block.index('\n') + 1  # skip the :::table{...} line
json_end = block.rfind('\n:::')
table_json = json.loads(block[json_start:json_end])

# table_json[0] is the header row
# Insert new_row at index 1 (right after header)
new_row = [...]  # your composed row
table_json.insert(1, new_row)

# Rebuild
new_json = json.dumps(table_json, ensure_ascii=False, indent=2)
new_block = block[:block.index('\n')+1] + new_json + '\n:::'
new_content = content[:table_start] + new_block + content[table_end:]

with open('/tmp/rn_update.citadelmd', 'w') as f:
    f.write(new_content)
```
