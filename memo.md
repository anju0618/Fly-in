# zone.py
```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional
```
* `from enum import Enum`: 固有の値（通常、進入不可など）を持ったEnum
* `from dataclasses import dataclass`: クラスの記述をシンプルにし、データの保持に特化させる「データクラス」のデコレータをインポート

```python
class ZoneType(str, Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"
```
* ゾーンの属性を定義する列挙型クラス.Enum ではなく、str と Enum を多重継承
* `NORMAL`: コスト1ターンの通常エリア。
* `BLOCKED`: 通行不可（グラフ構築時に完全に除外される）。
* `RESTRICTED`: コスト2ターンの制限エリア。
* `PRIORITY`: コスト1ターンだが、経路探索で優遇されるエリア。

```python
@dataclass
class Zone:
    name: str
    x: int
    y: int
    zone_type: ZoneType = ZoneType.NORMAL
    max_drones: int = 1
    colour: Optional[str] = None
```
## なぜ`@dataclass`か
通常、Pythonのオブジェクト指向でデータを保持するクラスを作る場合、__init__(self, name, x, y...) や、中身を綺麗にプリントするための __repr__(self) などを手動で書く必要があります。しかし、@dataclass を付与することで、これらの定型コードがコンパイル・実行時に自動生成されます。コードの行数を減らし、可読性を高めるため

* `name: str`:ゾーンの一意な名前（識別子）を保持します。ハイフンやスペースを含まない文字列
* `x: int, y: int`:ゾーンの空間的な座標です。整数（int）型で、ビジュアライザー（`visualizer.py`）が画面上にノードを描画する際の配置計算に直接利用
* `zone_type: ZoneType = ZoneType.NORMAL`: ーンのタイプを指定します。初期値（デフォルト値）として、課題書に記載された通り「指定がない場合は normal とする」という仕様を満たすため、ZoneType.NORMAL を代入しています。
* `max_drones: int = 1`:そのゾーンに同じターンに同時に滞在できるドローンの最大数です。こちらも課題書の仕様に準拠し、デフォルト値を `1`
* `colour: Optional[str] = None`:ビジュアライザーに使うためのカラー名（"red", "blue" など）を保持します。オプション項目であるため、型は Optional[str]（str または None）とし、デフォルト値は None（色指定なし）にしています。


# connection.py
```py
@dataclass
class Connection:
    zone1: str
    zone2: str
    max_link_capacity: int = 1
```
* `zone1: str / zone2: str`: 接続されている2つのゾーンの名前。マップ上では双方向（無向エッジ）として扱われるため、このデータモデル内では「始点・終点」の区別をつけずフラットに保持。
* `max_link_capacity: int`: 同一ターンにこの通路を同時に通過できるドローンの最大制限数。課題書の仕様に基づきデフォルト値は `1` に設定。

## グラフ理論用語

* 拠点を`node（ノード）`拠点同士をつなぐ通路を`edge（エッジ）`と呼ぶ
* 無向エッジはどちらの方向にも進めるが、有向エッジは一方通行

# drone.py

```py
class Drone:
    def __init__(self, id_num: int, start_zone_name: str) -> None:
        self.id_num: int = id_num
        self.current_zone: str = start_zone_name
        self.target_zone: Optional[str] = None
        self.turns_to_arrive: int = 0
```
## なぜ @dataclass ではないのか？:
`Zone` や `Connection` はデータを入れるだけのコンテナでしたが、`Drone` は「状態の更新ロジックや振る舞い（プロパティ）」を持つオブジェクト指向的な「エンティティ（実体）」として設計されているため、通常のクラス構造を採用しています。

* `current_zone: str`: 現在滞在しているゾーン名。移動中の場合は一時的に A-B のようなコネクション名が代入される
* `target_zone: Optional[str]`: 移動中の場合の「最終目的地」となるゾーン名。停止中は `None`
* `zturns_to_arrive: int`: 目的地に到着するまでの残りターン数。

