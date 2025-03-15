#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LDDワークフロー統合テスト
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
from ldd_workflow.workflow import LDDWorkflow
from ldd_workflow.learn import LearnPhase
from ldd_workflow.develop import DevelopPhase
from ldd_workflow.deploy import DeployPhase


class TestLDDWorkflow(unittest.TestCase):
    """LDDワークフローの統合テスト"""
    
    def setUp(self):
        """テスト前の準備"""
        # テスト用の一時ディレクトリを作成
        self.test_dir = tempfile.mkdtemp()
        
        # テスト用の設定ファイルを作成
        self.config_path = os.path.join(self.test_dir, "test_config.json")
        self._create_test_config()
        
        # テスト対象のインスタンスを作成
        self.workflow = LDDWorkflow(config_path=self.config_path)
        
        # 各フェーズのインスタンスを作成
        self.learn_phase = LearnPhase()
        self.develop_phase = DevelopPhase()
        self.deploy_phase = DeployPhase()
    
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
                "storage_path": os.path.join(self.test_dir, "metrics")
            },
            "feedback": {
                "enabled": True,
                "auto_adjust": True
            }
        }
        
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def test_config_loading(self):
        """設定ファイル読み込みのテスト"""
        # 設定が正しく読み込まれたことを確認
        self.assertIsNotNone(self.workflow.config)
        self.assertTrue(self.workflow.config["phases"]["learn"]["enabled"])
        self.assertEqual(self.workflow.config["phases"]["learn"]["timeout"], 10)
    
    def test_learn_phase(self):
        """学習フェーズのテスト"""
        # 学習フェーズの実行
        config = {"timeout": 5}
        result = self.learn_phase.execute(config)
        
        # 結果の確認
        self.assertTrue(result["success"])
        self.assertIn("duration", result)
        self.assertIn("metrics", result)
        self.assertIn("data", result)
    
    def test_develop_phase(self):
        """開発フェーズのテスト"""
        # 開発フェーズの実行
        config = {"timeout": 5}
        result = self.develop_phase.execute(config)
        
        # 結果の確認
        self.assertIn("success", result)
        self.assertIn("duration", result)
        self.assertIn("metrics", result)
        self.assertIn("data", result)
    
    def test_deploy_phase(self):
        """デプロイフェーズのテスト"""
        # デプロイフェーズの実行
        config = {"timeout": 5}
        result = self.deploy_phase.execute(config)
        
        # 結果の確認
        self.assertIn("success", result)
        self.assertIn("duration", result)
        self.assertIn("metrics", result)
        self.assertIn("data", result)
    
    def test_workflow_execution(self):
        """ワークフロー全体の実行テスト"""
        # ワークフローの実行
        results = self.workflow.run()
        
        # 結果の確認
        self.assertIn("learn", results)
        self.assertIn("develop", results)
        self.assertIn("deploy", results)
        
        # 各フェーズの結果を確認
        for phase in ["learn", "develop", "deploy"]:
            self.assertIn("status", results[phase])
            if results[phase]["status"] == "success":
                self.assertIn("data", results[phase])
    
    def test_partial_workflow(self):
        """一部のフェーズのみ実行するテスト"""
        # 開発フェーズから実行
        results = self.workflow.run(start_phase="develop")
        
        # 結果の確認
        self.assertNotIn("learn", results)
        self.assertIn("develop", results)
        self.assertIn("deploy", results)


if __name__ == "__main__":
    unittest.main()
