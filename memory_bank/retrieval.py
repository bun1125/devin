#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
メモリーバンク検索モジュール
"""

import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MemoryRetrieval:
    """メモリーデータの検索を行うクラス"""
    
    def __init__(self, storage_path="./data"):
        """
        初期化メソッド
        
        Args:
            storage_path (str): ストレージパス
        """
        self.storage_path = storage_path
        
    def search_by_key(self, key_pattern):
        """
        キーパターンによる検索
        
        Args:
            key_pattern (str): 検索キーパターン
            
        Returns:
            list: マッチしたキーのリスト
        """
        try:
            files = os.listdir(self.storage_path)
            keys = [f.replace(".json", "") for f in files if f.endswith(".json")]
            
            # パターンマッチング
            matched_keys = [k for k in keys if key_pattern in k]
            
            logger.info(f"キーパターン '{key_pattern}' で {len(matched_keys)} 件のデータが見つかりました")
            return matched_keys
        except Exception as e:
            logger.error(f"キー検索中にエラーが発生しました: {str(e)}")
            return []
    
    def search_by_content(self, query):
        """
        コンテンツによる検索
        
        Args:
            query (str): 検索クエリ
            
        Returns:
            list: マッチしたデータのリスト (キーと内容)
        """
        try:
            results = []
            files = os.listdir(self.storage_path)
            
            for file in files:
                if not file.endswith(".json"):
                    continue
                
                key = file.replace(".json", "")
                file_path = os.path.join(self.storage_path, file)
                
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        
                        # データ内容を文字列化して検索
                        data_str = json.dumps(data, ensure_ascii=False)
                        if query.lower() in data_str.lower():
                            results.append({
                                "key": key,
                                "data": data["data"],
                                "metadata": data["metadata"]
                            })
                    except json.JSONDecodeError:
                        logger.warning(f"JSONデコードエラー: {file}")
            
            logger.info(f"クエリ '{query}' で {len(results)} 件のデータが見つかりました")
            return results
        except Exception as e:
            logger.error(f"コンテンツ検索中にエラーが発生しました: {str(e)}")
            return []
    
    def get_recent(self, limit=10):
        """
        最近のデータを取得
        
        Args:
            limit (int): 取得する最大件数
            
        Returns:
            list: 最近のデータリスト
        """
        try:
            files = os.listdir(self.storage_path)
            json_files = [f for f in files if f.endswith(".json")]
            
            # ファイルの更新日時でソート
            file_times = []
            for file in json_files:
                file_path = os.path.join(self.storage_path, file)
                mtime = os.path.getmtime(file_path)
                file_times.append((file, mtime))
            
            # 新しい順にソート
            file_times.sort(key=lambda x: x[1], reverse=True)
            
            # 結果の取得
            results = []
            for file, _ in file_times[:limit]:
                key = file.replace(".json", "")
                file_path = os.path.join(self.storage_path, file)
                
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        results.append({
                            "key": key,
                            "data": data["data"],
                            "metadata": data["metadata"]
                        })
                    except json.JSONDecodeError:
                        logger.warning(f"JSONデコードエラー: {file}")
            
            logger.info(f"最近の {len(results)} 件のデータを取得しました")
            return results
        except Exception as e:
            logger.error(f"最近のデータ取得中にエラーが発生しました: {str(e)}")
            return []


if __name__ == "__main__":
    # ロギング設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # テスト用コード
    retrieval = MemoryRetrieval()
    
    # キー検索テスト
    keys = retrieval.search_by_key("test")
    print(f"キー検索結果: {keys}")
    
    # コンテンツ検索テスト
    results = retrieval.search_by_content("テスト")
    print(f"コンテンツ検索結果: {len(results)} 件")
    
    # 最近のデータテスト
    recent = retrieval.get_recent(5)
    print(f"最近のデータ: {len(recent)} 件")
