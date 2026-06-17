---
name: mangofolio-core-data
version: 1.0.0
description: "Mangofolio 核心数据层 - 统一数据获取与缓存"
author: 燃冰 + ant
created: 2026-05-08
skill_type: 核心🔴
allowed-tools: [Bash, Read, Write, Exec]
tags: [数据层，API, 缓存，Mangofolio]
---

# mangofolio-core-data: 核心数据层 📊

## 📋 功能描述

Mangofolio 的统一数据获取层，提供行情/基金/宏观数据的标准化接口。

**核心能力：**
- 统一数据 API（行情/基金/宏观）
- 数据缓存机制
- 多数据源降级链
- 信源等级标注

**边界条件：**
- 不替代专业金融终端
- 数据来源于公开 API（东方财富/天天基金等）
- 缓存有效期 24 小时

**免责声明：**
> ⚠️ 本文内容仅供参考，不构成任何投资建议。市场有风险，投资需谨慎。

---

## 🎯 核心模块

### 数据 API
- `DataAPI` - 统一数据接口
- `FundAPI` - 基金数据接口
- `Quote` - 行情数据模型
- `Financials` - 财务数据模型

### 数据提供者
- `eastmoney` - 东方财富
- `tencent` - 腾讯财经
- `sina` - 新浪财经
- `akshare` - AKShare（零 API Key）

### 缓存管理
- `CacheManager` - 缓存管理器
- 缓存有效期：24 小时
- 自动过期清理

---

## 🚀 快速开始

```bash
# 获取行情数据
python3 -c "
from data_api import DataAPI
api = DataAPI()
quote = api.get_quote('601688')
print(quote)
"
```

---

**版本**: v1.0.0  
**最后更新**: 2026-05-08
