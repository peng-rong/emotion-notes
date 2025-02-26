# EmotionNote - 个人情绪记录网站

这是一个基于 Flask 的个人情绪记录网站，数据存储于飞书多维表格。采用苹果设计风格，提供简洁优雅的记录体验。

## 功能特点

- 简洁的情绪记录界面
- 支持快速添加新记录
- 按时间顺序展示情绪记录
- 显示记录日期和事件内容
- 晚间/早晨问候功能
- 情绪颜色可视化
- 日历视图展示

## 技术栈

- 后端：Python Flask，集成日志记录系统
- 前端：原生HTML/CSS，采用苹果设计风格
- 数据源：飞书多维表格
- 依赖管理：Poetry

## 飞书配置要求

1. 创建飞书应用
   - 获取应用凭证（App ID 和 App Secret）
   - 开启多维表格权限：`bitable:record:read`

2. 创建多维表格
   - 创建情绪记录表格，包含以下字段：
     * 日期（时间戳格式）
     * 事件（文本格式）
   - 创建晚间问候表格，包含以下字段：
     * 提醒日（时间戳格式）
     * 晚间问候.文本化结果（文本格式）
     * 早晨问候.文本化结果（文本格式）
     * 情绪颜色（枚举：快乐、平静、疲倦、焦虑、低落、愤怒）

## 快速开始

1. 克隆项目后，创建以下目录结构：
```
EmotionNote/
├── README.md
├── poetry.toml          # Poetry配置文件
├── pyproject.toml       # 项目依赖配置
├── config.py           # 配置文件
├── app.py             # 主应用
├── static/            # 静态文件
│   ├── css/
│   └── js/
└── templates/         # HTML模板
    └── index.html    # 首页
```

2. 配置Poetry环境：
```bash
# 安装Poetry（如果未安装）
curl -sSL https://install.python-poetry.org | python3 -

# 安装项目依赖
poetry install --no-root
```

3. 创建poetry.toml文件：
```toml
[virtualenvs]
in-project = true
```

4. 配置环境变量
在项目根目录创建 `.env` 文件，填入以下配置信息：
```ini
# 飞书应用配置
FEISHU_APP_ID=你的飞书应用ID
FEISHU_APP_SECRET=你的飞书应用密钥

# 多维表格配置
BASE_ID=wiki                # 如果使用知识库，保持此值为wiki
WIKI_BASE=你的知识库Token    # 如果使用知识库，填入知识库Token
TABLE_ID=你的表格ID         # 情绪记录表格ID
# 问候表格配置
GREETING_TABLE_ID=你的问候表格ID  # 问候表格ID

# Flask配置(可选）)
SECRET_KEY=你的密钥         # Flask应用密钥
FLASK_ENV=development      # 开发环境设置为development，生产环境设置为production


```

注意：
- 请将上述配置中的占位符替换为实际的值
- 确保 `.env` 文件已添加到 `.gitignore` 中，避免敏感信息泄露
- 首次运行前必须完成所有配置项的设置

5. 运行应用：
```bash
poetry run python app.py
```

6. 访问网站：
打开浏览器访问 http://localhost:5000

## 常见问题

1. 数据显示异常
   - 检查飞书应用权限是否正确开启
   - 验证多维表格的字段名称是否与代码中完全一致
   - 确认表格中已添加数据

2. 环境配置问题
   - 确保Poetry正确安装并配置
   - 检查虚拟环境是否在项目目录下创建

## 注意事项

- 不要在代码中直接硬编码飞书应用凭证
- 建议使用环境变量或配置文件管理敏感信息
- 已添加数据缓存机制，优化了页面加载速度
