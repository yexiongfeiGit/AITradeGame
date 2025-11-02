# 测试配置说明

本文档说明了如何配置和运行AITradeGame项目的测试。

## 所需依赖

项目测试需要以下Python包：
- pytest: 测试框架
- 项目本身的依赖（已在requirements.txt中列出）

## 安装测试环境

1. 安装项目依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 安装测试依赖：
   ```bash
   pip install pytest
   ```

## 运行测试

### 运行所有测试
```bash
python -m pytest
```

### 运行特定测试文件
```bash
python -m pytest test.py -v
```

### 运行测试并显示覆盖率
```bash
pip install pytest-cov
python -m pytest --cov=.
```

## 测试结构

当前测试文件：
- `test.py`: 包含MarketDataFetcher类的测试

## 添加新测试

1. 在test.py中添加新的测试类或方法
2. 遵循unittest.TestCase的命名约定
3. 使用`test_`前缀命名测试方法

## IDE配置

### VS Code
安装以下插件以获得最佳测试体验：
- Python
- Pylance
- Python Test Explorer

### PyCharm
PyCharm Professional版内置了pytest支持。

## 故障排除

如果遇到问题，请尝试：
1. 确保所有依赖都已安装
2. 检查Python路径设置
3. 确认网络连接正常（某些测试需要访问外部API）