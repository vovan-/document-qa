MERGE INTO ${hdpDb}.${tableName} AS target
USING ${outputData} AS update
    ON target.id = update.id
WHEN MATCHED THEN UPDATE SET * EXCEPT(dp_create_timestamp)
WHEN NOT MATCHED THEN INSERT *