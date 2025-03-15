#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
メモリーバンクストレージモジュール
"""

import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MemoryStorage:
    """メモリーデータの保存と取得を行うクラス"""
    
    def __init__(self, storage_path="./data"):
        """
        初期化メソッド
        
        Args:
            storage_path (str): ストレージパス
        """
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
    def save(self, key, data, metadata=None):
        """
        データを保存
        
        Args:
            key (str): データの識別キー
            data (dict): 保存するデータ
            metadata (dict, optional): メタデータ
            
        Returns:
            bool: 保存成功の場合True
        """
        try:
            if metadata is None:
                metadata = {}
            
            # タイムスタンプの追加
            metadata["timestamp"] = datetime.now().isoformat()
            
            # 保存データの構造化
            storage_data = {
                "data": data,
                "metadata": metadata
            }
            
            # ファイルパスの生成
            file_path = os.path.join(self.storage_path, f"{key}.json")
            
            # JSONとして保存
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(storage_data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"データが正常に保存されました: {key}")
            return True
        except Exception as e:
            logger.error(f"データ保存中にエラーが発生しました: {str(e)}")
            return False
    
    def load(self, key):
        """
        データを読み込み
        
        Args:
            key (str): データの識別キー
            
        Returns:
            dict or None: 読み込んだデータ、失敗時はNone
        """
        try:
            file_path = os.path.join(self.storage_path, f"{key}.json")
            
            if not os.path.exists(file_path):
                logger.warning(f"指定されたキーのデータが見つかりません: {key}")
                return None
            
            with open(file_path, "r", encoding="utf-8") as f:
                storage_data = json.load(f)
            
            logger.info(f"データが正常に読み込まれました: {key}")
            return storage_data["data"]
        except Exception as e:
            logger.error(f"データ読み込み中にエラーが発生しました: {str(e)}")
            return None
    
    def list_keys(self):
        """
        保存されているキーの一覧を取得
        
        Returns:
            list: キーのリスト
        """
        try:
            files = os.listdir(self.storage_path)
            keys = [f.replace(".json", "") for f in files if f.endswith(".json")]
            return keys
        except Exception as e:
            logger.error(f"キー一覧取得中にエラーが発生しました: {str(e)}")
            return []


if __name__ == "__main__":
    # ロギング設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # テスト用コード
    storage = MemoryStorage()
    
    # データ保存テスト
    test_data = {"name": "テストデータ", "value": 123}
    storage.save("test_key", test_data, {"type": "test"})
    
    # データ読み込みテスト
    loaded_data = storage.load("test_key")
    print(f"読み込まれたデータ: {loaded_data}")
    
    # キー一覧テスト
    keys = storage.list_keys()
    print(f"保存されているキー: {keys}")