```py
@property
def name(self) -> str:
    return f"D{self.id_num}"

@property
def is_in_flight(self) -> bool:
    return self.target_zone is not None and self.turns_to_arrive > 0
```
* `@property name:` 課題書で厳密に指定されている出力形式（D1, D2 など）の文字列を動的に生成して返す.
* `@property is_in_flight`: ドローンが現在「空中（コネクション上）を飛行中か」を判定するブール値。

## 設計のポイント
* **2ターン移動（restricted）の解決策**:
    通常ゾーンの1ターン移動なら現在地を書き換えるだけで済みますが、2ターンかかる制限ゾーンへの移動では「1ターン目は空中（通路）に浮いていて、2ターン目に着陸する」という状態が発生します.
* このクラスに turns_to_arrive（カウントダウンカウンター）を持たせることで、シミュレーター（simulator.py）やビジュアライザー（visualizer.py）が「今ちょうど中間地点を飛行中である」という複雑な時空間の状態を追跡できるようになっています。


# map_data.py
```py
from dataclasses import dataclass, field
from connection import Connection
from zone import Zone
```
* `from dataclasses import field`: データクラス内で辞書（dict）やリスト（list）などの可変（変更可能）なオブジェクトを安全に初期化するために使用。Pythonの仕様上、データクラスで可変オブジェクトを普通に初期化すると全インスタンスで共有されてしまうバグが起きるため、field(default_factory=...) を使うのが義務。

```py
@dataclass
class MapData:
    nb_drones: int
    start_hub: Zone
    end_hub: Zone
    zones: dict[str, Zone] = field(default_factory=dict)
    connections: list[Connection] = field(default_factory=list)
    graph: dict[str, list[tuple[str, Connection]]] = field(
        default_factory=dict, init=False
    )
```
* `nb_drones`: マップに存在する総ドローン数.
* `start_hub / end_hub`: 出発地点と最終目的地の特殊ゾーン。
* `zones`: ゾーン名をキー、Zone オブジェクトを値とした辞書。これにより、特定のゾーン情報を一瞬（計算量 $O(1)$）で検索可能にする
* `connections`:パースされた通路（Connection）のフラットなリスト。
* `graph`: ゾーン名をキーとし、「（隣接するゾーン名, その通路データ）」のタプルのリストを持つ隣接リスト形式のグラフ。init=False を指定することで、外部から直接入力させるのではなく、内部で自動計算させる。

```py
def __post_init__(self) -> None:
        self.graph = {name: [] for name in self.zones}
        for conn in self.connections:
            if conn.zone1 in self.graph and conn.zone2 in self.graph:
                self.graph[conn.zone1].append((conn.zone2, conn))
                self.graph[conn.zone2].append((conn.zone1, conn))
```
* `__post_init__` とは:
データクラスのメンバー（`nb_drones` など）が初期化された直後に自動的に実行される特殊メソッド
* `内部ロジック`: フラットな通路データ（`connections`）をループで回し、zone1 から zone2、そして zone2 から zone1 の両方向へエッジを登録することで、前回の「無向エッジ」をプログラムが探索しやすい隣接リスト形式へ自動展開している。


# map_parser.py
```py
class MapParser:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.nb_drones: int = 0
        self.start_hub: Optional[Zone] = None
        self.end_hub: Optional[Zone] = None
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []
        self.seen_connections: set[tuple[str, str]] = set()
```
* `seen_connections`: 重複する接続定義（a-b と b-a など）を一瞬で検知するため、文字列のタプルを保存する setを用意。

```py
def parse(self) -> MapData:
        with open(self.file_path, "r") as file:
            for line_num, line in enumerate(file, 1):
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue

                main_content, metadata = self._extract_metadata(stripped)
```
* `メインループと前処理`: ファイルを安全なコンテキストマネージャ（with）で開き、enumerate(file, 1) で現在の行番号を追跡しながら1行ずつ走査。  空行や # から始まるコメント行は、仕様通り continue でスキップ
* `_extract_metadata` ヘルパーを呼び出し、通常のテキスト内容と [...] で囲まれたメタデータ部分を綺麗に分離。

