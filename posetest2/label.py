import pandas as pd
import json

# 🔄 CSV 불러오기
train_df = pd.read_csv("E:/pose/train_metadata.csv")
val_df = pd.read_csv("E:/pose/val_metadata.csv")
test_df = pd.read_csv("E:/pose/test_metadata.csv")

# 🔗 통합
all_df = pd.concat([train_df, val_df, test_df]).reset_index(drop=True)

# ✅ 매핑 생성 (label → 단어)
index_to_word = dict(zip(all_df['label'], all_df['단어']))

# 💾 JSON으로 저장
json_path = "E:/pose/index_to_word.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(index_to_word, f, ensure_ascii=False, indent=2)

print(f"✅ 라벨 매핑이 저장되었습니다: {json_path}")
print("예시:", list(index_to_word.items())[:5])
