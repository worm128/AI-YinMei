@echo off
chcp 65001 >nul
setlocal

rem ============================================================
rem  AI-YinMei 打包脚本（Nuitka standalone）
rem  在仓库根目录双击或执行： build.bat
rem  产物： build\api.dist\   —— 整个目录即为可分发的运行包
rem ============================================================

cd /d "%~dp0"

if not exist "config.yml" (
    echo [错误] 根目录没有 config.yml
    echo        它被 .gitignore 的 *.yml 规则排除，不在仓库里。
    echo        请先从整合包或自己的备份拷一份到本目录再打包。
    exit /b 1
)

where uv >nul 2>nul
if errorlevel 1 (
    echo [错误] 找不到 uv，请先安装： https://docs.astral.sh/uv/
    exit /b 1
)

rem 旧的 api.dist 会被覆盖，api.build 保留以复用编译缓存（ccache）
if exist "build\api.dist" rd /s /q "build\api.dist"

if exist "api.exe" (
    echo [错误] 根目录已有 api.exe，会和 Nuitka 的入口脚本名冲突，请先删掉。
    exit /b 1
)

echo [1/4] 同步打包依赖（build 组里的 nuitka）...
uv sync --group build
if errorlevel 1 goto fail

echo [2/4] Nuitka 编译中（首次约 10-15 分钟，之后走 ccache 约 1-3 分钟）...
uv run --group build python -m nuitka ^
    --standalone ^
    --mingw64 ^
    --windows-console-mode=force ^
    --include-data-files=config.yml=config.yml ^
    --output-dir=build ^
    api.py
if errorlevel 1 goto fail

if not exist "build\api.dist\api.exe" (
    echo [错误] 编译结束但没找到 build\api.dist\api.exe
    goto fail
)

echo [3/4] 复制外部可执行文件（mpv / song / accompany）...
set MISSING=
for %%F in (mpv.exe song.exe accompany.exe) do (
    if exist "%%F" (
        copy /y "%%F" "build\api.dist\" >nul
        echo    已复制 %%F
    ) else (
        set MISSING=1
        echo    未找到 %%F，跳过
    )
)
if defined MISSING (
    echo    注意：唱歌/念白依赖这些 exe，发布前请从整合包补齐到 build\api.dist\
)

echo [4/4] 创建运行时目录（代码里用的是工作目录相对路径）...
for %%D in (logs output porn) do (
    if not exist "build\api.dist\%%D" mkdir "build\api.dist\%%D"
)

echo.
echo ============================================================
echo  打包完成： build\api.dist\
echo.
echo  运行方式：进入 build\api.dist\ 再执行 api.exe
echo                （config.yml 已随包放在同目录，工作目录必须是那里）
echo.
echo  发布提示：build\api.dist\config.yml 里含 fastgpt 密钥等私有配置，
echo            对外分发前请先脱敏。
echo ============================================================
exit /b 0

:fail
echo.
echo [失败] 打包中断，请查看上方 Nuitka 输出。
exit /b 1