```py
if ":" not in main_content:
                    raise ValueError(f"Line {line_num}: Invalid format, missing ':'.")
                prefix, data = main_content.split(":", 1)
                prefix = prefix.strip()
                data = data.strip()
```
* ***プレフィックスの分離***: コロン（:）の有無をチェックし、存在しなければ即座に ValueError。コロンの左側を prefix（命令）、右側を data（中身）として抽出。

```py
if self.nb_drones == 0:
                    if prefix != "nb_drones":
                        raise ValueError(f"Line {line_num}: The first defined property must be 'nb_drones'.")
                    self._parse_nb_drones(data, line_num)
                    continue

                if prefix in ("hub", "start_hub", "end_hub"):
                    self._parse_zone(prefix, data, metadata, line_num)
                elif prefix == "connection":
                    self._parse_connection(data, metadata, line_num)
                else:
                    raise ValueError(f"Line {line_num}: Unknown property prefix '{prefix}'.")
```
* **厳格な順序制約の担保**: 課題の「最初の行は必ず nb_drones でなければならない」という制約を満たすため、self.nb_drones が未設定のうちは、それ以外の命令（hub など）が来たら即座に弾くロジックを実装。
* その後、各プレフィックスに応じて専用の内部メソッド（`_parse_zone`など）へ処理を安全にルーティング。未知の命令が来た場合も行番号付きのエラーを出力。

```py
if not self.start_hub or not self.end_hub:
            raise ValueError("Map is missing a unique start_hub or end_hub.")

        return MapData(...)
```
最終整合性チェック: ファイルの全行を読み終わった後、start_hub と end_hub が必ず1つずつ存在しているかを最終検証。不足していればエラーを投げ、クリアしていれば集めたデータを `MapData` コンテナへ流し込んで返却。

## 内部検証ヘルパーメソッドのロジック
* **① _parse_nb_drones**（ドローン数の検証）文字列を int に変換し、それが正の整数（> 0）であることを厳格に確認
* **② _parse_zone**（拠点の検証とメタデータ反映）座標（x, y）が正しい整数であるか、名前がすでに重複して登録されていないかをチェック。  名前の中にハイフン（-）が含まれている場合、のちの接続定義（a-b）のパースを壊すため、仕様通りにここで厳しく拒否
メタデータ（zone=restricted や max_drones=2）を辞書から取り出し、未指定の場合はデフォルト値（normal, 1）を安全に適用。  start_hub / end_hub が複数回定義された場合は「重複エラー」を発生させる。
* **③ _parse_connection（通路の検証と重複排除）**: ハイフン（-）で正しく2つのゾーンに分割できるかをチェック。  指定されたゾーン名が、事前に hub として定義済みの実在するゾーンであるかを検証。
ピアレビューの意地悪なトラップ（a-b の定義の後に、逆向きの b-a が登場するケース）を対策するため、2つの名前をアルファベット順にソートしてタプル化（例: ("a", "b")）し、seen_connections 集合を使って完全な重複排除を達成
* **④ _extract_metadata（角括弧の切り出し）** :[ と ] の位置をインデックスで探し、中身のキー・バリュー（max_drones=2 など）をスペース区切りでパースして辞書化する堅牢な文字列表現処理。

# pathfinder.py
```py
from collections import deque
from map_data import MapData
from typing import Any

class InvalidMoveError(Exception):
    pass

class CapacityExceededError(Exception):
    pass
```
* f`rom collections import deque:` 幅優先探索（BFS）で使う、要素の追加・取り出しが高速な両端キュー（deque）をインポートしています。 
* `InvalidMoveError / CapacityExceededError:` パスファインダー内部、またはマルチエージェント移動時の例外処理のためのカスタム例外クラスです

