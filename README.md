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
* (Optional for GUI) `tkinter` system package (e.g., `sudo apt install python3-tk` on Debian/Ubuntu)

### Setup and Installation
To automatically initialize the isolated virtual environment and install standard linter tools (`flake8`, `mypy`):
```bash
make install
```

### Execution
To execute the simulation routing with a map file:
`make run MAP=maps/easy/01_linear_path.txt`

You can also run the program directly with python to use additional flags:
`python3 main.py <map_file_path> [options]`

**Available Options:**
*   `--2D`: Launches the ultra-fast 2D fleet telemetry visualizer (Tkinter).
*   `--3D`: Launches the 3D spatial map canvas visualizer (Matplotlib).
*   `--capacity-info`: Displays turn-by-turn detailed network capacity usage (Zone and Connection occupancy). *Note: This feature was proactively implemented to demonstrate dynamic state validation.*

### Example Input and Expected Output
**Example Map Input (`maps/easy/03_basic_capacity.txt`):**
```text
nb_drones: 4
start_hub: start [0, 0]
hub: bottleneck [2, 0] (max_drones=2)
hub: wide_area [4, 0] (max_drones=3)
end_hub: goal [6, 0]
```
**Expected Simulation Output:**
```text
D3-bottleneck D4-bottleneck
D1-bottleneck D2-bottleneck D3-wide_area D4-wide_area
D1-wide_area D2-wide_area D3-goal D4-goal
D1-goal D2-goal
```

connection: start-bottleneck
connection: bottleneck-wide_area (max_link_capacity=2)
connection: wide_area-goal

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

