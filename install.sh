#!/usr/bin/env bash
# wechat-editorial-skill 一键安装脚本
# 支持 WorkBuddy 和 Codex 两个目标平台
#
# 用法:
#   curl -fsSL https://raw.githubusercontent.com/yxxx6666/wechat-editorial-skill/main/install.sh | bash
#   curl -fsSL ... | bash -s -- --target codex
#   curl -fsSL ... | bash -s -- --target workbuddy
#   curl -fsSL ... | bash -s -- --target all
set -e

REPO="https://github.com/yxxx6666/wechat-editorial-skill.git"
SKILL_NAME="wechat-editorial-skill"
VERSION="v0.5.0"
TARGET="auto"

# ---- 参数解析 ----
while [ $# -gt 0 ]; do
    case "$1" in
        --target)
            TARGET="$2"
            shift 2
            ;;
        --target=*)
            TARGET="${1#*=}"
            shift
            ;;
        --help|-h)
            cat <<EOF
wechat-editorial-skill 安装器 $VERSION

用法:
  install.sh [--target workbuddy|codex|all|auto]

目标:
  workbuddy  仅安装到 WorkBuddy  (~/.workbuddy/skills/)
  codex      仅安装到 Codex      (~/.codex/skills/)
  all        同时安装到两个平台
  auto       自动检测已安装的平台（默认）

示例:
  install.sh                       # 自动检测
  install.sh --target codex        # 仅 Codex
  install.sh --target all          # 两个都装
EOF
            exit 0
            ;;
        *)
            echo "[WARN] 未知参数: $1"
            shift
            ;;
    esac
done

echo "=================================="
echo "  wechat-editorial-skill 安装器"
echo "  $VERSION | Editorial Marker Library"
echo "=================================="
echo ""

# ---- 检测 Python ----
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        ver=$("$cmd" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null)
        major=$("$cmd" -c 'import sys; print(sys.version_info.major)' 2>/dev/null)
        minor=$("$cmd" -c 'import sys; print(sys.version_info.minor)' 2>/dev/null)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ] 2>/dev/null; then
            PYTHON="$cmd"
            echo "[OK] Python $ver ($cmd)"
            break
        fi
    fi
done
if [ -z "$PYTHON" ]; then
    echo "[ERROR] 需要 Python 3.10+，请先安装。"
    exit 1
fi

# ---- 检测 pip ----
PIP=""
for cmd in pip3 pip; do
    if command -v "$cmd" &>/dev/null; then
        PIP="$cmd"
        break
    fi
done
if [ -z "$PIP" ]; then
    echo "[ERROR] 未检测到 pip，请先安装。"
    exit 1
fi
echo "[OK] pip ($PIP)"

# ---- 检测 git ----
if ! command -v git &>/dev/null; then
    echo "[ERROR] 需要 git，请先安装。"
    exit 1
fi
echo "[OK] git"

# ---- 检测目标平台 ----
WORKBUDDY_DIR="${HOME}/.workbuddy/skills"
CODEX_DIR="${HOME}/.codex/skills"
INSTALL_WORKBUDDY=false
INSTALL_CODEX=false

case "$TARGET" in
    workbuddy)
        INSTALL_WORKBUDDY=true
        ;;
    codex)
        INSTALL_CODEX=true
        ;;
    all)
        INSTALL_WORKBUDDY=true
        INSTALL_CODEX=true
        ;;
    auto)
        if [ -d "${HOME}/.workbuddy" ]; then
            INSTALL_WORKBUDDY=true
            echo "[OK] 检测到 WorkBuddy (~/.workbuddy/)"
        fi
        if [ -d "${HOME}/.codex" ]; then
            INSTALL_CODEX=true
            echo "[OK] 检测到 Codex (~/.codex/)"
        fi
        if [ "$INSTALL_WORKBUDDY" = false ] && [ "$INSTALL_CODEX" = false ]; then
            echo "[INFO] 未检测到 WorkBuddy 或 Codex，默认安装到 WorkBuddy"
            INSTALL_WORKBUDDY=true
        fi
        ;;
    *)
        echo "[ERROR] 未知目标: $TARGET"
        echo "        可选: workbuddy | codex | all | auto"
        exit 1
        ;;
esac

echo ""

# ---- 克隆到临时目录 ----
TMP_DIR="${HOME}/.tmp/${SKILL_NAME}-install-$$"
mkdir -p "$(dirname "$TMP_DIR")"