```py
class Pathfinder:
    def __init__(self, map_data: MapData) -> None:
        self.map_data = map_data
        self.residual_graph: dict[str, dict[str, int]] = {}
        self.schedule: dict[int, dict[int, str]] = {}
```
* `self.residual_graph`: エドモンズ・カープ法で用いる「残余グラフ（流量を計算するための仮想グラフ）」を二重の辞書形式で保持します。
* `self.schedule`: 最終的に確定した「どのターン（int）に、どのドローン（int）が、どこ（str）に動くか」を格納するスケジュール帳です。

```py
def _add_edge(self, u: str, v: str, capacity: int) -> None:
        if u not in self.residual_graph:
            self.residual_graph[u] = {}
        if v not in self.residual_graph:
            self.residual_graph[v] = {}
        self.residual_graph[u][v] = capacity
        if u not in self.residual_graph[v]:
            self.residual_graph[v][u] = 0
```
* `ネットワーク流用の有向エッジ追加ヘルパー`: ノード u から v へ、容量 capacity の順方向エッジを張ります。
* `残余エッジの初期化`: 同時に逆方向のエッジ v から u へ、容量 0 の逆方向エッジを自動的にセットします。

```py
def build_network(self, max_time: int) -> None:
        self.residual_graph.clear()
        inf_capacity = self.map_data.nb_drones
```
* `時空間ネットワークの構築開始`: 探索ターン数（`max_time`）が決まるたびに、残余グラフを一度クリアしてゼロから再構築します。
* `inf_capacity`: スタートとゴールは容量無制限であるため、実質的な無限大として総ドローン数（`nb_drones`）を設定しています。

```py
for t in range(max_time + 1):
            for zone_name, zone in self.map_data.zones.items():
                in_node = f"{zone_name}_t{t}_in"
                out_node = f"{zone_name}_t{t}_out"

                is_special = zone_name in (
                    self.map_data.start_hub.name,
                    self.map_data.end_hub.name,
                )
                capacity = inf_capacity if is_special else zone.max_drones
                self._add_edge(in_node, out_node, capacity)

                if t < max_time:
                    next_in = f"{zone_name}_t{t+1}_in"
                    self._add_edge(out_node, next_in, capacity)
```
* `頂点（ゾーン）容量のモデル化（ノード分割）`: フローネットワークで「地点の容量（max_drones）」を表現するため、ある時刻 $t$ における各ゾーンを in_node と out_node の2つに分割し、その間に max_drones 容量のエッジを張ることで、同時滞在制限を完璧に再現しています。
* **`戦略的待機（Wait）のモデル化`**: 時刻 $t$ の出口（out_node）から、次の時刻 $t+1$ の同じゾーンの入口（next_in）へ容量 capacity の有向エッジを張ることで、ドローンが「その場で1ターン待機する」という行動を選択肢として組み込んでいます。  

```py
for u_name, edges in self.map_data.graph.items():
                for v_name, connection in edges:
                    v_zone = self.map_data.zones[v_name]
                    if v_zone.zone_type == "blocked":
                        continue

                    cost = 2 if v_zone.zone_type == "restricted" else 1

                    if t + cost <= max_time:
                        out_node = f"{u_name}_t{t}_out"
                        in_node = f"{v_name}_t{t+cost}_in"
                        self._add_edge(
                            out_node, in_node, connection.max_link_capacity
                        )
```
* **障害物の除外**: 移動先が blocked ゾーンの場合は、グラフにエッジを追加せず完全に無視（侵入不可に）します。
* **移動コストの時空間マッピング**: 通常・優先ゾーンへの移動コストは 1（時刻 $t \to t+1$）ですが、制限ゾーン（restricted）への移動はコスト 2 となるため、中間の時間をスキップして時刻 $t$ から $t+2$ へエッジを飛ばして接続します
* **通路容量（max_link_capacity）の制限**: 異なるゾーン間のエッジ容量には、コネクションごとの同時通行制限（max_link_capacity）を適用します。

