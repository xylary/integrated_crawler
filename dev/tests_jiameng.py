from pipelines.pipeline_jiameng import *
import csv


info = get_info(max_page=84)

with open('jiameng_result.csv', 'w+', encoding='ANSI', newline='') as csvfile:
    fieldnames = ['brand_name', 'food_category', 'total_stores', 'attendance_fee', 'corp_name',
                  'corp_address', 'corp_type', 'corp_capital', 'corp_reg_date', 'corp_location']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for item in info:
        try:
            writer.writerow(item)
        except UnicodeEncodeError as e:
            print(item)

