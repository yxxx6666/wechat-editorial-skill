#!/usr/bin/env bash
# wechat-editorial-skill 一键安装脚本
# 用法: curl -fsSL https://raw.githubusercontent.com/yxxx6666/wechat-editorial-skill/main/install.sh | bash
set -e

REPO="https://github.com/yxxx6666/wechat-editorial-skill.git"
SKILL_NAME="wechat-editorial-skill"
INSTALL_DIR="${HOME}/.workbuddy/skills/${SKILL_NAME}"
TMP_DIR="/tmp/${SKILL_NAME}-install-$$"

echo "================================"
echo "  wechat-editorial-skill 安装器"
echo "  v0.5.0 | Editorial Marker Library"
echo "================================"
echo ""

# 检测 Python
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        ver=$("$cmd" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null)
        major=$("$cmd" -c 'import sys; print(sys.version_info.major)' 2>/dev/null)
        minor=$("$cmd" -c 'import sys; print(sys.version_info.minor)' 2>/dev/null)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ] 2>/dev/null; then
            PYTHON="$cmd"
            echo "[OK] 检测到 Python $ver ($cmd)"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "[ERROR] 需要 Python 3.10+，请先安装 Python。"
    exit 1
fi

# 检测 pip
PIP=""
for cmd in pip3 pip; do
    if command -v "$cmd" &>/dev/null; then
        PIP="$cmd"
        break
    fi
done

if [ -z "$PIP" ]; then
    echo "[ERROR] 未检测到 pip，请先安装 pip。"
    exit 1
fi

echo "[OK] 检测到 pip ($PIP)"
echo ""

# 检测 git
if ! command -v git &>/dev/null; then
    echo "[ERROR] 需要 git，请先安装 git。"
    exit 1
fi
echo "[OK] 检测到 git"

# 安装目录
SKILLS_PARENT="${HOME}/.workbuddy/skills"
mkdir -p "$SKILLS_PARENT"

# 如果已存在，备份后覆盖
if [ -d "$INSTALL_DIR" ]; then
    BACKUP="${INSTALL_DIR}.bak.$(date +%Y%m%d%H%M%S)"
    echo "[INFO] 已存在旧版本，备份到: $BACKUP"
    mv "$INSTALL_DIR" "$BACKUP"
fi

echo ""
echo "[1/4] 克隆仓库..."
git clone --depth 1 "$REPO" "$INSTALL_DIR"
echo "[OK] 克隆完成"

echo ""
echo "[2/4] 安装 Python 依赖..."
$PIP install --quiet pyyaml jsonschema 2>/dev/null || {
    echo "[WARN] 全局安装失败，尝试用户级安装..."
    $PIP install --user --quiet pyyaml jsonschema
}
echo "[OK] 依赖安装完成"

echo ""
echo "[3/4] 验证安装..."
cd "$INSTALL_DIR"
$PYTHON scripts/quick_validate.py . --mode quick 2>&1 | tail -5 || {
    echo "[WARN] 快速验证未完全通过，请检查输出。这不影响安装，但建议运行 release 验证。"
}

echo ""
echo "[4/4] 安装完成！"
echo ""
echo "================================"
echo "  安装成功"
echo "================================"
echo ""
echo "安装位置: $INSTALL_DIR"
echo ""
echo "快速开始:"
echo "  cd $INSTALL_DIR"
echo "  $PYTHON scripts/build_article.py your-article.md --output-dir out"
echo ""
echo "生成全标识图鉴:"
echo "  $PYTHON scripts/render_marker_showcase.py -o showcase.html"
echo ""
echo "完整验证:"
echo "  $PYTHON scripts/quick_validate.py . --mode release"
echo ""
echo "在 WorkBuddy 中使用:"
echo "  对话中输入 @skill:wechat-editorial-skill 即可调用"
echo ""

# 清理
rm -rf "$TMP_DIR" 2>/dev/null || true