```py
def _bfs(self, src: str, sink: str, parent: dict[str, str]) -> bool:
        visited = {src}
        queue = deque([src])

        while queue:
            u = queue.popleft()
            for v, cap in self.residual_graph[u].items():
                if v not in visited and cap > 0:
                    parent[v] = u
                    if v == sink:
                        return True
                    visited.add(v)
                    queue.append(v)
        return False
```
* **増加パスの探索（BFS）**: 残余容量（cap）が 0 より大きいエッジだけを辿り、現在のネットワークでスタート（src）からゴール（sink）へ流せるルートがあるかを最短経路（ホップ数基準）で探索します。発見した場合は経路復元用に parent 辞書に記録して True を返します。

```PY
def edmonds_karp(self, src: str, sink: str) -> int:
        max_flow = 0
        parent: dict[str, str] = {}

        while self._bfs(src, sink, parent):
            path_flow = float("inf")
            v = sink
            while v != src:
                u = parent[v]
                path_flow = min(path_flow, self.residual_graph[u][v])
                v = parent[v]

            v = sink
            while v != src:
                u = parent[v]
                self.residual_graph[u][v] -= int(path_flow)
                self.residual_graph[v][u] += int(path_flow)
                v = parent[v]

            max_flow += int(path_flow)
            parent.clear()

        return max_flow
```
* **エドモンズ・カープ法の本体**: BFS で増加パスが見つからなくなるまで、ボトルネックとなる容量（path_flow）を算出しながら、繰り返し水を流し込みます。
* **残余グラフの更新**: 水を流した分だけ順方向のエッジ容量を減らし、逆に押し戻すことができるように逆方向のエッジ容量を増やします。最終的に流し込めた合計量（max_flow）を返します。

```py
def solve(self) -> dict[int, dict[int, str]]:
        nb_drones = self.map_data.nb_drones
        start_name = self.map_data.start_hub.name
        end_name = self.map_data.end_hub.name

        total_turns = 1
        max_limit = 200
        while total_turns <= max_limit:
            self.build_network(total_turns)

            self._add_edge("SUPER_SRC", f"{start_name}_t0_in", nb_drones)
            for t in range(total_turns + 1):
                end_out = f"{end_name}_t{t}_out"
                self._add_edge(end_out, "SUPER_SINK", nb_drones)

            flow = self.edmonds_karp("SUPER_SRC", "SUPER_SINK")
            if flow == nb_drones:
                break
            total_turns += 1
```

* **反復深化（Iterative Deepening）による最少ターンの決定**: シミュレーション全体の想定ターン数（total_turns）を 1 から順に増やしていき、毎ターン時空間グラフを拡張・構築し直します

* **スーパーソース・スーパーシンクの配置**: すべてのドローンが流入する仮想の始点 SUPER_SRC と、全タイムステップのゴール出口から流入する仮想の終点 SUPER_SINK を設置します。  絶対最小ターンの数学的証明: 最大流（flow）がドローン総数（nb_drones）と完全に一致した瞬間、ループを終了します。これより少ないターン数では、物理的な容量制限により絶対に全機を流し切ることができないため、この瞬間に数学的なグローバル最適解（最小ターン数）が確定します。

```py
flow_graph: dict[str, dict[str, int]] = {}
        for u in self.residual_graph:
            flow_graph[u] = {}
            for v in self.residual_graph[u]:
                if self.residual_graph[v].get(u, 0) > 0:
                    flow_graph[u][v] = self.residual_graph[v][u]
```
* **順フローの抽出（Flow Decomposition の準備）**: 計算完了後の残余グラフを解析し、逆方向エッジの溜まり具合（＝実際に水が流れた量）から、どのエッジをどれだけのドローンが通過したかを示すピュアな「フローグラフ」を取り出します

