*This project has been created as part of the 42 curriculum by amakino.*

# Fly_in
An optimized multi-agent drone routing simulation system that achieves mathematical minimum turns while strictly adhering to complex physical and spatial constraints.

## Description
The goal of this project is to design and implement a highly efficient routing engine capable of navigating a fleet of autonomous drones from a designated `start_hub` to an `end_hub`. The simulation operates in discrete turns, where multiple drones can move simultaneously provided they do not violate connection capacities (`max_link_capacity`) or zone capacities (`max_drones`). The system gracefully handles distinct zone properties, including multi-turn restricted zones, priority paths, and blocked obstacles, minimizing the total operational time horizon without deadlocks.

## Instructions
This project utilizes a Python virtual environment (`venv`) managed seamlessly via a dedicated `Makefile` to guarantee absolute dependency isolation and clean executions.

### Prerequisites
* Python 3.10 or later
* `make` utility

### Setup and Installation
To automatically initialize the isolated virtual environment and install standard linter tools (`flake8`, `mypy`):
```bash
make install
```

### Execution
To execute the simulation routing with a map file:
```bash
make run MAP=maps/easy/01_linear_path.txt
```
*(Note: You can substitute the `MAP` variable with any valid map configuration file path).*

### Verification & Static Analysis
To run full test suites for style guidelines conformance and strict typing safety validation:
```bash
make lint
```

### Debugging Mode
To trigger line-by-line execution tracking with the Python native debugger (`pdb`):
```bash
make debug MAP=maps/easy/01_linear_path.txt
```

### Cleanup
To wipe out caches and local runtime objects:
```bash
make clean
```
To fully obliterate the active environment including the `venv` framework:
```bash
make fclean
```

## Technical Choices and Algorithm Strategy
### Time-Expanded Network Flow Architecture
Instead of utilizing standard greedy heuristics or traditional single-agent pathfinders (like A* or Dijkstra) which inherently struggle with dynamic multi-agent collisions and spatial temporal capacities, this system frames the entire execution space as a Time-Expanded Network Flow problem.

The network is structurally cloned across successive discrete layers representing increments of time ($t = 0, 1, 2, ...$). Spatial nodes are split into inbound (`_in`) and outbound (`_out`) capacities to regulate exact turn-by-turn max occupancy limits. Strategic waiting actions are naturally supported by drawing forward-directed temporal edges between identical locations across adjacent steps. Multi-turn transit properties (such as restricted zones taking 2 turns) are elegantly mapped via extended directed edges skipping intermediate time horizons.

### Optimal Routing Flow Recovery
The maximum throughput is resolved by maximizing network flows using a tailored Edmonds-Karp algorithm (utilizing Breadth-First Search to establish augmenting paths) traveling from a single virtual `SUPER_SRC` to a `SUPER_SINK` node. An iterative deepening search continuously expands the time horizon layer until the net maximum flow matches the exact total drone head-count (`nb_drones`), mathematically proving that the derived turn sequence achieves the global absolute minimum duration.

## Visual Representation Features
The simulation tracks and outputs comprehensive, structurally sound, space-separated movement strings for every active turn using the mandatory `D<ID>-<zone>` standard. For drones locked in multi-turn operations traversing into restricted territories, the intermediate flight paths are explicitly logged via the `D<ID>-<connection>` paradigm, ensuring peer reviewers can explicitly witness conflict-free scheduling metrics dynamically unfolding over terminal streams.

## Empirical Performance Benchmarks
Our Time-Expanded Flow engine consistently demolishes the official performance optimization benchmarks stipulated in the assignment criteria, matching or beating the strict Bonus targets:

| Map Categories | Official Benchmark Target | Our Solution Score | Operational Result |
| :--- | :--- | :--- | :--- |
| `easy/01_linear_path` | $\le$ 6 Turns | 4 Turns | Beaten |
| `easy/02_simple_fork` | $\le$ 8 Turns | 4 Turns | Beaten |
| `easy/03_basic_capacity` | $\le$ 6 Turns | 4 Turns | Beaten |
| `medium/01_dead_end_trap` | $\le$ 12 Turns | 8 Turns | Beaten |
| `hard/01_maze_nightmare` | $\le$ 30 Turns | 13 Turns | Beaten (Double Score) |
| `hard/03_ultimate_challenge` | $\le$ 45 Turns | 26 Turns | Beaten |
| `challenger/01_the_impossible_dream` | $\le$ 45 Turns (Record) | 43 Turns | 🎉 Bonus Clear |

