# 贡献指南

感谢您对 CarlaViz 项目的兴趣！我们欢迎各种形式的贡献，包括但不限于：

- 报告Bug
- 提交功能建议
- 完善文档
- 提交代码修复
- 添加新功能

## 开发环境设置

1. Fork 本仓库
2. 克隆您的 Fork：
   ```bash
   git clone https://github.com/yourusername/carlaviz.git
   cd carlaviz
   ```

3. 创建虚拟环境：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # 或
   venv\Scripts\activate  # Windows
   ```

4. 安装开发依赖：
   ```bash
   pip install -e .[dev]
   ```

## 开发流程

### 1. 创建功能分支

```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/your-bug-fix
```

### 2. 编写代码

- 遵循现有的代码风格
- 添加适当的注释
- 确保代码清晰易懂

### 3. 测试

在提交之前，请确保：

```bash
pytest tests/
```

### 4. 提交更改

```bash
git add .
git commit -m "Add: 添加新功能描述"
```

提交信息格式：

- `Add:` 新功能
- `Fix:` 错误修复
- `Update:` 更新现有功能
- `Docs:` 文档更新
- `Refactor:` 代码重构
- `Test:` 测试相关

### 5. 推送并创建Pull Request

```bash
git push origin feature/your-feature-name
```

然后在 GitHub 上创建 Pull Request。

## 代码规范

### Python 代码风格

- 遵循 PEP 8 规范
- 使用 4 空格缩进
- 类名使用 CamelCase
- 函数和变量名使用 snake_case
- 添加适当的文档字符串

### 提交信息规范

```
类型: 简短描述

详细说明（可选）
```

示例：

```
Add: 添加无头模式支持

- 支持在不显示窗口的情况下运行
- 适用于服务器环境
- 添加 --headless 命令行参数
```

## 问题反馈

在 GitHub Issues 中报告问题时，请包含：

- 清晰的标题和描述
- 复现步骤
- 预期行为和实际行为
- 环境信息（操作系统、Python版本等）
- 相关的错误日志

## 许可证

通过贡献代码，您同意您的贡献将按照 MIT 许可证进行许可。