```py
for drone_id in range(1, nb_drones + 1):
            t = 0
            curr_zone = start_name
            while curr_zone != end_name:
                out_node = f"{curr_zone}_t{t}_out"
                next_node = ""
                if out_node in flow_graph:
                    for nxt, f in flow_graph[out_node].items():
                        if f > 0:
                            next_node = nxt
                            break
                if not next_node:
                    break

                flow_graph[out_node][next_node] -= 1
                clean = next_node.replace("_in", "").replace("_out", "")
                next_zone, t_str = clean.rsplit("_t", 1)
                next_t = int(t_str)

                sim_turn = t + 1
                if sim_turn not in self.schedule:
                    self.schedule[sim_turn] = {}

                if next_zone != curr_zone:
                    cost = next_t - t
                    if cost == 1:
                        self.schedule[sim_turn][drone_id] = next_zone
                    elif cost == 2:
                        self.schedule[sim_turn][drone_id] = (
                            f"{curr_zone}-{next_zone}"
                        )
                        next_turn = sim_turn + 1
                        if next_turn not in self.schedule:
                            self.schedule[next_turn] = {}
                        self.schedule[next_turn][drone_id] = next_zone

                t = next_t
                curr_zone = next_zone

        return self.schedule
```
* **フロー分解（Flow Decomposition）**による個別経路復元: 流れた総フローの塊を、1機ずつの具体的な移動タイムライン（drone_id ごとのスケジュール）へ分解してマッピングします
* **2ターン移動（インフライト）状態の補完**: 制限ゾーンへの移動（cost == 2）を検知した場合、仕様に従って1ターン目の出力用に `D<ID>-<connection>`（例：D1-zoneA-zoneB）という空中滞在ステータスをスケジュールへ自律的に補完・挿入しています。

```py
def compute_moves(self, simulator: Any) -> dict[int, str]:
        if not self.schedule:
            self.solve()
        return self.schedule.get(simulator.current_turn, {})
```
* **シミュレーターへの移動指示**: シミュレーター（simulator.py）から現在のターン数を尋ねられた際、事前計算してあるスケジュール帳（self.schedule）から、そのターンに行うべき全ドローンの移動命令の辞書を即座に引き出して渡します


# simulator.py
```py
from drone import Drone
from map_data import MapData
from typing import Any

class InvalidMoveError(Exception):
    pass

class CapacityExceededError(Exception):
    pass
```
いつもの

```py
class Simulator:
    def __init__(self, map_data: MapData) -> None:
        self.map_data = map_data
        self.drones: list[Drone] = []
        self.zone_occupancy = {
                name: 0 for name in self.map_data.zones
        }
        self.current_turn: int = 1

        start_name = self.map_data.start_hub.name
        self.zone_occupancy[start_name] = self.map_data.nb_drones
        for i in range(1, self.map_data.nb_drones + 1):
            drone = Drone(i, self.map_data.start_hub.name)
            self.drones.append(drone)
```
初期状態のセットアップ:`zone_occupancy`: 各ゾーンに「今何機のドローンがいるか」をリアルタイムに記録するカウンターの辞書。
* **初期配置**: シミュレーション開始時、すべてのドローン（1〜nb_drones）を一斉に生成し、例外ルールである「容量無制限の start_hub」に全機を配置。

```py
def run_turn(self, moves: dict[int, str]) -> None:
        self.current_turn += 1

        for drone_id, target_zone in moves.items():
            current_zone = self.drones[drone_id - 1].current_zone
            if "-" not in current_zone:
                self.zone_occupancy[current_zone] -= 1
```

* **ターンの進行と容量の先行解放（ファーストパス）**:課題の重要なルールである「ゾーンから出ていくドローンは、そのターンのうちに即座に容量を解放する」を忠実に再現。
* 移動する全ドローンを先になめ、現在地が空中（- を含むコネクション上）でなければ、元のゾーンのカウントをマイナスしてスペースを空ける。

