# -*- coding: utf-8 -*-
"""全クラスタ同時停止シグナルの読み書き判定。

/stop はギルドコマンドなので、そのギルドのシャードを持つ 1 クラスタにしか届かない。
全クラスタを揃って落とすため、受け取ったクラスタが共有ディレクトリにシグナルファイルを
書き、他クラスタが watchfiles で検知して各自 stop() する。

Discord に依存しない純ロジックなので tests/test_cluster_signal.py から直接テストできる。
"""
import os
import time

SIGNAL_FILENAME = "stop_signal.json"


def signal_path(base_dir):
    """シグナルファイルの絶対パス。全クラスタが同一ディレクトリを共有している前提。"""
    return os.path.join(base_dir, SIGNAL_FILENAME)


def build_signal(message, cluster_id):
    """シグナルファイルに書き込む内容を組み立てる。"""
    return {"message": message, "issued_by": cluster_id, "issued_at": time.time()}


def should_stop(payload, cluster_id, started_at):
    """読み込んだシグナルに従って停止すべきかを判定する。

    payload: シグナルファイルの中身(壊れていれば None などが来る)
    cluster_id: 自クラスタの CLUSTER_ID
    started_at: 自プロセスの起動時刻(time.time())
    """
    if not isinstance(payload, dict):
        return False

    # 発行元は watcher ではなく直接 stop() するので、ここでは反応しない
    if payload.get("issued_by") == cluster_id:
        return False

    issued_at = payload.get("issued_at")
    if not isinstance(issued_at, (int, float)):
        # 起動時に作る空ファイル({})や壊れた内容
        return False

    # 起動より前のシグナルは処理済み。再起動直後に読み返して停止ループに陥るのを防ぐ
    return issued_at > started_at
