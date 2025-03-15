#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
メモリーバンク初期化モジュール
"""

import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MemoryBankInitializer:
    """メモリーバンクの初期化を行うクラス"""
    
    def __init__(self, storage_path="./data"):
        """
        初期化メソッド
        
        Args:
            storage_path (str): ストレージパス
        """
        self.storage_path = storage_path
        self.initialized = False
        
    def initialize(self):
        """メモリーバンクの初期化を実行"""
        try:
            # ストレージディレクトリの作成
            os.makedirs(self.storage_path, exist_ok=True)
            
            # 初期化ログの作成
            init_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(os.path.join(self.storage_path, "init_log.txt"), "w") as f:
                f.write(f"Memory Bank Initialized at: {init_time}\n")
            
            self.initialized = True
            logger.info(f"メモリーバンクが正常に初期化されました。保存先: {self.storage_path}")
            return True
        except Exception as e:
            logger.error(f"メモリーバンクの初期化中にエラーが発生しました: {str(e)}")
            return False
    
    def status(self):
        """初期化状態を確認"""
        return {
            "initialized": self.initialized,
            "storage_path": self.storage_path,
            "storage_exists": os.path.exists(self.storage_path) if self.storage_path else False
        }


if __name__ == "__main__":
    # ロギング設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 初期化の実行
    initializer = MemoryBankInitializer()
    success = initializer.initialize()
    
    if success:
        print("メモリーバンクの初期化が完了しました。")
    else:
        print("メモリーバンクの初期化に失敗しました。ログを確認してください。")