```py
for drone_id, target_zone in moves.items():
            current_zone = self.drones[drone_id - 1].current_zone

            if "-" in current_zone:
                self.zone_occupancy[target_zone] += 1
                self.drones[drone_id - 1].current_zone = target_zone
                continue

            if "-" in target_zone:
                self.drones[drone_id - 1].current_zone = target_zone
                continue
```
* **特殊移動（空中・制限ゾーン）の検証（セカンドパス：前半）**:
* **着陸処理**: 現在地が空中（- あり）だったドローンが通常の目的地へ着陸する場合、目的地のゾーンカウントを増やして現在地を上書き。
* **離陸処理**: 目的地が空中（制限ゾーンへ向かう2ターン移動の1ターン目）の場合、ドローンの現在地をコネクション名に書き換える（まだ目的地のゾーンには入っていないため、ゾーンカウントは増やさない）。

```py
valid_destinations = [
                name for name, _ in self.map_data.graph[current_zone]
            ]

            if target_zone in valid_destinations:
                is_special = target_zone in (
                    self.map_data.start_hub.name,
                    self.map_data.end_hub.name,
                )
                max_drones = self.map_data.zones[target_zone].max_drones
                has_space = self.zone_occupancy[target_zone] < max_drones

                if not is_special and not has_space:
                    raise CapacityExceededError(f"{target_zone} is full.")
                else:
                    self.zone_occupancy[target_zone] += 1
                    self.drones[drone_id - 1].current_zone = target_zone
```
* **通常移動の厳格な検証（セカンドパス：後半）**:地理的に移動可能な隣接ゾーンであるかを隣接リストから検証。
移動先が start_hub または end_hub（これらは容量無制限の例外エリア）でない場合、現在の滞在数が max_drones を超えないかを厳しくチェック
もし容量オーバーが発生していれば、即座に CapacityExceededError を発生させてシミュレーションを中断（安全の確保）

```py
def is_finished(self) -> bool:
        end_name = self.map_data.end_hub.name
        return all(d.current_zone == end_name for d in self.drones)
```
* 終了判定: すべてのドローン（all()）の現在地が end_hub になった瞬間、シミュレーション完了（True）と判定。

```py
def run(self, pathfinder: Any, show_capacity: bool = False) -> None:
        while not self.is_finished():
            moves = pathfinder.compute_moves(self)
            if moves:
                turn_output = " ".join(f"D{d}-{z}" for d, z in moves.items())
                print(turn_output)
            self.run_turn(moves)
            if show_capacity:
                # --- Turn Capacity Info の出力ロジック ---
```

## シミュレーションの実行ループと標準出力:
* pathfinder からそのターンの全移動コマンド（moves）を取得し、課題指定の D1-zoneA D2-zoneB というスペース区切りのフォーマットで標準出力へ一括出力（動かなかったドローンは自動で除外される）
* 移動を実行（run_turn）した後、--capacity-info フラグ（show_capacity）が有効であれば、各ゾーンと各コネクションの現在の利用率をリアルタイムで詳細に出力する

# main.py
```py
def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <map_file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
```
引数チェック
```py
try:
        parser = MapParser(file_path)
        map_data = parser.parse()

        simulator = Simulator(map_data)
        pathfinder = Pathfinder(map_data)

        simulator.run(pathfinder, show_capacity="--capacity-info" in sys.argv)
```

# visualizer.py

```py
import math
import tkinter as tk
from typing import Any, Dict, List, Tuple
```
* **import math**:同一ゾーンにドローンが複数滞在した際、描画が重ならないように配置を分散させる三角関数の計算で使用します。
* **import tkinter as tk**: Python標準のGUIツールキットであるTkinterフレームワークをインポートしています。

```py
def _calculate_bounds(self) -> None:
        xs = [z.x for z in self.map_data.zones.values()]
        ys = [z.y for z in self.map_data.zones.values()]

        min_x = min(xs) if xs else 0
        max_x = max(xs) if xs else 10
        min_y = min(ys) if ys else 0
        max_y = max(ys) if ys else 10

        self.range_x = float(max_x - min_x if max_x != min_x else 1)
        self.range_y = float(max_y - min_y if max_y != min_y else 1)
        self.min_x = float(min_x)
        self.min_y = float(min_y)
```
マップの境界値とスケールの動的計算: すべてのゾーンのX座標・Y座標の最大値と最小値を算出します。ウィンドウの解像度（1000x750）に合わせて、マップ全体のトポロジーを画面中央に綺麗に収めるためのスケーリング係数を事前計算します。

