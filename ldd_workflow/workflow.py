#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LDDワークフロー実行エンジン
"""

import os
import json
import logging
import importlib
from datetime import datetime

logger = logging.getLogger(__name__)

class LDDWorkflow:
    """LDDワークフローを実行するクラス"""
    
    def __init__(self, config_path="config.json"):
        """
        初期化メソッド
        
        Args:
            config_path (str): 設定ファイルのパス
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.phases = ["learn", "develop", "deploy"]
        self.current_phase = None
        self.phase_modules = {}
        
    def _load_config(self):
        """設定ファイルを読み込む"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                logger.warning(f"設定ファイルが見つかりません: {self.config_path}")
                return {
                    "phases": {
                        "learn": {"enabled": True, "timeout": 3600},
                        "develop": {"enabled": True, "timeout": 7200},
                        "deploy": {"enabled": True, "timeout": 1800}
                    },
                    "metrics": {
                        "collect": True,
                        "storage_path": "../logs/metrics"
                    },
                    "feedback": {
                        "enabled": True,
                        "auto_adjust": True
                    }
                }
        except Exception as e:
            logger.error(f"設定ファイル読み込み中にエラーが発生しました: {str(e)}")
            return {}
    
    def _save_config(self):
        """設定ファイルを保存する"""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            logger.info(f"設定ファイルを保存しました: {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"設定ファイル保存中にエラーが発生しました: {str(e)}")
            return False
    
    def _load_phase_module(self, phase):
        """フェーズモジュールを読み込む"""
        try:
            if phase in self.phase_modules:
                return self.phase_modules[phase]
            
            module_name = f"ldd_workflow.{phase}"
            module = importlib.import_module(module_name)
            
            # モジュールからフェーズクラスを取得
            class_name = f"{phase.capitalize()}Phase"
            phase_class = getattr(module, class_name)
            
            self.phase_modules[phase] = phase_class()
            return self.phase_modules[phase]
        except Exception as e:
            logger.error(f"フェーズモジュール '{phase}' の読み込み中にエラーが発生しました: {str(e)}")
            return None
    
    def run(self, start_phase=None):
        """
        ワークフローを実行
        
        Args:
            start_phase (str, optional): 開始フェーズ
            
        Returns:
            dict: 実行結果
        """
        results = {}
        start_idx = 0
        
        # 開始フェーズの設定
        if start_phase and start_phase in self.phases:
            start_idx = self.phases.index(start_phase)
        
        # 各フェーズを順番に実行
        for i in range(start_idx, len(self.phases)):
            phase = self.phases[i]
            self.current_phase = phase
            
            # フェーズが無効の場合はスキップ
            if not self.config["phases"].get(phase, {}).get("enabled", True):
                logger.info(f"フェーズ '{phase}' は無効化されているためスキップします")
                results[phase] = {"status": "skipped"}
                continue
            
            logger.info(f"フェーズ '{phase}' を開始します")
            
            # フェーズモジュールの読み込みと実行
            phase_module = self._load_phase_module(phase)
            if phase_module:
                try:
                    # フェーズの実行
                    phase_config = self.config["phases"].get(phase, {})
                    phase_result = phase_module.execute(phase_config)
                    
                    # 結果の記録
                    results[phase] = {
                        "status": "success" if phase_result.get("success", False) else "failed",
                        "data": phase_result
                    }
                    
                    # メトリクスの収集
                    if self.config["metrics"].get("collect", False):
                        self._collect_metrics(phase, phase_result)
                    
                    # フェーズが失敗した場合は中断
                    if not phase_result.get("success", False):
                        logger.warning(f"フェーズ '{phase}' が失敗したためワークフローを中断します")
                        break
                    
                except Exception as e:
                    logger.error(f"フェーズ '{phase}' の実行中にエラーが発生しました: {str(e)}")
                    results[phase] = {
                        "status": "error",
                        "error": str(e)
                    }
                    break
            else:
                results[phase] = {
                    "status": "error",
                    "error": f"フェーズモジュール '{phase}' を読み込めませんでした"
                }
                break
            
            logger.info(f"フェーズ '{phase}' が完了しました")
        
        self.current_phase = None
        return results
    
    def _collect_metrics(self, phase, result):
        """メトリクスを収集"""
        try:
            metrics_path = self.config["metrics"].get("storage_path", "../logs/metrics")
            os.makedirs(metrics_path, exist_ok=True)
            
            # メトリクスファイル名の生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            metrics_file = os.path.join(metrics_path, f"{phase}_{timestamp}.json")
            
            # メトリクスデータの構築
            metrics_data = {
                "phase": phase,
                "timestamp": datetime.now().isoformat(),
                "duration": result.get("duration", 0),
                "success": result.get("success", False),
                "metrics": result.get("metrics", {})
            }
            
            # メトリクスの保存
            with open(metrics_file, "w", encoding="utf-8") as f:
                json.dump(metrics_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"フェーズ '{phase}' のメトリクスを保存しました: {metrics_file}")
            return True
        except Exception as e:
            logger.error(f"メトリクス収集中にエラーが発生しました: {str(e)}")
            return False


if __name__ == "__main__":
    # ロギング設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # ワークフローの実行
    workflow = LDDWorkflow()
    results = workflow.run()
    
    print(f"ワークフロー実行結果: {json.dumps(results, ensure_ascii=False, indent=2)}")
