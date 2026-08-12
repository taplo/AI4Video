# AI4Video

多路视频接入与智能布控分析平台。支持 GB28181 / RTSP、YOLO 小模型检测、OpenAI 兼容大模型复核、多边形布控与结构化报警。

**开源协议：** MIT License，可自由商用。详见 `LICENSE`。

---

## 功能

- 视频接入：RTSP / GB28181 拉流，ZLMediaKit 转发，ONVIF 发现
- 智能分析：YOLO-PyTorch / ONNX / OpenVINO 小模型 + 可选大模型复核
- 布控报警：多边形区域、5 种后处理规则（入侵/越线/方向/密度/滞留）
- 运维：控制面板监控、流媒体启停、录像、多语言（7 种）
- 安全：认证加固、审计日志、请求限流、CSRF 保护
- API：OpenAPI/Swagger 文档（DEBUG 模式）

---

## 环境要求

- Python 3.12+
- FFmpeg（PATH 或 `config.json` 配置）
- ZLMediaKit（流媒体，端口与 `config.json` 一致）
- GPU 可选

---

## 安装

### Linux

```bash
# 进入 ZLMediaKit 目录
cd zlm/bin.x86.gcc9.4  # 或 zlm/bin.arm.gcc9.4

# 确保可执行权限
chmod +x ai4video_zlm

# 如果启动失败，安装依赖
sudo apt update
sudo apt install -y libsrtp2-1

# 下载并安装 libssl1.1（Ubuntu 20.04+）
wget http://security.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2.24_amd64.deb
sudo dpkg -i libssl1.1_1.1.1f-1ubuntu2.24_amd64.deb
sudo apt -f install
```

### 安装 Python 依赖

```bash
# 推荐使用 uv（快速依赖管理）
uv sync

# 或使用 pip
pip install -r requirements.txt
```

---

## 配置

### 环境变量

创建 `.env` 文件（已在 `.gitignore` 中）：

```env
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 应用配置

编辑 `config.json` 配置端口、ZLMediaKit、FFmpeg 等。
编辑 `settings.json` 配置界面品牌和多语言。

启动配置页保存后多数项热更新生效；改管理端口或调试日志需重启服务。

---

## 快速开始

```bash
# 使用 uv（推荐）
uv run python manage.py runserver 0.0.0.0:10001

# 或直接运行
python manage.py runserver 0.0.0.0:10001
```

浏览器访问 `http://<host>:10001/`，默认账号 `admin`。

---

## 使用顺序

```
视频管理 → 小模型 → 大模型 → 业务算法 → 布控管理 → 启动分析 → 报警管理
```

1. 添加摄像头并确认拉流正常
2. 上传/配置小模型（流程 1/3）和大模型（流程 2/3）
3. 创建业务算法，在布控页画区域并绑定算法
4. 点击「启动分析」（**重启服务后需手动再点**）
5. 在报警管理查看结果

> 只有业务算法规则命中才会报警；单纯检测到目标或画面运动不会产生报警记录。

---

## 开发

### 运行测试

```bash
# 使用 uv（推荐）
uv run pytest tests/ -v

# 带覆盖率
uv run pytest tests/ --cov=app --cov-report=term-missing

# 运行验证脚本
pwsh scripts/verify.ps1
```

### 测试覆盖率

当前覆盖率：30%（448 测试通过）

覆盖率门槛：29%（在 `pytest.ini` 和 CI 中强制执行）

> 注：硬件依赖模块（GPU、SIP、ZLMediaKit）无法在 CI 中有效 mock，覆盖率上限约 30%。

### CI/CD

GitHub Actions 自动运行：
- pytest + 覆盖率检查
- makemigrations --check（迁移漂移检测）
- flake8 lint

### 代码审查

```bash
# 查看代码审查报告
cat .planning/phases/07-.../07-REVIEW.md
```

---

## 项目结构

```
AI4Video/
├── app/                    # Django 应用
│   ├── views/              # 视图层（AlgorithmView, StreamView, etc.）
│   ├── analysis/           # 分析引擎（ONNX, OpenVINO, PyTorch）
│   ├── services/           # 业务服务
│   ├── utils/              # 工具类（GlobalUtils, ZLMediaKitApi, etc.）
│   └── models.py           # 数据模型（含 AuditLog）
├── framework/              # Django 框架配置
├── tests/                  # 测试文件（448 测试）
├── zlm/                    # ZLMediaKit 二进制
├── config.json             # 应用配置
├── settings.json           # 界面品牌配置
├── pytest.ini              # pytest 配置
├── manage.py               # Django 管理脚本
└── requirements.txt        # Python 依赖
```

---

## 常见问题

| 问题 | 处理 |
|------|------|
| 没有报警 | 确认拉流正常、布控已绑算法、已启动分析、检测类别匹配 |
| 改配置不生效 | 布控/算法可热更新；换小模型需重启分析；改端口需重启服务 |
| 端口占用 | 结束残留 `python.exe` 后重新启动 |
| 数据库错误 | 检查 `ai4video.sqlite3` 文件权限，WAL 模式需写入权限 |

---

## 版本历史

### v1.0 (2026-08-12)

- 项目重命名 rebucca → AI4Video
- ONNX 模型自动检测和输入自动 resize
- 安全加固（认证绕过修复、DEBUG 环境控制、CSRF）
- 测试体系建设（448 测试，pytest 框架）
- 依赖升级（Django 5.2.17）
- 审计日志和请求限流
- OpenAPI/Swagger API 文档
- 覆盖率门槛（30%）和 CI 迁移漂移检查

详见 [v1.0 里程碑文档](.planning/milestones/v1.0-ROADMAP.md)。

---

## 日志

日志目录：`log/`

版本号见 `framework/settings.py`