```py
def _get_coords(self, zone_name: str) -> Tuple[float, float]:
        if "-" in zone_name:
            u_name, v_name = zone_name.split("-", 1)
            u_x, u_y = self._get_coords(u_name)
            v_x, v_y = self._get_coords(v_name)
            return (u_x + v_x) / 2, (u_y + v_y) / 2
        ...
        if self.range_y == 1.0:
            pixel_y = h / 2
        else:
            pixel_y = self.padding + (zone.y - self.min_y) * scale_y
```
## 実座標からピクセル空間への変換ロジック:
* 制限ゾーンへの移動中を表すコネクション名（A-B）が渡された場合、自動的にゾーンAとゾーンBの中間地点（航空機の中間座標）を計算して返却します。
* 一直線マップ（エッジケース）の対策: すべてのゾーンのY座標がゼロ（range_y == 1.0）となる直線状のマップが入力された場合でも、ノードが画面最上部に張り付いて見えなくなるのを防ぐため、画面の垂直方向中央（h / 2）へ強制的に一列整列させるレイアウト補正を実装しています。

```py
def refresh_view(self) -> None:
        # 1. 接続ラインの描画（省略）
        # 2. ゾーン円の描画とメタデータカラーの反映
            meta_color = (zone.colour or "").lower()
            if meta_color == "green": color_hex = "#a6e3a1"
            elif meta_color == "red": color_hex = "#f38ba8"
            ...
```
## 画面のリアルタイム再レンダリング
* キャンバス上の古い描画を一度全て削除（.delete("all")）した上で、最新の状態を再描画します
* マップテキスト内で指定されたオプショナルなカラー属性（color=red など）の文字列を検知し、対応するカラーコードに変換してノードの円（oval）へ動的に適用します
* start_hub は緑色、end_hub は黄色として最優先で固定色分けし、視認性を高めています。

```py
for z_name, drones in zone_clusters.items():
            zx, zy = self._get_coords(z_name)
            num_drones = len(drones)

            for idx, d_id in enumerate(drones):
                offset_r = 32 if num_drones > 1 else 0
                angle = idx * (2 * math.pi / num_drones) if num_drones > 0 else 0.0
                dx = zx + offset_r * math.cos(angle)
                dy = zy + offset_r * math.sin(angle)
```
## ドローンの重なり防止（クラスター分散描画）:
* 1つのゾーンに複数のドローンが同時滞在している（num_drones > 1）場合、ドローンの円が完全に真上に重なって見えなくなる現象を防止します。
* 滞在しているドローンの数に応じて円周上の角度（angle）を均等に分割し、三角関数（cos / sin）を使って、中心ノードの周囲の軌道上に綺麗に分散（クラスター配置）させて描画する高度なUI工夫です

```py
def prev_turn(self) -> None:
        if self.current_turn <= 0:
            return
        self.current_turn -= 1
        for i in range(1, self.map_data.nb_drones + 1):
            self.drone_positions[i] = self.map_data.start_hub.name

        for t in range(1, self.current_turn + 1):
            turn_moves = self.schedule.get(t, {})
            for d_id, target_zone in turn_moves.items():
                self.drone_positions[d_id] = target_zone
```
## 安全な「ターン巻き戻し」メカニズム（リプレイ方式）:
* 42のレビュー中に「1ターン前の渋滞状況をもう一度見せて」と言われた際に対応する機能です。
* 各移動の逆演算ロジックを無理に書くと、制限ゾーンなどの複雑な状態の巻き戻しでバグが発生しやすくなります。
* このシステムでは、ボタンが押されると全てのドローンを一度スタート地点にリセットし、第1ターンから目的のターン（current_turn）までの移動スケジュールを一瞬で高速に再適用（リプレイ）する手法を採用しています。これにより、バグを100%発生させずに、安全かつ確実に過去の任意の盤面を復元できます。  


