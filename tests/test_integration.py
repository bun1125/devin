#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
全体統合テスト
"""

import os
import sys
import unittest
import tempfile
import shutil
import json
import logging
from datetime import datetime

# テスト対象モジュールのパスを追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# テスト対象モジュールのインポート
from memory_bank.init import MemoryBankInitializer
from memory_bank.storage import MemoryStorage
from memory_bank.retrieval import MemoryRetrieval
from ldd_workflow.workflow import LDDWorkflow


class TestIntegration(unittest.TestCase):
    """全体統合テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        # ロギングの設定
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # テスト用の一時ディレクトリを作成
        self.test_dir = tempfile.mkdtemp()
        
        # サブディレクトリの作成
        self.memory_dir = os.path.join(self.test_dir, "memory")
        self.workflow_dir = os.path.join(self.test_dir, "workflow")
        self.logs_dir = os.path.join(self.test_dir, "logs")
        os.makedirs(self.memory_dir, exist_ok=True)
        os.makedirs(self.workflow_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # テスト用の設定ファイルを作成
        self.config_path = os.path.join(self.test_dir, "test_config.json")
        self._create_test_config()
        
        # テスト対象のインスタンスを作成
        self.initializer = MemoryBankInitializer(storage_path=self.memory_dir)
        self.storage = MemoryStorage(storage_path=self.memory_dir)
        self.retrieval = MemoryRetrieval(storage_path=self.memory_dir)
        self.workflow = LDDWorkflow(config_path=self.config_path)
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        # テスト用の一時ディレクトリを削除
        shutil.rmtree(self.test_dir)
    
    def _create_test_config(self):
        """テスト用の設定ファイルを作成"""
        config = {
            "phases": {
                "learn": {
                    "enabled": True,
                    "timeout": 10
                },
                "develop": {
                    "enabled": True,
                    "timeout": 20
                },
                "deploy": {
                    "enabled": True,
                    "timeout": 10
                }
            },
            "metrics": {
                "collect": True,
                "storage_path": self.logs_dir
            },
            "feedback": {
                "enabled": True,
                "auto_adjust": True
            }
        }
        
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def test_end_to_end_workflow(self):
        """エンドツーエンドのワークフローテスト"""
        # 1. メモリーバンクの初期化
        init_result = self.initializer.initialize()
        self.assertTrue(init_result)
        
        # 2. テストデータの保存
        test_data = {
            "name": "統合テストデータ",
            "value": 42,
            "tags": ["integration", "test"]
        }
        save_result = self.storage.save("integration_key", test_data, {"type": "integration_test"})
        self.assertTrue(save_result)
        
        # 3. ワークフローの実行
        workflow_results = self.workflow.run()
        
        # 4. 結果の検証
        # 4.1 メモリーバンクのデータが正しく保存されているか
        loaded_data = self.storage.load("integration_key")
        self.assertIsNotNone(loaded_data)
        self.assertEqual(loaded_data["name"], "統合テストデータ")
        
        # 4.2 ワークフローが正しく実行されたか
        self.assertIn("learn", workflow_results)
        self.assertIn("develop", workflow_results)
        self.assertIn("deploy", workflow_results)
        
        # 4.3 検索機能が正しく動作するか
        search_results = self.retrieval.search_by_content("統合テスト")
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0]["key"], "integration_key")
    
    def test_feedback_loop(self):
        """フィードバックループのテスト"""
        # 1. メモリーバンクの初期化
        self.initializer.initialize()
        
        # 2. 初期データの保存
        initial_data = {
            "name": "フィードバックテスト",
            "iteration": 0,
            "status": "initial"
        }
        self.storage.save("feedback_key", initial_data)
        
        # 3. ワークフローの実行（学習フェーズのみ）
        learn_results = self.workflow.run(start_phase="learn")
        
        # 4. フィードバックデータの更新
        loaded_data = self.storage.load("feedback_key")
        updated_data = loaded_data.copy()
        updated_data["iteration"] = 1
        updated_data["status"] = "updated"
        updated_data["feedback"] = "学習フェーズからのフィードバック"
        self.storage.save("feedback_key", updated_data)
        
        # 5. 再度ワークフローを実行（開発フェーズから）
        develop_results = self.workflow.run(start_phase="develop")
        
        # 6. 最終的なデータを検証
        final_data = self.storage.load("feedback_key")
        self.assertEqual(final_data["iteration"], 1)
        self.assertEqual(final_data["status"], "updated")
        self.assertIn("feedback", final_data)
    
    def test_metrics_collection(self):
        """メトリクス収集のテスト"""
        # 1. メモリーバンクの初期化
        self.initializer.initialize()
        
        # 2. ワークフローの実行
        self.workflow.run()
        
        # 3. メトリクスディレクトリにファイルが作成されたことを確認
        metrics_files = os.listdir(self.logs_dir)
        self.assertGreater(len(metrics_files), 0)
        
        # 4. メトリクスファイルの内容を確認
        for file in metrics_files:
            if file.endswith(".json"):
                file_path = os.path.join(self.logs_dir, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    metrics_data = json.load(f)
                    
                    # 基本的なメトリクス項目が含まれていることを確認
                    self.assertIn("phase", metrics_data)
                    self.assertIn("timestamp", metrics_data)
                    self.assertIn("duration", metrics_data)
                    self.assertIn("success", metrics_data)


if __name__ == "__main__":
    unittest.main()
