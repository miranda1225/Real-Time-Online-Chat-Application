#!/bin/bash

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 激活虚拟环境
source venv/bin/activate

# 运行 pytest
echo "🚀 Running tests..."
pytest -v

