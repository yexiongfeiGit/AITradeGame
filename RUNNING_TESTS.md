# 如何运行特定的测试方法

本文档说明了如何单独运行特定的测试方法或新增的测试方法。

## 运行单个测试方法

### 1. 使用pytest运行特定测试方法

要运行单个测试方法，可以使用以下语法：

```bash
# 运行特定测试类中的特定方法
python -m pytest test.py::TestMarketDataService::test_get_market_data -v

# 运行另一个特定测试方法
python -m pytest test.py::TestMarketDataService::test_get_current_price -v

# 运行第三个测试方法
python -m pytest test.py::TestMarketDataService::test_invalid_coin -v
```

### 2. 使用unittest运行特定测试方法

```bash
# 运行特定测试类中的特定方法
python -m unittest test.TestMarketDataService.test_get_market_data -v

# 运行另一个特定测试方法
python -m unittest test.TestMarketDataService.test_get_current_price -v

# 运行第三个测试方法
python -m unittest test.TestMarketDataService.test_invalid_coin -v
```

## 运行特定测试类中的所有方法

```bash
# 使用pytest运行测试类中的所有方法
python -m pytest test.py::TestMarketDataService -v

# 使用unittest运行测试类中的所有方法
python -m unittest test.TestMarketDataService -v
```

## 运行整个测试文件

```bash
# 使用pytest运行所有测试
python -m pytest test.py -v

# 使用unittest运行所有测试
python -m unittest test -v
```

## 添加新的测试方法

要在test.py中添加新的测试方法，请按照以下步骤操作：

1. 在TestMarketDataService类中添加新的方法
2. 确保方法名以`test_`开头
3. 添加适当的文档字符串说明测试目的
4. 实现测试逻辑

例如：

```python
def test_new_feature(self):
    """Test description of what this test does."""
    # Your test implementation here
    pass
```

然后可以单独运行这个新方法：

```bash
python -m pytest test.py::TestMarketDataService::test_new_feature -v
```

## 常用测试运行选项

### 详细输出
```bash
python -m pytest test.py::TestMarketDataService::test_get_market_data -v
```

### 更详细的输出（包括打印语句）
```bash
python -m pytest test.py::TestMarketDataService::test_get_market_data -vv -s
```

### 运行失败的测试
```bash
python -m pytest --lf
```

### 运行前N个测试
```bash
python -m pytest --count=5
```

## 示例输出

运行单个测试方法的示例输出：

```
======================================= test session starts =======================================
platform darwin -- Python 3.12.0, pytest-8.4.2, pluggy-1.6.0 -- /usr/local/bin/python
cachedir: .pytest_cache
rootdir: /Users/fei/Documents/demo/AITradeGame
plugins: anyio-4.10.0, langsmith-0.4.13
collected 1 item                                                                                  

test.py::TestMarketDataService::test_get_market_data PASSED                                 [100%]

======================================== 1 passed in 1.54s ========================================
```