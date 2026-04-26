from django.db import migrations


ENV_VIEW_SQL = """
CREATE OR REPLACE VIEW env_data_new AS
SELECT
    COALESCE(r.source_timestamp, r.created_at) AS timestamp,
    r.device_id,
    MAX(
        CASE WHEN s.sensor_code IN ('SHT45')
            THEN COALESCE(
                NULLIF(r.payload->>'sht45_temperature', '')::double precision,
                NULLIF(r.payload->>'temperature', '')::double precision
            )
        END
    ) AS sht45_temperature,
    MAX(
        CASE WHEN s.sensor_code IN ('SHT45')
            THEN COALESCE(
                NULLIF(r.payload->>'sht45_humidity', '')::double precision,
                NULLIF(r.payload->>'humidity', '')::double precision
            )
        END
    ) AS sht45_humidity,
    MAX(
        CASE WHEN s.sensor_code IN ('BME688')
            THEN COALESCE(
                NULLIF(r.payload->>'bme688_temperature', '')::double precision,
                NULLIF(r.payload->>'temperature', '')::double precision
            )
        END
    ) AS bme688_temperature,
    MAX(
        CASE WHEN s.sensor_code IN ('BME688')
            THEN COALESCE(
                NULLIF(r.payload->>'bme688_humidity', '')::double precision,
                NULLIF(r.payload->>'humidity', '')::double precision
            )
        END
    ) AS bme688_humidity,
    MAX(
        CASE WHEN s.sensor_code IN ('BME688')
            THEN COALESCE(
                NULLIF(r.payload->>'bme688_pressure', '')::double precision,
                NULLIF(r.payload->>'pressure', '')::double precision
            )
        END
    ) AS bme688_pressure
FROM data_ingestion_sensorreading r
JOIN data_ingestion_sensor s ON r.sensor_id = s.id
GROUP BY COALESCE(r.source_timestamp, r.created_at), r.device_id;
"""


GAS_VIEW_SQL = """
CREATE OR REPLACE VIEW gas_data_new AS
SELECT
    COALESCE(r.source_timestamp, r.created_at) AS timestamp,
    r.device_id,
    MAX(
        CASE WHEN s.sensor_code IN ('ETHYLENE_SENSOR', 'ETHYLENE')
            THEN COALESCE(
                NULLIF(r.payload->>'ethylene_sensor_value', '')::double precision,
                NULLIF(r.payload->>'value', '')::double precision
            )
        END
    ) AS ethylene_sensor_value,
    MAX(
        CASE WHEN s.sensor_code IN ('MQ135')
            THEN COALESCE(
                NULLIF(r.payload->>'mq135_air_quality', '')::double precision,
                NULLIF(r.payload->>'air_quality', '')::double precision
            )
        END
    ) AS mq135_air_quality,
    MAX(
        CASE WHEN s.sensor_code IN ('MQ136')
            THEN COALESCE(
                NULLIF(r.payload->>'mq136_sulfur_level', '')::double precision,
                NULLIF(r.payload->>'sulfur_level', '')::double precision
            )
        END
    ) AS mq136_sulfur_level,
    MAX(
        CASE WHEN s.sensor_code IN ('TGS2600')
            THEN COALESCE(
                NULLIF(r.payload->>'tgs2600_contamination', '')::double precision,
                NULLIF(r.payload->>'contamination', '')::double precision
            )
        END
    ) AS tgs2600_contamination
FROM data_ingestion_sensorreading r
JOIN data_ingestion_sensor s ON r.sensor_id = s.id
GROUP BY COALESCE(r.source_timestamp, r.created_at), r.device_id;
"""


