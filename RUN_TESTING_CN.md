# GART 运行与复现实验说明

项目主拓扑已经按论文改为 NSFNet、GEANT2、Renater 2010 和
Synthetic-300。原来的 Military 47 节点拓扑只保留在
`baseline/drl-or-s/`，不会再作为 GART 默认实验。

## 1. 论文拓扑

| 数据集 | 节点 | 物理链路 | 有向链路 |
|---|---:|---:|---:|
| NSFNet | 14 | 21 | 42 |
| GEANT2 | 23 | 36 | 72 |
| Renater 2010 | 43 | 56 | 112 |
| Synthetic-300 | 300 | 669 | 1,338 |

目录如下：

```text
topology/
├── nsfnet/
├── geant2/
├── renater2010/
└── synthetic300/
```

每个目录包含：

- `Topology.txt`：物理链路，每条链路由加载器转换为两个方向；
- `TM.txt`：可直接运行的流量矩阵；
- `metadata.json`：数据来源、论文计数和复现边界。

论文没有公开 Synthetic-300 的具体随机实例与种子，因此仓库提供固定种子、
精确满足 300 节点和 1,338 条有向链路的可重生成实例。公开的 23 节点
GEANT2 测量快照有 37 条物理链路，而论文写 36 条；仓库去掉最低容量、非桥接
的 `(6, 19)` 链路以严格匹配论文计数，并在元数据中记录该处理。

## 2. 安装

```bash
pip3 install -r requirements.txt
```

完整仿真还需要在 Linux 中安装 Mininet 和 Open vSwitch。

## 3. 训练

默认训练 NSFNet：

```bash
python3 -m gart.train \
  --dataset nsfnet \
  --traffic-intensity 0.7 \
  --interactions 100000 \
  --seed 1
```

输出为 `models/nsfnet/gart.pt`。其他数据集只需修改 `--dataset`：

```bash
python3 -m gart.train --dataset geant2 --traffic-intensity 0.3 --seed 1
python3 -m gart.train --dataset renater2010 --traffic-intensity 0.7 --seed 1
python3 -m gart.train --dataset synthetic300 --traffic-intensity 0.7 --seed 1
```

论文中每组实验使用种子 1-5 独立运行，并分别测试 0.3 轻负载和 0.7 重负载。
NSFNet/GEANT2 的仓库内 `TM.txt` 是可运行的确定性流量夹具；若要精确复现论文
流量，应从论文引用的大型官方数据包中抽取对应矩阵后替换。Renater 和
Synthetic-300 使用论文所述的 gravity 模型夹具。

## 4. 启动 Mininet 与服务

```bash
./start_suite.sh
```

默认启动 NSFNet。切换拓扑：

```bash
GART_TOPOLOGY=geant2 ./start_suite.sh
GART_TOPOLOGY=renater2010 ./start_suite.sh
```

默认模型路径自动变为 `models/<拓扑名>/gart.pt`。模型不存在时，路径服务会
带原因回退到 Dijkstra。

物理网卡混合模式：

```bash
GART_TOPOLOGY=nsfnet ./start_suite.sh eno1
```

## 5. 单独启动路径服务

```bash
python3 -m gart.path_service \
  --topo nsfnet \
  --algorithm gart \
  --model models/nsfnet/gart.pt
```

旧 DRL-OR-S/Military 只在 baseline 模式使用：

```bash
python3 -m gart.path_service \
  --topo Military \
  --algorithm baseline \
  --model baseline/drl-or-s/model/Military_mininet
```

## 6. 验证

```bash
python3 -m pytest -q
python3 tools/build_paper_topologies.py
git diff --exit-code -- topology
```

拓扑测试会检查节点连续性、连通性、无重复链路、流量矩阵尺寸以及论文中的
四组节点/链路计数。

## 7. 停止与日志

```bash
./stop_suite.sh
cat logs/path_service.log
cat logs/server_agent.stdout.log
cat logs/controllers.log
```