echo "[1/5] 克隆仓库..."
git clone --depth 1 "$REPO" "$TMP_DIR"
echo "[OK] 克隆完成"

# ---- 安装 Python 依赖 ----
echo ""
echo "[2/5] 安装 Python 依赖 (pyyaml, jsonschema)..."
$PIP install --quiet pyyaml jsonschema 2>/dev/null || {
    echo "[WARN] 全局安装失败，尝试用户级安装..."
    $PIP install --user --quiet pyyaml jsonschema
}
echo "[OK] 依赖就绪"

# ---- 安装函数 ----
# 第一个目标用 mv（从临时目录移动），后续目标用 symlink 指向第一个，
# symlink 失败则复制。这样保持单一来源，更新时只需更新一处。
MAIN_INSTALL=""

install_to() {
    local target_name="$1"
    local target_parent="$2"
    local target_dir="${target_parent}/${SKILL_NAME}"

    echo ""
    echo "[3/5] 安装到 ${target_name}..."
    mkdir -p "$target_parent"

    # 如果已存在（目录或 symlink），备份
    if [ -e "$target_dir" ] || [ -L "$target_dir" ]; then
        BACKUP="${target_dir}.bak.$(date +%Y%m%d%H%M%S)"
        echo "[INFO] ${target_name} 已有旧版本，备份到: $BACKUP"
        mv "$target_dir" "$BACKUP" 2>/dev/null || rm -rf "$target_dir"
    fi

    if [ -z "$MAIN_INSTALL" ]; then
        # 第一个目标：移动临时目录
        mv "$TMP_DIR" "$target_dir"
        MAIN_INSTALL="$target_dir"
        echo "[OK] 已安装: $target_dir"
    else
        # 后续目标：优先 symlink，失败则复制
        if ln -s "$MAIN_INSTALL" "$target_dir" 2>/dev/null; then
            echo "[OK] symlink: $target_dir -> $MAIN_INSTALL"
        else
            echo "[INFO] symlink 不可用，改为复制..."
            cp -r "$MAIN_INSTALL" "$target_dir"
            echo "[OK] 已复制: $target_dir"
        fi
    fi
}

# ---- 执行安装 ----
if [ "$INSTALL_WORKBUDDY" = true ]; then
    install_to "WorkBuddy" "$WORKBUDDY_DIR"
fi
if [ "$INSTALL_CODEX" = true ]; then
    install_to "Codex" "$CODEX_DIR"
fi

# ---- 验证 ----
echo ""
echo "[4/5] 验证安装..."
if [ -n "$MAIN_INSTALL" ]; then
    cd "$MAIN_INSTALL"
    $PYTHON scripts/quick_validate.py . --mode quick 2>&1 | tail -5 || {
        echo "[WARN] 快速验证未完全通过，不影响安装。"
        echo "       建议手动运行: $PYTHON scripts/quick_validate.py . --mode release"
    }
fi

# ---- 完成 ----
echo ""
echo "[5/5] 安装完成！"
echo ""
echo "=================================="
echo "  安装成功"
echo "=================================="
echo ""
if [ "$INSTALL_WORKBUDDY" = true ]; then
    echo "  WorkBuddy: $WORKBUDDY_DIR/$SKILL_NAME"
fi
if [ "$INSTALL_CODEX" = true ]; then
    echo "  Codex:     $CODEX_DIR/$SKILL_NAME"
fi
echo ""
echo "快速开始:"
echo "  $PYTHON scripts/build_article.py your-article.md --output-dir out"
echo ""
echo "生成全标识图鉴:"
echo "  $PYTHON scripts/render_marker_showcase.py -o showcase.html"
echo ""
echo "完整验证:"
echo "  $PYTHON scripts/quick_validate.py . --mode release"
echo ""
if [ "$INSTALL_WORKBUDDY" = true ]; then
    echo "WorkBuddy 调用:"
    echo "  对话中输入 @skill:wechat-editorial-skill"
fi
if [ "$INSTALL_CODEX" = true ]; then
    echo "Codex 调用:"
    echo "  对话中输入 \$wechat-editorial-skill"
    echo "  或隐式触发（根据 description 自动匹配）"
fi
echo ""

# ---- 清理（仅清理临时目录，已 mv 的不会被影响）----
[ -d "$TMP_DIR" ] && rm -rf "$TMP_DIR" 2>/dev/null || true