[【Matplotlib入門⑧】3次元プロット入門（3D折れ線・散布図・曲面）](https://zenn.dev/haruhiro1020/articles/b9e73c18cd63c2)

[Pythonで3Dの「動く立方体」を作る | 外部モジュールなし | python | tkinter |](https://note.com/__init__4335/n/nab258ff741a0)

[python tkinterGUIへの埋め込みmatplotlibで3Dフィギュアをプロット](https://qiita.com/taiko1/items/ed9becf5110829adb401)

[エドモンズ・カープのアルゴリズム](https://ja.wikipedia.org/wiki/%E3%82%A8%E3%83%89%E3%83%A2%E3%83%B3%E3%82%BA%E3%83%BB%E3%82%AB%E3%83%BC%E3%83%97%E3%81%AE%E3%82%A2%E3%83%AB%E3%82%B4%E3%83%AA%E3%82%BA%E3%83%A0)

[matplotlib 入門](https://qiita.com/Shmwa2/items/8f0d337c0bfb75a8716f)

[最大フロー問題](https://ja.wikipedia.org/wiki/%E6%9C%80%E5%A4%A7%E3%83%95%E3%83%AD%E3%83%BC%E5%95%8F%E9%A1%8C)

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

### 例
**Example Map Input (`maps/easy/03_basic_capacity.txt`):**
```text
nb_drones: 4
start_hub: start 0, 0
hub: bottleneck 2, 0 [max_drones=2]
hub: wide_area 4, 0 [max_drones=3]
end_hub: goal 6, 0
```
**Expected Simulation Output:**
```text
D3-bottleneck D4-bottleneck
D1-bottleneck D2-bottleneck D3-wide_area D4-wide_area
D1-wide_area D2-wide_area D3-goal D4-goal
D1-goal D2-goal
```

### lint
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
本システムでは、実行空間全体を時空間ネットワーク流（Time-Expanded Network Flow）問題として定式化しています.ネットワークは、時間の経過 `t = 0, 1, 2,...`に応じて連続する離散的なレイヤーとして構造的に複製されます. 空間的なノードは、ターンごとの正確な最大収容数を制御するために、流入 `_in` と流出 `_out`の容量に分割されます. 同一地点での「戦略的待機」アクションは、隣接する時間ステップ間の同じ拠点間に順方向の未利用エッジを張ることで自然にサポートされます. 到着に2ターンを要する「制限ゾーン $restricted$」のようなマルチターン移動特性は、中間の時間軸をスキップして進む有向エッジを構築することでエレガントにマッピングされます.

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

[【Matplotlib入門⑧】3次元プロット入門（3D折れ線・散布図・曲面）](https://zenn.dev/haruhiro1020/articles/b9e73c18cd63c2)

[Pythonで3Dの「動く立方体」を作る | 外部モジュールなし | python | tkinter |](https://note.com/__init__4335/n/nab258ff741a0)

[python tkinterGUIへの埋め込みmatplotlibで3Dフィギュアをプロット](https://qiita.com/taiko1/items/ed9becf5110829adb401)

[エドモンズ・カープのアルゴリズム](https://ja.wikipedia.org/wiki/%E3%82%A8%E3%83%89%E3%83%A2%E3%83%B3%E3%82%BA%E3%83%BB%E3%82%AB%E3%83%BC%E3%83%97%E3%81%AE%E3%82%A2%E3%83%AB%E3%82%B4%E3%83%AA%E3%82%BA%E3%83%A0)

[離散最適化基礎論 (第5回) 最大流問題：Edmonds-Karpのアルゴリズム 2023年11月7日](https://www.youtube.com/watch?v=q09kUcJrY00)

[matplotlib 入門](https://qiita.com/Shmwa2/items/8f0d337c0bfb75a8716f)

###　AIの利用
1. Docstringの標準化: PythonのPEP 257に準拠したGoogleスタイルのdocstringレイアウトを自動化し、コードの完全なコンプライアンスを検証.
2. リンターのエラー回避: 自動検証時（`make lint`）に、グローバルワイルドカードが仮想環境内のサードパーティ製依存関係と誤って干渉する境界条件の解決.
3. エッジケースのパース堅牢化: ゾーン記述子内に文字列トークンが埋め込まれた複雑な文字列（`trap_a1` などの `_t` 誤爆トラップ）を頑健に分離するための解析パラメーターの強化.
4. visualizer

---
## コード詳細解説 (Code Architecture)

### 1. `connection.py` - 拠点間接続の定義
このファイルでは、シミュレーション空間における2つのゾーン（拠点）を結ぶ**双方向の経路（エッジ）**を定義しています。

#### クラス: `Connection`
Pythonの `dataclasses` モジュールを使用し、データを保持することに特化したクリーンでオブジェクト指向的なクラス設計を行っています。

* **`zone1: str` / `zone2: str`**
    * 接続されている2つのゾーンの名前を保持します。パーサー（`map_parser.py`）によって読み込まれた情報が格納されます。
* **`max_link_capacity: int = 1`**
    * この接続（経路）を**同時に通過できるドローンの最大数**を制限するためのプロパティです。デフォルト値は課題の仕様通り `1` に設定されています。
    * この値は `pathfinder.py` で時空間ネットワークの最大流エッジ容量を設定する際、および `simulator.py` での容量チェックで厳密に参照されます。

#### 設計の意図と制約へのアプローチ
* **双方向性の担保**: 
    `zone1` と `zone2` に明確な「始点」「終点」の区別をつけず、データ構造としてフラットに持つことで、無向グラフ（双方向の移動が可能）としての役割をシンプルに表現しています。
* **データのカプセル化**:
    不必要なロジックを持たせないことで、単なる「接続データ構造」として独立させ、依存関係を最小限に抑えています。

---
### 2. `drone.py` - ドローンの状態管理

このファイルでは、シミュレーション内を自律飛行する個々のドローンの状態を管理するクラスを定義しています。

### クラス: `Drone`
各ドローンが「今どこにいるのか」「どこに向かっているのか」「あと何ターンで到着するのか」という、動的な時間経過に伴う状態をカプセル化しています

* **`id_num: int`**
    * ドローンを一意に識別するための識別番号（ID）です（例: 1, 2, 3...）。
* **`current_zone: str`**
    * ドローンが現在位置するゾーンの名前、または移動中のコネクション名（例: `start` や `hub-roof1`）を保持します。
* **`target_zone: Optional[str] = None`**
    * 移動中の目的地となるゾーンの名前を保持します。停止中や1ターンで移動が完了する場合は `None` になります。
* **`turns_to_arrive: int = 0`**
    * 目的地に到着するまでにかかる残りターン数です。

### プロパティ (Property)

* **`name`**
    * 課題の出力仕様で厳密に指定されている `D<ID>` 形式の文字列（例: `D1`）を動的に生成して返します。
* **`is_in_flight`**
    * ドローンが現在「制限ゾーン（2ターンを要するゾーン）」などへの移動中で、空中（コネクション上）に滞在しているかどうかを判定するブール値です。`target_zone` が設定されており、かつ `turns_to_arrive` が 0 より大きい場合に `True` となります。

### 設計の意図と制約へのアプローチ
* **制限ゾーン（2ターン移動）のモデル化**: 
    1ターンで移動が終わる通常ゾーンとは異なり、2ターンかかる移動では「1ターン目はコネクション上にいる」という状態を表現する必要があります。このクラスでは `turns_to_arrive` を持たせることで、「残りの飛行時間」をシミュレーター側からカウントダウンできるように設計されています。これにより、複雑な時空間の移動状態を破綻なく管理できます。

---
### 3. `main.py` - エントリーポイント
このファイルは、ドローンルーティングシミュレーション全体の実行フローを制御するメインスクリプトです。

### 主な処理フロー
各ドローンが「今どこにいるのか」「どこに向かっているのか」「あと何ターンで到着するのか」という、動的な時間経過に伴う状態をカプセル化しています

* 1. **引数の検証**: コマンドライン引数からマップファイルのパスを受け取ります。指定がない場合は使い方（Usage）を表示して終了します。
* 2. **データのパース**: 指定されたマップファイルを読み込み、検証し、プログラムで扱いやすい `MapData` オブジェクトに変換します。
* 3. **初期化**: パースされた構造データ（`MapData`）を基に、シミュレーター（状態管理）とパスファインダー（経路探索）を初期化します。
* 4. **シミュレーションの実行**: `simulator.run(pathfinder)` を呼び出し、ターンごとの経路探索と移動処理を実行・出力します。
* 5. **ビジュアライザーの起動 (Visualizer)**: シミュレーションが正常に完了し、スケジュールが生成された場合、GUIビジュアライザーを起動します。
* 6. **エラーハンドリング**: 実行中に発生したあらゆる例外（パースエラー、容量オーバー、経路探索失敗など）を捕捉し、標準エラー出力（`stderr`）に分かりやすいエラーメッセージを表示して安全にプログラムを終了します（`sys.exit(1)`）。

---
### 4. `map_data.py`　- マップデータの統合コンテナ
このファイルは、パーサーによって読み込まれたマップの全構成要素をひとまとめにして保持し、シミュレーターや経路探索アルゴリズムに渡すためのデータコンテナ（Data Transfer Object）を定義しています。

#### クラス: `MapData`
Pythonの `@dataclass` を活用し、不変（イミュータブル）な構成データとしてマップ全体の状態を安全に保持します。

* **属性 (Attributes)**
    * `nb_drones`: シミュレーションに参加するドローンの総数。
    * `start_hub` / `end_hub`: 全ドローンの出発地点と最終目的地となる特殊なゾーン（`Zone` オブジェクト）。
    * `zones`: ゾーン名をキー、`Zone` オブジェクトを値とする辞書。素早いゾーン情報の検索（$O(1)$）を可能にします。
    * `connections`: マップ内に存在する全接続（`Connection` オブジェクト）のリスト。
    * `graph`: ゾーン名をキーとし、隣接するゾーン名とその接続情報のタプルをリストとして保持する**隣接リスト（Adjacency List）**。

#### `__post_init__` によるグラフの自動構築
* データクラスの初期化直後に自動で呼び出される `__post_init__` メソッドを利用し、フラットな `connections` リストから**隣接リスト形式のグラフ (`self.graph`) を事前計算（Precompute）**しています。
* 双方向グラフであるため、`zone1` から `zone2`、`zone2` から `zone1` の両方の向きでエッジを追加しています。

#### 設計の意図と制約へのアプローチ
* **探索アルゴリズムの最適化**: 
    経路探索（`pathfinder.py`）において、あるゾーンから移動可能な隣接ゾーンを毎ターン計算するのは非常にコストがかかります。初期化時に隣接リストを構築しておくことで、探索時の計算量とメモリ削減（空間計算量 $O(V + E)$）しています。
* **データとロジックの分離**:
    このクラスはあくまで「状態の保持」に徹しており、状態を変更するようなメソッドを持たせません。これにより、後続のモジュールが意図せずマップ構造を破壊してしまうバグを未然に防いでいます。

### 5. `map_parser.py` - マップ定義ファイルの解析 (Parser)

このファイルは、テキスト形式で提供されるマップの設計図を読み込み、バリデーション（構文・意味チェック）を行いながら、プログラム内で利用可能な `MapData` オブジェクトを構築するパーサーです。

#### クラス: `MapParser`
入力ファイルを1行ずつ読み込み、正規表現や文字列操作を用いて要素を分解・検証します。

* **メイン処理: `parse` メソッド**
    * ファイルを走査し、空白行やコメント（`#`）を無視します。
    * 先頭が必ず `nb_drones:` であることを検証し、その後 `hub`, `start_hub`, `end_hub`, `connection` などの各プレフィックスに応じて専用のパース処理（`_parse_zone` など）に振り分けます。
* **メタデータの抽出: `_extract_metadata`**
    * 必須情報（名前や座標など）と、角括弧 `[...]` で囲まれたオプションのメタデータ（`zone=restricted`, `max_drones=2`, `color=red` など）を分離し、辞書形式に変換する堅牢なヘルパーメソッドです。
* **ゾーンとコネクションの解析: `_parse_zone` / `_parse_connection`**
    * ゾーンの座標が整数であるか、名前にハイフン（`-`）が含まれていないか（接続表現との衝突防止）をチェックします。
    * コネクションの定義において、存在しないゾーンが指定されていないか、同じ接続が重複して定義されていないかを検証します。

#### 設計の意図と制約へのアプローチ
* **フェイルファスト (Fail-Fast) 原則の徹底**:
    シミュレーションの途中で未知のエラーによるクラッシュを防ぐため、**「少しでも構文や論理がおかしい場合は、エラーが発生した行番号と具体的な理由（例外内容）を即座に表示してプログラムを終了させる」**ように設計されています。
* **堅牢なエラーハンドリング**:
    不正な文字、負の容量値、スタート・エンドハブの欠落または重複など、考えられるあらゆるエッジケースに対して `ValueError` を投げることで、プロジェクト要件である「明確で情報量の多いエラーメッセージの出力」を完璧に満たしています。

---
### 6. `pathfinder.py` - 最適経路探索アルゴリズム (Pathfinder)

このファイルは、本プロジェクトにおける**コア**です。単なる経路探索ではなく、複数のドローンが互いに衝突・渋滞することなく、かつ数学的に証明可能な「最小ターン数」でゴールに到達するための高度なアルゴリズムが実装されています。

#### コアアルゴリズム: 時空間ネットワーク流 (Time-Expanded Network Flow)
A* (A-star) やダイクストラ法のような単一エージェント向けの経路探索手法では、「他のドローンによる道の占有」や「容量制限による待機」といった動的なマルチエージェントの衝突回避を最適に解くことが困難です。
この課題を解決するため、本プログラムでは空間グラフに「時間($t$)」の次元を掛け合わせた**「時空間ネットワーク（Time-Expanded Graph）」**を構築し、そこへ**「最大フロー問題（Maximum Flow Problem）」**を適用するアプローチをとっています。

#### 1. グラフの構築プロセス (`build_network`)
時間を $t=0, 1, 2, \dots$ と離散化し、各時間ごとに空間（マップ）を複製して層（レイヤー）を作ります。

* **ゾーン容量（`max_drones`）の厳密な制御（ノード分割）**:
  フローネットワークにおいて「頂点の容量」を表現するため、各ゾーンを `in_node`（入口）と `out_node`（出口）の2つに分割し、その間に `max_drones` を上限容量とする有向エッジを張ります。これにより、ゾーン内に規定数以上のドローンが滞在できない物理制約をグラフ構造として保証します。
* **「待機（Wait）」のモデル化**:
  ある時刻 $t$ の出口 (`_t_out`) から、次の時刻 $t+1$ の同じゾーンの入口 (`_t+1_in`) に対して有向エッジを張ります。これにより、ドローンが「空きができるまでその場で待つ」という戦略的行動をアルゴリズムが自然に選択できるようになります。
* **移動とコストのモデル化（`max_link_capacity`）**:
  異なるゾーン間の移動は、コネクションの容量を上限とする有向エッジで表現します。
  通常（normal）や優先（priority）ゾーンへの移動は時刻 $t$ から $t+1$ へエッジを張りますが、**制限（restricted）ゾーンへの移動は時刻 $t$ から $t+2$ へエッジを飛ばして張ります**。これにより、2ターンかかる移動が時空間上で正確に表現されます。

#### 2. 最大流の計算 (`edmonds_karp`, `_bfs`)
* 全ドローンの出発点となる仮想的な「スーパーソース (`SUPER_SRC`)」と、到着点となる「スーパーシンク (`SUPER_SINK`)」を配置します。
* **エドモンズ・カープ（Edmonds-Karp）アルゴリズム**:
  幅優先探索（BFS）を用いて増加パス（Augmenting Path）を繰り返し見つけ、スーパーソースからスーパーシンクへ「水（ドローン）」を流し込みます。ネットワークの制約（エッジ容量）が空間の物理制約と完全に一致しているため、流れた水量は「安全にゴールできたドローンの数」と等しくなります。

#### 3. 最小ターン数の証明（反復深化） (`solve`)
* ターン数（`total_turns`）を1から順に少しずつ増やしながら、都度グラフを構築し直して最大流を計算します。
* 最大流（ゴールできた数）がドローンの総数（`nb_drones`）と一致した瞬間、探索を終了します。**これが数学的に証明された「絶対最小ターン数」**となります（これより少ないターンでは全ドローンを流し切る物理的容量が存在しないため）。

#### 4. 経路の復元 (Flow Decomposition)
* フローが流れ終わった後の「残余グラフ（Residual Graph）」を解析し、どのドローン（ID）が、どの時刻に、どのゾーンを通過したかという具体的なスケジュール（辞書型データ `self.schedule`）に変換します。
* 制限ゾーン（2ターン移動）へ向かったドローンに対しては、中間ターンにおいて `zoneA-zoneB` という**コネクション上の滞在状態（in-flight）**を出力するための補完処理もここで行われます。

#### 設計の意図と成果
このアーキテクチャにより、局所的な渋滞回避（ヒューリスティクス）ではなく、**「大域的最適解（Global Optimum）」**を常に導き出すことができます。これが、ハードマップやチャレンジャーマップにおいて、公式ベンチマークを大幅に上回るスコアを叩き出せる最大の理由です。

### 7. `simulator.py` - シミュレーション実行・状態管理エンジン

このファイルは、パスファインダーが作成した移動スケジュールに従って実際にドローンを動かし、課題のルール（容量制限など）が厳密に守られているかをターンごとに検証しながら進行する「審判（ルールエンフォーサー）」の役割を担います。

#### クラス: `Simulator`
現在のターン数、各ドローンの状態リスト、各ゾーンの現在の滞在人数（`zone_occupancy`）など、時々刻々と変化する「動的な状態」を一元管理します。

* **状態の初期化 (`__init__`)**:
    シミュレーション開始時、すべてのドローンを生成し、一斉に `start_hub` に配置します。

* **移動と検証 (`run_turn`)**:
    * 辞書形式で渡された移動予定（`moves`）を基に、1ターンの移動処理を実行します。まず移動元ゾーンの滞在人数を減らし、次に移動先ゾーンの滞在人数を増やします。
    * **容量チェック**: 移動先が `start_hub` や `end_hub`（これらは容量無制限の例外）でない場合、そのゾーンの `max_drones` を超えないかをチェックします。もし超過する移動があれば、即座にカスタム例外 `CapacityExceededError` を発生させます。
    * **フライト（空中）状態の処理**: ドローンの現在地や目的地がゾーン名ではなく「コネクション名（例: `A-B`）」である場合（制限ゾーンへの2ターン移動の途中など）、ゾーンの収容人数（`zone_occupancy`）にはカウントしないよう特別にハンドリングし、空間上の整合性を保ちます。

* **メインループ (`run`)**:
    全ドローンがゴールに到達する（`is_finished() == True`）までループを回します。
    ターンの移動結果を課題指定のフォーマット（例: `D1-roof1 D2-corridorA`）で標準出力に出力します。また、追加の `show_capacity` フラグが有効な場合は、ターンごとのリアルタイムなネットワーク容量使用状況を出力します。

#### 設計の意図と制約へのアプローチ
* **関心の分離 (Separation of Concerns)**:
    「どう動くか（経路計画）」は `pathfinder.py` に完全に任せ、この `simulator.py` は「その動きが物理法則（ルール）に反していないか」の検証と実行に専念させています。これにより、仮に探索アルゴリズム側にバグがあっても、シミュレーターが確実にルール違反を検知できる「フェイルセーフ・二重チェック」の強固な設計を実現しています。

### 8. `visualizer.py` - グラフィカル・フリート・テレメトリ・ビジュアライザー

このファイルは、Tkinterフレームワークを使用し、ドローンフリートの動的な運行状況を直感的にモニタリングできるGUI（グラフィカル・ユーザー・インターフェース）ビジュアライザーを定義しています。プロジェクトのボーナス要件を満たすだけでなく、ピアレビューでの説得力を劇的に高める機能を備えています。

#### クラス: `Visualizer`
マップのトポロジー、各ゾーンの制約、ドローンの時系列の位置データをCanvas上に動的にレンダリングします。

* **アスペクト比を維持した動的スケーリング (`_calculate_bounds`, `_get_coords`)**:
    マップごとにバラバラなノードのX/Y座標を自動的に解析し、画面の解像度（1000x750）に合わせて適切な比率でCanvas中央に自動配置します。特に、Y座標がすべてゼロ（一直線の直線マップ）のようなエッジケースであっても、`range_y == 1.0` の判定により画面の垂直中央（`h / 2`）に整列させ、ノードが画面上部に張り付いてしまうレイアウト崩れを防いでいます。
* **状態のリアルタイム更新 (`refresh_view`)**:
    * **ゾーンの可視化**: ゾーンのメタデータに基づいたカラー（`colour` プロパティ）を正確に反映し、`start_hub`（緑）や `end_hub`（黄）などの重要拠点をひと目で識別できるようにしています。文字がノードやドローンと重ならないよう、テキスト描画のY座標を上に `35` ピクセルずらす工夫が施されています。
    * **ドローンのクラスター配置（渋滞の可視化）**: 1つのゾーンに複数のドローンが同時滞在している（`max_drones > 1`）場合、ドローンの円が完全に重なって見えなくなるのを防ぐため、三角関数（`cos`/`sin`）による動的な角度計算を行い、同じノードの周囲に軌道を描くように分散（クラスター配置）して描画します。
* **高機能なステップ制御 (`next_turn`, `prev_turn`)**:
    * **1ターン進む (`next_turn`)**: スケジュール辞書からそのターンの動きを1ステップ読み進め、ドローンの座標を更新します。
    * **1ターン戻る (`prev_turn`)**: 「動きを巻き戻して見たい」というレビューアーの要望に応えるための強力な機能です。状態管理を破綻させないよう、内部的には一度すべてのドローンを初期位置（`start_hub`）に戻した上で、目的のターンまでの移動スケジュールを一瞬で高速に再適用（リプレイ）することで、バグを発生させずに完全な過去の状態を1タップで復元します。

---
### 9. `zone.py` - ゾーン（拠点）の性質とデータ構造

このファイルは、マップを構成する各ノード（拠点）のデータ構造と、それぞれのゾーンが持つ固有の「性質（タイプ）」を定義しています。

#### 列挙型: `ZoneType` (Enum)
ゾーンの種類を文字列の Enum（列挙型）として定義し、タイポ（打ち間違い）によるバグを防ぎつつ、アルゴリズム側で移動コストを判定する際の明確な基準を提供しています。

* **`NORMAL`**: 標準のゾーン。移動にかかるコストは1ターンです。
* **`BLOCKED`**: 進入不可能な障害物ゾーン。パスファインダーのグラフ構築時にこのノードは完全に無視（除外）され、ドローンが通過することは一切ありません。
* **`RESTRICTED`**: 制限ゾーン。到着までに「2ターン」を要する特殊なゾーンです。パスファインダーにおいて、時間レイヤーを1つ飛ばしてエッジを張る（$t \to t+2$）トリガーとして機能します。
* **`PRIORITY`**: 優先ゾーン。移動コストは1ターンですが、他の経路よりも優先して選ばれるべき経路として機能します。

#### クラス: `Zone`
各ゾーンの静的な属性（名前、座標、容量など）を管理するデータクラス（DTO）です。

* **属性 (Attributes)**
    * `name`: ゾーンの一意な識別名。
    * `x`, `y`: マップ上での空間的な座標。ビジュアライザー（GUI）でノードを描画する際の配置計算に直接使用されます。
    * `zone_type`: 上記の `ZoneType` を保持します（デフォルトは `NORMAL`）。
    * `max_drones`: そのゾーンに同時に滞在できる最大ドローン数（デフォルトは 1）。シミュレーターでの衝突検知や、パスファインダーでの入口・出口ノード間のエッジ容量として使われる極めて重要な値です。
    * `colour`: ビジュアライザーでノードを色分けして描画するためのオプション情報です。

#### 設計の意図と制約へのアプローチ
* **型安全性（Type Safety）の確保**:
    ゾーンのタイプを単なる文字列ではなく `Enum` クラスとして定義することで、Mypyなどの静的型チェッカーによる厳密なチェックが可能になり、予期せぬゾーンタイプが混入するリスクを排除しています。
* **単一責任の原則 (Single Responsibility Principle)**:
    このクラスはあくまで「マップ上の静的なポイント」の表現に徹しており、現在の滞在人数などの「動的な状態」は `simulator.py` 側に持たせています。静的データと動的状態を分離することで、コードの安全性と予測可能性を高く保っています。

## アルゴリズム完全解説 (Technical choices & Algorithm Strategy)

本プロジェクトの核心は、単に「ドローンをゴールへ導く」ことではなく、**「複数のドローンが互いに衝突・渋滞することなく、数学的に証明可能な『絶対最小ターン数』で全員が同時にゴールするスケジュールを導き出す」**ことにあります。

プログラミングやグラフ理論を全く知らない人でも理解できるように、図とたとえ話を交えてその仕組みをステップバイステップで解説します。

---

### 1. 従来のやり方（単一経路探索）ではなぜ失敗するのか？

カーナビやゲームのキャラクター移動でよく使われる「ダイクストラ法」や「A*（エースター）アルゴリズム」は、**「1台のドローン」**が最短ルートを進むときには最高の力を発揮します。しかし、今回のように**「たくさんのドローン（マルチエージェント）」**を同時に動かす場合、以下の問題（衝突や渋滞）が起きて破綻します。

* **すれ違いの衝突:** ドローンAとドローンBが狭い一本道で正面衝突してしまう。
* **キャパシティ（収容人数）オーバー:** 1台しか入れない小さな部屋（ゾーン）に、3台のドローンが同時に押し寄せてしまう。
* **お見合い状態（デッドロック）:** お互いが道を譲り合って、その場で一歩も動けなくなってしまう。

これらを避けるために「ドローンが来たらその都度避ける」という行き当たりばったりのルールを作ると、今度は「最短ターン数（世界記録）」を出すことができなくなります。

そこで本システムでは、**「時空間ネットワーク流（Time-Expanded Network Flow）」**という、時間と空間をすべて味方につけた最高峰の数理最適化アルゴリズムを採用しています。

---

### 2. コア概念①：時空間ネットワーク（パラパラ漫画トリック）

普通のマップは「東に3マス、北に2マス」という**「空間（場所）」**しか持ちません。ここに**「時間（ターン）」**の概念を掛け算します。

イメージとしては**「アニメーションのパラパラ漫画」**です。
* 「0ターンの瞬間のマップ」
* 「1ターンの瞬間のマップ」
* 「2ターンの瞬間のマップ」

というように、時間の経過ごとにマップを丸ごとコピーして、縦に積み重ねていきます。

```text
 [ 時間の流れ (t) ]
    ▲
    │  [ t = 2 のマップ ]  (部屋A) ─── (部屋B)
    │       ▲                  │           │
    │       │ 時間移動エッジ    │           │
    │  [ t = 1 のマップ ]  (部屋A) ─── (部屋B)
    │       ▲                  │           │
    │       │ 待機             │           │
    │  [ t = 0 のマップ ]  (部屋A) ─── (部屋B)
    │
────┴────────────────────────────────────────► 空間（場所）
```

ドローンが「0ターン目に部屋A」にいて、「1ターン目に部屋B」に移動する場合、それは立体的なパラパラ漫画の中で「0ターン目の部屋A」から「1ターン目の部屋B」へ向かって斜めに進む矢印（エッジ）として表現されます。

このパラパラ漫画構造を作ることで、「いつ、誰が、どこにいるか」という複雑な未来の予定を、すべて1つの巨大な立体マップとしてあらかじめ描き出すことができます。


### 3. コア概念②：物理ルールを「グラフの形」で強制する
課題で指定された「最大ドローン数（max_drones）」や「制限ゾーン（restricted：移動に2ターンかかる）」などの厳しい物理ルールは、if文で判定するのではなく、「グラフの構造（ネットワークの形）」そのものを工夫することで、絶対にルールを破れないように設計しています。

1. 部屋の収容人数制限（ノード分割）
「この部屋には同時に $N$ 台までしか入れない」というルールを再現するため、すべての部屋を「入口（_in）」と「出口（_out）」の2つに分割し、その間を「太さ $N$ のストロー」で繋ぎます。ストローの太さが $N$ なので、どう頑張っても同時に $N$ 個以上の水（ドローン）は通過できません。これにより、部屋のキャパシティオーバーを自動的に防ぎます。

```text
【普通の部屋】        【プログラムが内部で作る構造】
                    ┌──────────────┐
  ┌────────┐        │   部屋A_in    │ (入口)
  │ 部屋A   │   ►    └──────┬───────┘
  └────────┘               │ ▲
                           │ │ 太さ ＝ max_drones（収容人数）
                           ▼ │
                    ┌──────────────┐
                    │  部屋A_out    │ (出口)
                    └──────────────┘
```

2. 「その場で待つ（戦略的待機）」の表現
ドローンが移動せず、次のターンまでその部屋でじっと待つという行動は、「現在のターンの出口（_t_out）」から「次のターンの入口（_t+1_in）」へ向かってまっすぐ進む矢印を張ることで表現されます。もちろん、待つときにも上記の「収容人数制限」のストローを通るため、部屋が満杯なら待つこともできません。

3. 制限ゾーン（到着に2ターンかかる部屋）への移動
制限ゾーンへの移動は、時間を1コマ飛ばして矢印を張ります。
具体的には、「現在のターンの出口（_t_out）」から「2つ先のターンの入口（_t+2_in）」へ直接矢印を伸ばします。
これにより、ドローンがその経路を選んだ瞬間、自動的に2ターンを消費して移動することになります。途中で止まる（コネクション上で待機する）ための矢印は存在しないため、「途中で勝手に待ってはいけない」というルールも自動的に守られます。

4. 進入不可ゾーン（blocked）の処理
障害物（blocked）として指定された部屋は、パラパラ漫画のマップを作る段階で最初からノード（頂点）ごと完全に消去します。道が存在しないため、アルゴリズムが誤ってそこを通るルートを計画することは100%ありません。

5. コア概念③：エドモンズ・カープ法（水道管ネットワークに水を流す）
こうして完成した「超立体的なパラパラ漫画の道」を、巨大な「水道管ネットワーク」に見立てます。

* 1. スーパーソース（仮想の給水栓）: すべてのドローンがスタートする「最初の瞬間（t=0）の start_hub」に、ドローンの数と同じ量（nb_drones）の水を一気に流し込みます。

* 2. スーパーシンク（仮想の排水口）: すべてのドローンが目指す「各ターンの end_hub」をすべて1つの大きな排水口にまとめます。

ここで登場するのが「エドモンズ・カープ（Edmonds-Karp）アルゴリズム」です。
このアルゴリズムは、幅優先探索（BFS）という堅実な探索を繰り返しながら、「給水栓から排水口まで、まだ水が流せる隙間（ルート）はないか？」を徹底的に探し、水（フロー）を流していきます。

水道管の太さ（エッジ容量）が「部屋の定員」や「道の太さ（max_link_capacity）」と完全に一致しているため、「水が綺麗に流れたルート」こそが、ドローン同士が絶対に衝突しない安全なフライトスケジュールになります。

```text
[仮想の給水栓] ───► (t=0 のスタート) ───► [立体的な水道管マップ] ───► (各ターンのゴール) ───► [仮想の排水口]
   (全ドローン分)                               (複雑な渋滞回避ルート)                                (全員無事到着)
```

6. 「絶対最小ターン数」（反復深化）
「どうやって世界最短記録（最小ターン数）を見つけているのか？」

プログラムは、まず「1ターンで全員ゴールできるか？」を試します。当然、水道管（時間軸）が短すぎて、水は全員分流れません（最大流 $<$ ドローンの総数）。全員分流れないと分かったら、パラパラ漫画をもう1ページ破いて時間軸を「2ターン」「3ターン」と1コマずつ後ろに引き延ばし、グラフを大きくして再度水を流し直します（反復深化探索）。そして、「流れた水の量」が「ドローンの総数」と完全に一致した瞬間に探索をストップします。これより短いターン数（時間軸）では、物理的な容量（部屋の広さや道の太さ）の限界のせいで、全ドローンを流し切ることが絶対に不可能だと手前のステップで証明されているため、この終了した瞬間のターン数こそが、数学的に導き出せる「地球上で最も短い絶対最適解（最小ターン数）」になります。

7. 経路の復元と出力（水流からスケジュールへの変換）
水（フロー）を流し終わったら、最後に「どの水道管をどれだけの水が通ったか」を逆算（Flow Decomposition）します。
これによって、「ドローン1番は、0ターン目に部屋A、1ターン目に部屋B、2ターン目にゴール...」という具体的な動きが割り出され、課題指定の D1-roomA D2-roomB という美しいテキスト形式でターミナルに出力されます。

制限ゾーンを飛行中のドローンに対しても、中間のターンで D1-roomA-roomB（飛行中）という状態が自動的に計算され、完璧なログが生成されます。

```text
===============================================================
▼ 図解1：時空間ネットワーク（Time-Expanded Network）の基本
===============================================================
ドローン(D1)が、スタート(Zone A)からゴール(Zone B)へ向かうシンプルな例です。
時間を「縦軸」に取ることで、未来の移動予定がすべて「1つの地図」になります。
斜めの矢印が「移動」、真下の矢印が「待機」を表します。

[時間軸]       [ Zone A ]                           [ Zone B ]

 t = 0         ( D1 )                                (    )
                 │                                     │
            待機  │     移動 ──────────────┐       待機  │
                 ▼                        ▼            ▼
 t = 1         (    )                   ( D1 )         │
                 │                        │            │
            待機  │     移動 ──────┐         │ 待機       │
                 ▼                ▼       ▼            ▼
 t = 2         (    )                   ( D1 ) 🎉ゴール到達！
                 │                        │ (以後、待機し続ける)
                 ▼                        ▼


===============================================================
▼ 図解2：制限ゾーン（2ターン移動）へのフライト
===============================================================
「到着に2ターンかかる」というルールも、矢印の引き方を変えるだけで
自動的に再現されます（途中で待機することが物理的に不可能になります）。

[時間軸]       [ Start ]                         [ Restricted Zone ]

 t = 0         ( D1 ) 
                 │    移動 ──────────┐
 t = 1         (    )                │ (空中・フライト中)
                 │                   │
 t = 2         (    )                ▼
                 │                 ( D1 ) 🎉2ターン後に到着！
                 ▼                   ▼


===============================================================
▼ 図解3：キャパシティ制限の仕組み（ノード分割）
===============================================================
「1つの部屋には max_drones 台しか入れない」という物理ルールを、
グラフの「水道管の太さ（容量）」に変換する魔法です。

【物理ルール】                       【アルゴリズム内部のグラフ構造】

                                     ( 入口 )         ( 出口 )
                                   ┌────────┐       ┌────────┐
「Zone Aの定員は2台」       ▶       │ A_in   ├───────►│ A_out  │
                                   └────────┘   ▲   └────────┘
                                                │
                                  ここの矢印の太さ(容量)を「2」に設定する！
                                  ⇒ 物理的に3台以上は絶対に通過できなくなる。
```

