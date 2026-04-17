# 配置说明

## 配置文件位置

所有配置都在 `backend/config.json` 文件中。

## 配置项说明

### 1. 小米账号配置 (xiaomi)
```json
"xiaomi": {
  "username": "您的小米账号",
  "password": "您的小米密码"
}
```
- 用于登录小米账号，获取小爱音箱对话记录

### 2. AI模型配置 (openai_api) ⭐
```json
"openai_api": {
  "base_url": "https://api.openai.com/v1",
  "api_key": "您的API密钥",
  "model": "gpt-3.5-turbo"
}
```

#### 如何修改AI API：
- **base_url**: AI服务的API地址
  - OpenAI: `https://api.openai.com/v1`
  - 小米Mimo: `https://api.xiaomimimo.com/v1`
  - 阿里云百炼: `https://dashscope.aliyuncs.com/compatible-mode/v1`
  - 其他兼容OpenAI格式的服务都可以使用
  
- **api_key**: 您的API密钥
  - 从对应AI平台的控制台获取
  
- **model**: 使用的模型名称
  - OpenAI: `gpt-3.5-turbo`, `gpt-4`
  - 小米Mimo: `MiMo-V2-Flash`, `MiMo-V2-Pro`
  - 阿里云: `qwen-plus`, `qwen-max`

#### 支持的AI服务商（兼容OpenAI格式）：
| 服务商 | base_url | model示例 |
|--------|----------|------------|
| OpenAI | `https://api.openai.com/v1` | gpt-3.5-turbo, gpt-4 |
| 小米Mimo | `https://api.xiaomimimo.com/v1` | MiMo-V2-Flash |
| 阿里云百炼 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | qwen-plus |
| Anthropic | `https://api.anthropic.com` | claude-3-opus |
| Azure OpenAI | `https://{your-resource-name}.openai.azure.com/openai/deployments/{deployment-id}` | gpt-35-turbo |

### 3. WebSocket配置 (websocket)
```json
"websocket": {
  "host": "localhost",
  "port": 8765
}
```
- 后端服务监听的地址和端口
- 浏览器插件通过此端口连接

### 4. 浏览器控制配置 (browser_control)
```json
"browser_control": {
  "enable_ai": true,
  "default_timeout": 10,
  "enable_keyword_fallback": true
}
```
- `enable_ai`: 是否启用AI解析
- `default_timeout`: AI请求超时时间（秒）
- `enable_keyword_fallback`: 是否启用关键词匹配作为备选

### 5. 对话记录配置 (conversation)
```json
"conversation": {
  "pull_interval": 2,
  "enable_pull_ask": true
}
```
- `pull_interval`: 拉取对话记录的时间间隔（秒）
- `enable_pull_ask`: 是否启用对话记录拉取

## 常见配置示例

### 示例1: 使用OpenAI
```json
"openai_api": {
  "base_url": "https://api.openai.com/v1",
  "api_key": "sk-xxxxx",
  "model": "gpt-3.5-turbo"
}
```

### 示例2: 使用小米Mimo
```json
"openai_api": {
  "base_url": "https://api.xiaomimimo.com/v1",
  "api_key": "您的Mimo_API_Key",
  "model": "MiMo-V2-Flash"
}
```

### 示例3: 使用阿里云百炼
```json
"openai_api": {
  "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
  "api_key": "您的阿里云API_Key",
  "model": "qwen-plus"
}
```

## 环境变量方式

也可以通过环境变量配置：
```bash
export XIAOMI_USERNAME="your_username"
export XIAOMI_PASSWORD="your_password"
export OPENAI_API_KEY="your_api_key"
export OPENAI_BASE_URL="https://api.openai.com/v1"
export OPENAI_MODEL="gpt-3.5-turbo"
export WEBSOCKET_PORT=8765
```