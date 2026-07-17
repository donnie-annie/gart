# GART Routing Suite 运行与测试说明

本文档说明 GART 主实现的训练、启动、测试和常见排障方式。旧 DRL-OR-S
实现只作为比较基线保存在 `baseline/drl-or-s/`，不会出现在主代码路径中。

## 1. 目录结构

```text
gart/
├── gart/                         # GART 主实现和路径服务
├── topology/Military/            # 47 节点拓扑与流量矩阵
├── models/GART_Military/         # GART checkpoint 输出目录
├── baseline/drl-or-s/            # 旧算法、环境和模型权重
├── controller.py                 # Ryu 控制器应用
├── server_agent.py               # 根控制器服务与 Web/API
├── start_suite.sh                # 一键启动脚本
└── tests/                        # 自动化测试
```

## 2. 环境准备

建议使用 Linux/Ubuntu 测试环境。安装 Python 依赖：

```bash
cd gart
pip3 install -r requirements.txt
```

Mininet、Open vSwitch 与系统网络工具需要通过系统包管理器安装。验证关键
Python 依赖：

```bash
python3 - <<'PY'
import flask, networkx, numpy, torch
print("Python dependencies OK")
PY
```

## 3. 训练 GART

```bash
python3 -m gart.train \
  --topology topology/Military/Topology.txt \
  --traffic-matrix topology/Military/TM.txt \
  --traffic-intensity 0.7 \
  --interactions 100000 \
  --seed 1 \
  --output models/GART_Military/gart.pt
```

论文报告五次独立运行的平均值，因此复现实验时应分别使用种子 1 至 5。

## 4. 启动完整系统

```bash
./start_suite.sh
```

脚本依次启动：

1. `python3 -m gart.path_service`，端口 `8889`；
2. `server_agent.py`，服务端口 `6001`、Web 端口 `6009`；
3. Military 拓扑对应的 Ryu 控制器；
4. Military Mininet 拓扑和当前终端中的 Mininet CLI。

默认模型为 `models/GART_Military/gart.pt`。checkpoint 不存在或推理失败时，
服务会返回带原因字段的 Dijkstra 回退结果。

可覆盖运行参数：

```bash
PATH_SERVICE_PYTHON=/path/to/python \
PATH_SERVICE_MODEL=models/GART_Military/gart.pt \
ROUTING_ALGORITHM=gart \
SERVER_AGENT_ROUTE_MODE=hybrid \
./start_suite.sh
```

## 5. 混合物理交换机模式

```bash
./start_suite.sh eno1
```

该命令把 `eno1` 接入 `s1:port20`，并设置默认外部链路白名单
`EXTERNAL_LINK_PORTS=1:20`。如需自定义：

```bash
EXTERNAL_LINK_PORTS=1:20 ./start_suite.sh eno1
```

## 6. 单独启动路径服务

GART：

```bash
python3 -m gart.path_service \
  --topo Military \
  --port 8889 \
  --algorithm gart \
  --model models/GART_Military/gart.pt
```

比较旧基线时必须显式选择：

```bash
python3 -m gart.path_service \
  --topo Military \
  --port 8889 \
  --algorithm baseline \
  --model baseline/drl-or-s/model/Military_mininet
```

## 7. 自动化测试

运行全部测试：

```bash
python3 -m pytest -q
```

仅运行 GART 论文对齐与路径服务测试：

```bash
python3 -m pytest -q \
  tests/test_gart_paper_alignment.py \
  tests/test_gart_path_service_integration.py
```

## 8. 运行状态检查

```bash
cat logs/path_service.log
cat logs/server_agent.stdout.log
cat logs/controllers.log
curl http://127.0.0.1:6009/api/graph
```

检查端口：

```bash
ss -lntp | grep -E '6001|6009|8889'
```

## 9. 停止系统

```bash
./stop_suite.sh
```

如进程异常退出，可检查 `logs/*.pid` 和对应日志后再次运行停止脚本。

## 10. 常见问题

- **找不到 `gart.pt`**：先执行训练命令，或通过 `PATH_SERVICE_MODEL` 指向
  已训练 checkpoint。
- **缺少 PyTorch/PyG**：重新安装 `requirements.txt`，并确认当前启动脚本
  使用的 Python 与安装依赖的 Python 相同。
- **Mininet 权限错误**：从具备 sudo 权限的 Linux 终端启动。
- **路径服务返回 Dijkstra**：查看响应的 `fallback_reason` 与
  `logs/path_service.log`，确认 checkpoint、拓扑和动态链路特征是否完整。
- **端口被占用**：先运行 `./stop_suite.sh`，再检查是否有遗留进程。
