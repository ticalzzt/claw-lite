# Claw-Lite 扣子轻量版

> 一个对扣子(Coze)核心功能的轻量级开源实现

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](README.md)
[![Stars](https://img.shields.io/github/stars/tical/claw-lite)](https://github.com/tical/claw-lite)

## 项目简介

**Claw-Lite** 是由 [@tical](https://github.com/tical) 创建的开源项目，旨在提供扣子(Coze)核心功能的轻量级开源实现。

本项目提取了扣子平台的核心能力，包括智能代理(Agent)、记忆管理(Memory)、任务调度(Scheduler)等模块，让开发者能够快速构建自己的 AI 应用，而无需依赖特定的商业平台。

### 核心定位

- **轻量级**：无外部依赖，核心库 < 1000 行代码
- **可扩展**：模块化设计，便于二次开发和功能扩展
- **易上手**：简洁的 API 设计，5 分钟快速入门
- **本地化**：支持本地部署，数据完全自主控制

## 功能特性

### 🧠 记忆管理系统 (Memory)
- 短期记忆：会话级上下文管理
- 长期记忆：持久化存储，支持文件系统和向量数据库
- 记忆检索：基于语义相似度的智能召回
- 记忆压缩：自动总结和遗忘低价值信息

### 🤖 Agent 核心引擎
- 多轮对话：支持连续上下文交互
- 工具调用：灵活扩展的工具系统
- 角色扮演：自定义 Agent 行为和人格
- 流式输出：实时响应，支持打字机效果

### 📅 任务调度系统 (Scheduler)
- 定时任务：支持 Cron 表达式
- 周期执行：分钟级到年级的精确调度
- 事件驱动：基于条件的任务触发
- 任务队列：优先级和依赖管理

### 🔧 LLM 客户端
- 多模型支持：OpenAI、Claude、MiniMax 等
- 统一接口：适配多种 LLM 提供商
- 灵活配置：支持 API Key、多端点配置
- 请求管理：自动重试、流量控制

## 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/tical/claw-lite.git
cd claw-lite

# 安装依赖
pip install -r requirements.txt

# 配置 API Key
cp config.example.yaml config.yaml
# 编辑 config.yaml 填入你的 API Key
```

### 基础使用

```python
from src.core.agent import Agent
from src.core.memory import Memory
from src.utils.llm_client import LLMClient

# 初始化组件
memory = Memory()
llm = LLMClient(provider="minimax")
agent = Agent(llm_client=llm, memory=memory)

# 开始对话
response = agent.chat("你好！")
print(response)
```

### 运行示例

```bash
python examples/basic_agent.py
```

## 架构说明

```
claw-lite/
├── src/
│   ├── core/                 # 核心模块
│   │   ├── agent.py         # Agent 核心类
│   │   ├── memory.py        # 记忆管理
│   │   └── scheduler.py     # 任务调度
│   └── utils/               # 工具模块
│       ├── file_handler.py  # 文件处理
│       └── llm_client.py    # LLM 客户端
├── examples/                # 使用示例
│   └── basic_agent.py
├── config.example.yaml      # 配置示例
└── requirements.txt         # 依赖清单
```

### 核心模块

| 模块 | 说明 |
|------|------|
| `Agent` | 智能代理核心，负责对话管理和工具调用 |
| `Memory` | 记忆管理，支持短期/长期记忆的存储和检索 |
| `Scheduler` | 任务调度器，处理定时和周期性任务 |
| `LLMClient` | 大语言模型客户端，统一接口访问多种模型 |

## 配置说明

```yaml
# config.example.yaml
llm:
  provider: minimax
  api_key: your-api-key
  base_url: https://api.minimax.chat/v1
  model: abab6-chat

memory:
  type: file  # file, sqlite, redis
  path: ./data/memory
  max_size: 1000

scheduler:
  enable: true
  timezone: Asia/Shanghai
```

## 贡献指南

我们欢迎任何形式的贡献！

### 如何参与

1. **Fork** 本仓库
2. **Clone** 你的 Fork: `git clone https://github.com/your-username/claw-lite.git`
3. **创建分支**: `git checkout -b feature/your-feature`
4. **提交改动**: `git commit -m 'Add some feature'`
5. **推送**: `git push origin feature/your-feature`
6. **提交 PR**

### 贡献类型

- 🐛 Bug 修复
- ✨ 新功能
- 📝 文档改进
- 🔧 代码优化
- 🧪 测试用例

### 开发规范

- 遵循 PEP 8 代码规范
- 提交前运行测试
- 更新相关文档

## 许可证

本项目采用 [MIT License](LICENSE) 开源。

## 致谢

- 感谢扣子(Coze)提供的灵感
- 感谢所有贡献者的付出

---

**Star ⭐ 支持一下，让更多人看到这个小项目！**
