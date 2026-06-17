#!/bin/bash
# MangoView 服务管理脚本

echo "=== MangoView 服务管理 ==="

# 检查服务状态
echo ""
echo "1. 检查服务状态..."
echo "--- 后端 API ---"
curl -s http://localhost:8003/api/health 2>/dev/null || echo "❌ 后端未运行"

echo ""
echo "--- 前端 ---"
curl -s -o /dev/null -w "HTTP %{http_code}" http://localhost:3000 2>/dev/null || echo "❌ 前端未运行"

echo ""
echo "--- Tunnel ---"
ps aux | grep "mangoview" | grep cloudflared | grep -v grep | head -1 || echo "❌ Tunnel 未运行"

echo ""
echo "2. 访问地址..."
echo "  前端: https://view.mangofolio.com"
echo "  后端: https://api.mangofolio.com"

echo ""
echo "3. 日志位置..."
echo "  前端: tail -f /tmp/mangoview-web.log"
echo "  后端: tail -f /tmp/mangoview-api.log"
echo "  Tunnel: tail -f /tmp/mangoview-tunnel.log"

echo ""
echo "=== 完成 ==="
