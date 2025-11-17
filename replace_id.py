import pandas as pd
import csv

# 1. 定義 user_id 的置換對應表
USER_ID_MAPPING = {
    6: 60,
    10: 30,
    13: 17,
    22: 32,
    54: 38,
    73: 69,
    85: 66,
    127: 65,
    580: 164,
    2793: 490
}
# 針對置換邏輯，將映射表的鍵/值轉為字串，以便處理 CSV 檔案中可能為字串的 user_id
USER_ID_MAPPING_STR = {str(k): str(v) for k, v in USER_ID_MAPPING.items()}


# 輸入檔案名稱
input_filename = "file_info_202511171011.csv"
# 輸出檔案名稱
output_filename = input_filename.replace(".csv", "-out.csv")

def replace_user_id_and_save(input_file, output_file, mapping_str):
    """
    讀取 CSV 檔案，確保 user_id 欄位保持其原始類型 (字串)，
    根據對應表替換值，並以 UTF-8 BOM 格式儲存，保留字串值的引號。
    """
    try:
        # 讀取 CSV 檔案，明確指定 'user_id' 欄位為字串 (str)，保留原始資料的格式
        df = pd.read_csv(input_file, encoding='utf-8', dtype={'user_id': str})
        
        print("✅ 成功讀取檔案: {}，共 {} 筆資料。".format(input_file, len(df)))

        # 執行置換操作：如果 user_id 在 mapping 中，則使用新值；否則使用原值
        # 因為 df['user_id'] 和 mapping_str 的鍵/值都是字串，替換結果也是字串
        df['user_id'] = df['user_id'].apply(lambda x: mapping_str.get(x, x))

        print("🔄 user_id 欄位替換完成。")
        
        # 儲存檔案
        # 這裡移除或修改 `quoting` 參數：
        # - 移除 `quoting` 參數 (預設為 csv.QUOTE_MINIMAL)
        # - 使用 `quoting=csv.QUOTE_MINIMAL`：只對包含特殊字元 (如逗號、引號) 的字串加引號
        # - 使用 `quoting=csv.QUOTE_NONNUMERIC`：只對非數值字串加引號 (您原本的設定)
        
        # 由於您希望 `"5"` 輸出為 `"5"` (即字串加上引號)，
        # 我們**移除**您原本的 `quoting=csv.QUOTE_NONNUMERIC`，讓 Pandas 預設處理
        # 如果 df['user_id'] 是字串 (如 "5") 且不含逗號，Pandas 預設可能不會加引號，
        # 所以為了確保 `"5"` 被視為字串並輸出引號，我們應該確保 Pandas 知道它是字串。

        # 最佳做法：因為 'user_id' 欄位現在是 object (字串) 類型，
        # to_csv 在 QUOTE_NONNUMERIC 下會對它加引號。
        # 但如果原始資料是 `"5"`，讀入後可能變成 '5' (字串，不含引號)
        
        # **最穩妥的處理方式：**
        # 讓 `user_id` 欄位保持字串類型，並使用 `csv.QUOTE_NONNUMERIC` 來確保非數值欄位被引號包圍
        df.to_csv(output_file, 
                  index=False, 
                  encoding='utf-8-sig', 
                  # 確保非數值欄位被引號包圍，數值欄位不加引號
                  quoting=csv.QUOTE_NONNUMERIC) 
        
        print("🎉 檔案已成功儲存為: {}，編碼格式為 UTF-8-BOM。".format(output_file))

    except FileNotFoundError:
        print("❌ 錯誤：找不到檔案 {}。".format(input_file))
    except Exception as e:
        print("❌ 處理檔案時發生錯誤: {}".format(e))

# 執行函式
replace_user_id_and_save(input_filename, output_filename, USER_ID_MAPPING_STR)