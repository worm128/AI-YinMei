@echo off

set PYTHON=.\pydraw\Scripts\python.exe
set GIT=
set VENV_DIR=.\pydraw\
set COMMANDLINE_ARGS=--api --listen --no-gradio-queue --ckpt ./models/Stable-diffusion/realvisxlV30Turbo_v30TurboBakedvae.safetensors

call webui.bat
