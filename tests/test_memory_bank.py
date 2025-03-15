#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
メモリーバンク統合テスト
"""

import os
import sys
import unittest
import tempfile
import shutil
import json
from datetime import datetime

# テスト対象モジュールのパスを追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# テスト対象モジュールのインポート
from memory_bank.init import MemoryBankInitializer
from memory_bank.storage import MemoryStorage
from memory_bank.retrieval import MemoryRetrieval


class TestMemoryBank(unittest.TestCase):
    """メモリーバンクの統合テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        # テスト用の一時ディレクトリを作成
        self.test_dir = tempfile.mkdtemp()
        
        # テスト対象のインスタンスを作成
        self.initializer = MemoryBankInitializer(storage_path=self.test_dir)
        self.storage = MemoryStorage(storage_path=self.test_dir)
        self.retrieval = MemoryRetrieval(storage_path=self.test_dir)
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        # テスト用の一時ディレクトリを削除
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """初期化のテスト"""
        # 初期化の実行
        result = self.initializer.initialize()
        
        # 初期化が成功したことを確認
        self.assertTrue(result)
        self.assertTrue(self.initializer.initialized)
        
        # 初期化ログファイルが作成されたことを確認
        log_file = os.path.join(self.test_dir, "init_log.txt")
        self.assertTrue(os.path.exists(log_file))
        
        # 初期化状態の確認
        status = self.initializer.status()
        self.assertTrue(status["initialized"])
        self.assertEqual(status["storage_path"], self.test_dir)
        self.assertTrue(status["storage_exists"])
    
    def test_storage_and_retrieval(self):
        """保存と検索のテスト"""
        # 初期化
        self.initializer.initialize()
        
        # テストデータの作成
        test_data = {
            "name": "テストデータ",
            "value": 123,
            "tags": ["test", "memory", "bank"]
        }
        
        # データの保存
        save_result = self.storage.save("test_key", test_data, {"type": "test"})
        self.assertTrue(save_result)
        
        # データの読み込み
        loaded_data = self.storage.load("test_key")
        self.assertIsNotNone(loaded_data)
        self.assertEqual(loaded_data["name"], "テストデータ")
        self.assertEqual(loaded_data["value"], 123)
        
        # キー検索
        keys = self.retrieval.search_by_key("test")
        self.assertIn("test_key", keys)
        
        # コンテンツ検索
        results = self.retrieval.search_by_content("テストデータ")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["key"], "test_key")
        
        # 最近のデータ取得
        recent = self.retrieval.get_recent(5)
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0]["key"], "test_key")
    
    def test_multiple_data(self):
        """複数データのテスト"""
        # 初期化
        self.initializer.initialize()
        
        # 複数のテストデータを保存
        for i in range(5):
            data = {
                "id": i,
                "name": f"テストデータ{i}",
                "value": i * 10
            }
            self.storage.save(f"key_{i}", data, {"index": i})
        
        # 保存されたキーの一覧を取得
        keys = self.storage.list_keys()
        self.assertEqual(len(keys), 5)
        
        # キー検索
        keys_3 = self.retrieval.search_by_key("key_3")
        self.assertEqual(len(keys_3), 1)
        self.assertEqual(keys_3[0], "key_3")
        
        # コンテンツ検索
        results_20 = self.retrieval.search_by_content("20")
        self.assertEqual(len(results_20), 1)
        self.assertEqual(results_20[0]["data"]["value"], 20)
        
        # 最近のデータ取得（制限あり）
        recent_3 = self.retrieval.get_recent(3)
        self.assertEqual(len(recent_3), 3)


if __name__ == "__main__":
    unittest.main()
