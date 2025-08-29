#!/bin/bash

# 配置设置脚本
# 这个脚本帮助用户设置项目配置

echo "=== 安师记微信公众号AI助手配置设置 ==="
echo ""

# 检查是否已存在define.py
if [ -f "define.py" ]; then
    echo "⚠️  发现已存在的 define.py 文件"
    read -p "是否要备份现有配置？(y/n): " backup_choice
    if [ "$backup_choice" = "y" ] || [ "$backup_choice" = "Y" ]; then
        backup_file="define.py.backup.$(date +%Y%m%d_%H%M%S)"
        cp define.py "$backup_file"
        echo "✅ 已备份到: $backup_file"
    fi
fi

# 创建define.py配置
echo ""
echo "📝 创建 define.py 配置文件..."
if [ ! -f "define.example.py" ]; then
    echo "❌ 找不到 define.example.py 模板文件"
    exit 1
fi

cp define.example.py define.py
echo "✅ define.py 已创建，请编辑该文件填写实际配置"

# 创建.env配置
echo ""
echo "📝 创建 .env 环境变量文件..."
if [ ! -f ".env.example" ]; then
    echo "❌ 找不到 .env.example 模板文件"
else
    cp .env.example .env
    echo "✅ .env 已创建，请编辑该文件填写实际环境变量"
fi

echo ""
echo "🎉 配置设置完成！"
echo ""
echo "下一步操作："
echo "1. 编辑 define.py 文件，填写实际的配置信息"
echo "2. 编辑 .env 文件（如需要），填写环境变量"
echo "3. 确保这些文件不会被提交到Git（已在.gitignore中配置）"
echo "4. 运行项目：python wechat_app.py"
