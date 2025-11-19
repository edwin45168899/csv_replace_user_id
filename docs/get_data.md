# 統計要匯出的所有統計資料
```sql
-- 取得 131 資料

SELECT *
FROM alatech.activity_day
WHERE user_id IN (
85
,1069
)
AND year_num >= 2024
;

SELECT *
FROM alatech.activity_day_of_first_monday
WHERE user_id IN (
85
,1069
)
AND year_num >= 2024
;

SELECT *
FROM alatech.activity_day_weight_training
WHERE user_id IN (
85
,1069
)
AND year_num >= 2024
;

SELECT *
FROM alatech.activity_day_weight_training_of_first_monday
WHERE user_id IN (
85
,1069
)
AND year_num >= 2024
;

SELECT *
FROM alatech.activity_month
WHERE user_id IN (
85
,1069
)
AND year_num >= 2024
;

SELECT *
FROM alatech.activity_month_weight_training
WHERE user_id IN (
85
,1069
)
AND year_num >= 2024
;

SELECT *
FROM alatech.activity_week
WHERE user_id IN (
85
,1069
)
AND year_num >= 2024
;

SELECT *
FROM alatech.activity_week_of_first_monday
WHERE user_id IN (
85
,1069
)
AND year_num >= 2024
;

SELECT *
FROM alatech.activity_week_weight_training
WHERE user_id IN (
85
,1069
)
AND year_num >= 2024
;

SELECT *
FROM alatech.activity_week_weight_training_of_first_monday
WHERE user_id IN (
85
,1069
)
AND year_num >= 2024
;


SELECT *
FROM alatech.activity_info
WHERE user_id IN (
85
,1069
)
AND start_time >= '2024-0101-9T00:00:00.000+08:00'
;

SELECT *
FROM alatech.file_info
WHERE user_id IN (
85
,1069
)
AND creation_date >= '2024-0101-9T00:00:00.000+08:00'
;

```