## Resources and AI Usage Policy
### Reference Materials

[巡視船の航路を最適化で求める](https://qiita.com/SaitoTsutomu/items/e153db5ed89e5f28598d)

[github.com/Diogo-Serra/Fly-in](https://github.com/Diogo-Serra/Fly-in)

### Artificial Intelligence Declaration
In strict adherence to the peer learning principles outlined in Chapter II, Generative AI assistance was utilized transparently for the following scoped engineering workflows:
1. Docstring Standardization: Automating repetitive Python PEP 257 Google-style docstring layouts for comprehensive code compliance verification.
2. Linter Troubleshooting: Resolving complex static analyzer boundaries where global wildcards interacted incorrectly with sub-dependencies during automated testing (`make lint` vs virtual directories).
3. Edge Case Parsing: Hardening structural parsing parameters to robustly handle complex character scenarios (e.g., text isolation anomalies like string tokens embedded inside zone descriptors).
4. visualizer

---
*This project has been created as part of the 42 curriculum by amakino.*

# フライ・イン $Fly\_in$


複雑な物理的・空間的制約を厳密に遵守しながら、数理的な最小ターン数を達成する、最適化されたマルチエージェント・ドローンルーティング・シミュレーションシステム.

## 概要 $Description$
本プロジェクトの目的は、指定された `start_hub` から `end_hub` まで、自律型ドローンフリートを最も効率的に誘導するルーティングエンジンを設計・実装することです.
シミュレーションは離散的なターン単位で進行し、経路容量やゾーン容量 の制約を満たす限り、複数のドローンが同時に移動できます.
本システムは、2ターンを要する制限ゾーン $restricted$、優先経路 $priority$、進入不可の障害物 $blocked$ などの異なるゾーン特性を適切に処理し、デッドロックを起こすことなく総飛行ターン数を最小化します.

## 操作手順 $Instructions$
本プロジェクトでは、依存関係の完全な隔離とクリーンな実行を保証するため、`Makefile` によってシームレスに管理されるPython仮想環境 `venv\` を利用しています.

### 前提条件 $Prerequisites$
*Python 3.10 以降*  `make` ユーティリティ

### 環境構築とインストール $Setup and Installation$
隔離された仮想環境を自動的に初期化し、標準の静的解析ツール `flake8`, `mypy`をインストールするには、以下のコマンドを実行します:
```bash
make install
```

### シミュレーションの実行 $Execution$
マップファイルを指定してルーティングシミュレーションを実行するには、以下のコマンドを使用します:
```bash
make run MAP=maps/easy/01_linear_path.txt
```
* 注意: `MAP` 変数には、任意の有効なマップ設定ファイルのパスを指定できます$.

### コード規約・静的型チェックの検証 $Verification \& Static Analysis$
コーディング標準の遵守と厳格な型安全性の検証を一括で実行するには、以下のコマンドを使用します:
```bash
make lint
```

### デバッグモード $Debugging Mode$
Python組み込みのデバッガ `pdb\`を使用して、コードを1行ずつ追跡実行するには、以下のコマンドを使用します:
```bash
make debug MAP=maps/easy/01_linear_path.txt
```

### クリーニング $Cleanup$
キャッシュや一時ファイルを削除するには:
```bash
make clean
```
生成された `venv` 環境を含め、プロジェクトを完全に初期状態に戻すには:
```bash
make fclean
```

---
## 技術選定とアルゴリズム戦略 $Technical Choices and Algorithm Strategy$

### 時空間ネットワーク流アーキテクチャ $Time-Expanded Network Flow$
マルチエージェントの衝突や時空間的な容量制限の処理が本質的に困難な、貪欲法的なヘリスティクスや従来の単一エージェント経路探索（A*やダイクストラ法など）は採用していません. 本システムでは、実行空間全体を時空間ネットワーク流（Time-Expanded Network Flow）問題として定式化しています.ネットワークは、時間の経過 `t = 0, 1, 2,...`に応じて連続する離散的なレイヤーとして構造的に複製されます. 空間的なノードは、ターンごとの正確な最大収容数を制御するために、流入 `_in` と流出 `_out`の容量に分割されます. 同一地点での「戦略的待機」アクションは、隣接する時間ステップ間の同じ拠点間に順方向の未利用エッジを張ることで自然にサポートされます. 到着に2ターンを要する「制限ゾーン $restricted$」のようなマルチターン移動特性は、中間の時間軸をスキップして進む有向エッジを構築することでエレガントにマッピングされます.

### 最適経路の復元 $Optimal Routing Flow Recovery$

仮想的な単一の `SUPER_SRC` から `SUPER_SINK` ノードへ向かうネットワーク流量を、エドモンズ・カープ（Edmonds-Karp）アルゴリズム（幅優先探索を用いて増加パスを決定）によって最大化します. 反復深化探索を用いて、最大流量がドローンの総数 `nb_drones`$ と完全に一致するまで時間レイヤーを拡張し続けることで、得られるターンシーケンスが数学的にグローバルな絶対最小ターン数であることを証明します.


## 視覚的表現 $Visual Representation$
シミュレーションの実行時、すべての有効なターンにおけるドローンの移動ログが、規定の `D<ID>-<zone` 形式でスペース区切りで標準出力されます.
制限ゾーンへの移動中など、マルチターン移動のプロセスにあるドローンの飛行状態は `D<ID>-<connection` 形式で明示的に記録されるため、評価者は衝突のないスケジューリングが動的に展開される様子をターミナル上で明確に確認できます.


## 実証的パフォーマンスベンチマーク $Empirical Performance Benchmarks$
本システムの時空間ネットワーク流エンジンは、課題書に規定された公式の最適化ベンチマーク目標をすべて大幅に塗り替え、厳格なボーナス目標を完全に達成または超過しています:
| マップカテゴリ | 公式目標ターン数 | 本ソリューションのスコア | 結果 |
| :--- | :--- | :--- | :--- |
| `easy/01_linear_path` | 6ターン 以下 \ | 4ターン | 目標達成 $大幅短縮$ |
| `easy/02_simple_fork` | 8ターン 以下 \ | 4ターン | 目標達成 $大幅短縮$ |
| `easy/03_basic_capacity` | 6ターン 以下 \ | 4ターン | 目標達成 $大幅短縮$ |
| `medium/01_dead_end_trap` | 12ターン 以下 \ | 8ターン | 目標達成 $大幅短縮$ |
| `hard/01_maze_nightmare` | 30ターン 以下 \ | 13ターン | 目標達成 $ダブルスコア以上の圧勝$ |
| `hard/03_ultimate_challenge` | 45ターン 以下 \ | 26ターン | 目標達成 $大幅短縮$ |
| `challenger/01_the_impossible_dream` | 45ターン 以下 $公式記録$ \ | 43ターン | 🎉 $ボーナスクリア$  |

---
## 参考文献とAI利用方針 $Resources and AI Usage Policy$
### 参考文献 $References$

[巡視船の航路を最適化で求める](https://qiita.com/SaitoTsutomu/items/e153db5ed89e5f28598d)

[github.com/Diogo-Serra/Fly-in](https://github.com/Diogo-Serra/Fly-in)


###　AIの利用
1. Docstringの標準化: PythonのPEP 257に準拠したGoogleスタイルのdocstringレイアウトを自動化し、コードの完全なコンプライアンスを検証.
2. リンターのエラー回避: 自動検証時（`make lint`）に、グローバルワイルドカードが仮想環境内のサードパーティ製依存関係と誤って干渉する境界条件の解決.
3. エッジケースのパース堅牢化: ゾーン記述子内に文字列トークンが埋め込まれた複雑な文字列（`trap_a1` などの `_t` 誤爆トラップ）を頑健に分離するための解析パラメーターの強化.
4. visualizer