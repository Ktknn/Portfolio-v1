import pandas as pd
import schedule
import time
from vnstock import Listing
import os
import logging
import argparse

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Đường dẫn đến thư mục 'data'
data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(data_dir, exist_ok=True)
file_path = os.path.join(data_dir, "company_info.csv")

# Hàm lưu DataFrame vào file CSV
def save_to_csv(df, file_path):
    try:
        df.to_csv(file_path, mode='w', header=True, index=False)
        logging.info(f"Dữ liệu đã được ghi đè lên file {file_path}!")
    except Exception as e:
        logging.error(f"Lỗi khi lưu dữ liệu vào CSV: {e}")

# --- MỚI: Hàm chuẩn hóa ngành theo thị trường Việt Nam ---
def map_vietnam_sector(row):
    """
    Hàm này dùng ICB Level 2 và 3 để phân loại lại ngành 
    cho sát với thực tế đầu tư tại Việt Nam.
    """
    # Chuyển về string để tránh lỗi nếu dữ liệu là NaN
    level1 = str(row.get('icb_name1', ''))
    level2 = str(row.get('icb_name2', ''))
    level3 = str(row.get('icb_name3', ''))
    
    # 1. Tách nhóm Tài chính
    if level2 == 'Bất động sản':
        return 'Bất động sản'
    if level2 == 'Ngân hàng':
        return 'Ngân hàng'
    if 'tài chính' in level3.lower() or 'chứng khoán' in level3.lower():
        return 'Chứng khoán'
    if 'bảo hiểm' in level3.lower():
        return 'Bảo hiểm'

    # 2. Tách nhóm Tài nguyên / Vật liệu
    if 'kim loại' in level3.lower() or 'thép' in level3.lower():
        return 'Thép'
    if 'hóa chất' in level3.lower():
        return 'Hóa chất & Phân bón'
    
    # 3. Nhóm Dầu khí & Tiện ích
    if level2 == 'Dầu khí':
        return 'Dầu khí'
    if 'điện' in level3.lower() or 'khí đốt' in level3.lower() or 'nước' in level3.lower():
        return 'Điện, Nước & Xăng dầu'

    # 4. Nhóm Bán lẻ & Tiêu dùng
    if level2 == 'Bán lẻ':
        return 'Bán lẻ'
    if level2 == 'Thực phẩm và đồ uống':
        return 'Thực phẩm & Đồ uống'
        
    # 5. Nhóm Công nghệ
    if level2 == 'Công nghệ':
        return 'Công nghệ'

    # 6. Nhóm Xây dựng & Vật liệu xây dựng
    if level3 == 'Xây dựng và vật liệu':
        return 'Xây dựng & VLXD'

    # Mặc định: Nếu không rơi vào các case trên thì lấy Level 2
    return level2

# Hàm chính để thu thập dữ liệu và lưu vào CSV
def fetch_listing_dataframe():
    """Tải dữ liệu mã cổ phiếu cùng thông tin ngành và sàn giao dịch."""
    listing = Listing()

    logging.info("Đang tải dữ liệu phân ngành từ vnstock...")
    industries_df = listing.symbols_by_industries()
    if industries_df is None or industries_df.empty:
        raise ValueError("Không thể lấy dữ liệu phân ngành từ vnstock.symbols_by_industries().")

    logging.info("Đang tải dữ liệu sàn giao dịch từ vnstock...")
    exchanges_df = listing.symbols_by_exchange()
    if exchanges_df is None or exchanges_df.empty:
        raise ValueError("Không thể lấy dữ liệu sàn giao dịch từ vnstock.symbols_by_exchange().")

    exchanges_df = exchanges_df.copy()
    exchanges_df['type'] = exchanges_df['type'].astype(str).str.upper()
    exchanges_df = exchanges_df[exchanges_df['type'] == 'STOCK']
    exchanges_df = exchanges_df[['symbol', 'exchange']].drop_duplicates('symbol')
    exchanges_df['exchange'] = exchanges_df['exchange'].astype(str).str.upper()
    exchanges_df['exchange'] = exchanges_df['exchange'].replace({'HSX': 'HOSE'})

    industries_df = industries_df.copy()
    industries_df['icb_code1'] = industries_df['icb_code1'].fillna('').astype(str).str.strip()

    icb_lookup = listing.industries_icb()
    if icb_lookup is None or icb_lookup.empty:
        logging.warning("Không thể tải bảng tra cứu ICB level 1, sẽ sử dụng Level 2 để thay thế.")
        level1_map = {}
    else:
        level1_df = icb_lookup.loc[icb_lookup['level'] == 1, ['icb_code', 'icb_name']].dropna(subset=['icb_code'])
        level1_df['icb_code'] = level1_df['icb_code'].astype(str).str.strip()
        level1_map = dict(zip(level1_df['icb_code'], level1_df['icb_name']))

    industries_df['icb_name1'] = industries_df['icb_code1'].map(level1_map).fillna(industries_df['icb_name2'])
    industries_df = industries_df[['symbol', 'organ_name', 'icb_name1', 'icb_name2', 'icb_name3']]
    for column in ['icb_name1', 'icb_name2', 'icb_name3']:
        industries_df[column] = industries_df[column].fillna('')

    merged_df = industries_df.merge(exchanges_df, on='symbol', how='left')
    merged_df['exchange'] = merged_df['exchange'].astype(str).str.upper()

    return merged_df


def run_task():
    logging.info("Bắt đầu thu thập dữ liệu...")
    try:
        logging.info("Đang tải danh sách cổ phiếu và thông tin ngành chi tiết từ vnstock Listing API...")
        df_full = fetch_listing_dataframe()

        logging.info(f"Đã tải về {len(df_full)} mã chứng khoán.")

        required_cols = ['symbol', 'organ_name', 'exchange', 'icb_name1', 'icb_name2', 'icb_name3']
        missing_cols = [col for col in required_cols if col not in df_full.columns]
        if missing_cols:
            raise ValueError(f"Thiếu các cột bắt buộc: {missing_cols}")

        df_full = df_full.dropna(subset=['symbol']).copy()
        df_full = df_full[required_cols]

        logging.info("Đang chuẩn hóa tên ngành...")
        df_full['sector_vietnam'] = df_full.apply(map_vietnam_sector, axis=1)

        df_final = df_full.rename(columns={'sector_vietnam': 'icb_name'})
        df_final = df_final[['symbol', 'organ_name', 'icb_name', 'exchange']]
        df_final = df_final[df_final['exchange'].isin(['HOSE', 'HNX', 'UPCOM'])]

        logging.info(f"Kết quả cuối cùng sau khi xử lý: {len(df_final)} dòng.")
        save_to_csv(df_final, file_path)
        logging.info("Công việc đã hoàn thành và dữ liệu được cập nhật!")

    except Exception as e:
        logging.error(f"Lỗi trong quá trình thu thập dữ liệu: {e}")
        import traceback
        traceback.print_exc()

# Chế độ chạy: ngay hoặc schedule
def main():
    parser = argparse.ArgumentParser(description="Thu thập dữ liệu chứng khoán.")
    parser.add_argument('--mode', choices=['now', 'schedule'], default='now', help='Chọn chế độ chạy: now (ngay) hoặc schedule (lập lịch)')
    args = parser.parse_args()
    if args.mode == 'now':
        run_task()
    else:
        logging.info("Thiết lập lịch chạy hàng ngày lúc 08:00...")
        schedule.every().day.at("08:00").do(run_task)
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    main()