PM_VIEW_SQL = """
CREATE OR REPLACE VIEW pm_data_new AS
SELECT
    COALESCE(r.source_timestamp, r.created_at) AS timestamp,
    r.device_id,
    MAX(
        CASE WHEN s.sensor_code IN ('PMS7003')
            THEN COALESCE(
                NULLIF(r.payload->>'pms7003_pm1', '')::double precision,
                NULLIF(r.payload->>'pm1', '')::double precision
            )
        END
    ) AS pms7003_pm1,
    MAX(
        CASE WHEN s.sensor_code IN ('PMS7003')
            THEN COALESCE(
                NULLIF(r.payload->>'pms7003_pm2_5', '')::double precision,
                NULLIF(r.payload->>'pm2_5', '')::double precision,
                NULLIF(r.payload->>'pm25', '')::double precision
            )
        END
    ) AS pms7003_pm2_5,
    MAX(
        CASE WHEN s.sensor_code IN ('PMS7003')
            THEN COALESCE(
                NULLIF(r.payload->>'pms7003_pm10', '')::double precision,
                NULLIF(r.payload->>'pm10', '')::double precision
            )
        END
    ) AS pms7003_pm10,
    MAX(
        CASE WHEN s.sensor_code IN ('SPS30')
            THEN COALESCE(
                NULLIF(r.payload->>'sps30_pm1', '')::double precision,
                NULLIF(r.payload->>'pm1', '')::double precision
            )
        END
    ) AS sps30_pm1,
    MAX(
        CASE WHEN s.sensor_code IN ('SPS30')
            THEN COALESCE(
                NULLIF(r.payload->>'sps30_pm2_5', '')::double precision,
                NULLIF(r.payload->>'pm2_5', '')::double precision,
                NULLIF(r.payload->>'pm25', '')::double precision
            )
        END
    ) AS sps30_pm2_5,
    MAX(
        CASE WHEN s.sensor_code IN ('SPS30')
            THEN COALESCE(
                NULLIF(r.payload->>'sps30_pm10', '')::double precision,
                NULLIF(r.payload->>'pm10', '')::double precision
            )
        END
    ) AS sps30_pm10,
    MAX(
        CASE WHEN s.sensor_code IN ('PMS7003', 'SPS30', 'PM')
            THEN NULLIF(r.payload->>'pm1', '')::double precision
        END
    ) AS pm1,
    MAX(
        CASE WHEN s.sensor_code IN ('PMS7003', 'SPS30', 'PM')
            THEN COALESCE(
                NULLIF(r.payload->>'pm25', '')::double precision,
                NULLIF(r.payload->>'pm2_5', '')::double precision
            )
        END
    ) AS pm25,
    MAX(
        CASE WHEN s.sensor_code IN ('PMS7003', 'SPS30', 'PM')
            THEN NULLIF(r.payload->>'pm10', '')::double precision
        END
    ) AS pm10,
    MAX(
        CASE WHEN s.sensor_code IN ('PMS7003', 'SPS30', 'PM')
            THEN NULLIF(r.payload->>'particle_count', '')::double precision
        END
    ) AS particle_count
FROM data_ingestion_sensorreading r
JOIN data_ingestion_sensor s ON r.sensor_id = s.id
GROUP BY COALESCE(r.source_timestamp, r.created_at), r.device_id;
"""


class Migration(migrations.Migration):
    dependencies = [
        ("api_gateway", "0002_frontendclient_module_access_apiendpoint_and_more"),
        ("data_ingestion", "0002_datavalidationrule_source_kind_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            sql=ENV_VIEW_SQL,
            reverse_sql="DROP VIEW IF EXISTS env_data_new;",
        ),
        migrations.RunSQL(
            sql=GAS_VIEW_SQL,
            reverse_sql="DROP VIEW IF EXISTS gas_data_new;",
        ),
        migrations.RunSQL(
            sql=PM_VIEW_SQL,
            reverse_sql="DROP VIEW IF EXISTS pm_data_new;",
        ),
        migrations.RunSQL(
            sql=(
                "CREATE INDEX IF NOT EXISTS idx_data_ingestion_sensorreading_sensor_time "
                "ON data_ingestion_sensorreading (sensor_id, source_timestamp);"
            ),
            reverse_sql="DROP INDEX IF EXISTS idx_data_ingestion_sensorreading_sensor_time;",
        ),
        migrations.RunSQL(
            sql=(
                "CREATE INDEX IF NOT EXISTS idx_data_ingestion_sensor_sensor_code "
                "ON data_ingestion_sensor (sensor_code);"
            ),
            reverse_sql="DROP INDEX IF EXISTS idx_data_ingestion_sensor_sensor_code;",
        ),
    ]
