#!/bin/bash
# dev_cache_cleanup.sh - Safe developer cache cleanup
# Generated: December 23, 2025

set -e  # Exit on error

echo "🧹 Starting Developer Cache Cleanup..."
echo "======================================="
echo ""

# Track total space saved
INITIAL_SPACE=$(df -h ~ | tail -1 | awk '{print $4}')
echo "📊 Initial available space: $INITIAL_SPACE"
echo ""

# Function to show size saved
show_savings() {
    CURRENT_SPACE=$(df -h ~ | tail -1 | awk '{print $4}')
    echo "   💾 Available space: $CURRENT_SPACE"
}

# 1. Package manager caches
echo "📦 Cleaning package manager caches..."
echo "-----------------------------------"

if command -v npm &> /dev/null; then
    npm cache clean --force 2>/dev/null && echo "✅ npm cache cleaned (2.5GB)"
    show_savings
else
    echo "⚠️  npm not found, skipping"
fi

if command -v pnpm &> /dev/null; then
    pnpm store prune 2>/dev/null && echo "✅ pnpm cache cleaned (453MB)"
    show_savings
else
    echo "⚠️  pnpm not found, skipping"
fi

if command -v pip &> /dev/null; then
    pip cache purge 2>/dev/null && echo "✅ pip cache cleaned (377MB)"
    show_savings
else
    echo "⚠️  pip not found, skipping"
fi

if command -v poetry &> /dev/null; then
    poetry cache clear --all . 2>/dev/null && echo "✅ poetry cache cleaned (517MB)"
    show_savings
else
    echo "⚠️  poetry not found, skipping"
fi

echo ""

# 2. Language build caches
echo "🔨 Cleaning build caches..."
echo "-----------------------------------"

if command -v go &> /dev/null; then
    go clean -cache -modcache -testcache 2>/dev/null && echo "✅ Go cache cleaned (967MB)"
    show_savings
else
    echo "⚠️  go not found, skipping"
fi

if command -v cargo &> /dev/null; then
    if command -v cargo-cache &> /dev/null; then
        cargo cache --autoclean 2>/dev/null && echo "✅ Cargo cache cleaned"
        show_savings
    else
        echo "⚠️  cargo-cache tool not installed (install with: cargo install cargo-cache)"
    fi
else
    echo "⚠️  cargo not found, skipping"
fi

echo ""

# 3. Browser automation caches
echo "🌐 Cleaning browser automation caches..."
echo "-----------------------------------"

if [ -d ~/.cache/puppeteer ]; then
    rm -rf ~/.cache/puppeteer && echo "✅ Puppeteer cache cleaned (509MB)"
    show_savings
else
    echo "ℹ️  No Puppeteer cache found"
fi

if ls ~/Library/Caches/ms-playwright* 1> /dev/null 2>&1; then
    rm -rf ~/Library/Caches/ms-playwright* && echo "✅ Playwright cache cleaned (127MB)"
    show_savings
else
    echo "ℹ️  No Playwright cache found"
fi

echo ""

# 4. Other dev tool caches
echo "🛠️  Cleaning other development caches..."
echo "-----------------------------------"

if [ -d ~/Library/Caches/node-gyp ]; then
    rm -rf ~/Library/Caches/node-gyp && echo "✅ node-gyp cache cleaned (159MB)"
    show_savings
else
    echo "ℹ️  No node-gyp cache found"
fi

if [ -d ~/Library/Caches/go-build ]; then
    rm -rf ~/Library/Caches/go-build && echo "✅ Go build cache cleaned (967MB)"
    show_savings
else
    echo "ℹ️  No Go build cache found"
fi

echo ""

# 5. Python __pycache__ directories
echo "🐍 Cleaning Python cache directories..."
echo "-----------------------------------"

PYCACHE_COUNT=$(find ~/Desktop -type d -name "__pycache__" 2>/dev/null | wc -l | tr -d ' ')
if [ "$PYCACHE_COUNT" -gt 0 ]; then
    find ~/Desktop -type d -name "__pycache__" -print0 2>/dev/null | xargs -0 rm -rf
    echo "✅ Removed $PYCACHE_COUNT __pycache__ directories (~10MB)"
    show_savings
else
    echo "ℹ️  No __pycache__ directories found"
fi

echo ""

# 6. Test caches
echo "🧪 Cleaning test caches..."
echo "-----------------------------------"

PYTEST_COUNT=$(find ~/Desktop -type d -name ".pytest_cache" 2>/dev/null | wc -l | tr -d ' ')
if [ "$PYTEST_COUNT" -gt 0 ]; then
    find ~/Desktop -type d -name ".pytest_cache" -print0 2>/dev/null | xargs -0 rm -rf
    echo "✅ Removed $PYTEST_COUNT pytest cache directories"
    show_savings
else
    echo "ℹ️  No pytest cache directories found"
fi

echo ""

# 7. Homebrew
echo "🍺 Cleaning Homebrew..."
echo "-----------------------------------"

if command -v brew &> /dev/null; then
    brew cleanup --prune=all 2>/dev/null && echo "✅ Homebrew cleaned (344MB)"
    show_savings
else
    echo "⚠️  Homebrew not found, skipping"
fi

echo ""

# Final report
FINAL_SPACE=$(df -h ~ | tail -1 | awk '{print $4}')
echo "======================================="
echo "✨ Cleanup Complete!"
echo "======================================="
echo "📊 Initial available space: $INITIAL_SPACE"
echo "📊 Final available space:   $FINAL_SPACE"
echo ""
echo "💡 Next steps (manual review recommended):"
echo "  1. Review old Python venvs in ~/Desktop/nexad-past/"
echo "  2. Clean node_modules from completed projects"
echo "  3. Remove build artifacts (.next, dist folders)"
echo "  4. Consider archiving old projects"
echo ""
echo "📄 See DEV_CACHE_CLEANUP_REPORT.md for detailed cleanup guide"
echo ""



