from django.db import models


class HeaderData(models.Model):
    id = models.AutoField(primary_key=True)
    device_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    firmware_version = models.CharField(max_length=100, null=True, blank=True)
    location_tag = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = "header_data"
        indexes = [models.Index(fields=["device_id", "-timestamp"])]


class McuMonitoring(models.Model):
    id = models.AutoField(primary_key=True)
    device_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    carrier_board_mcu = models.CharField(max_length=100, null=True, blank=True)
    uptime_seconds = models.BigIntegerField(null=True, blank=True)
    vcc_main_v = models.FloatField(null=True, blank=True)
    i2c_bus_status = models.CharField(max_length=50, null=True, blank=True)
    spi_bus_status = models.CharField(max_length=50, null=True, blank=True)
    watchdog_resets = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "mcu_monitoring"
        indexes = [models.Index(fields=["device_id", "-timestamp"])]


class DeviceHealth(models.Model):
    id = models.AutoField(primary_key=True)
    device_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    soc_temp_c = models.FloatField(null=True, blank=True)
    gpu_load_percent = models.FloatField(null=True, blank=True)
    cpu_load_percent = models.JSONField(null=True, blank=True)
    ram_usage_mb = models.IntegerField(null=True, blank=True)
    emmc_storage_free_gb = models.FloatField(null=True, blank=True)
    power_mode = models.CharField(max_length=50, null=True, blank=True)
    fan_speed_rpm = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "device_health"
        indexes = [models.Index(fields=["device_id", "-timestamp"])]


class EnvData(models.Model):
    id = models.AutoField(primary_key=True)
    device_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    sht45_temperature = models.FloatField(null=True, blank=True)
    sht45_humidity = models.FloatField(null=True, blank=True)
    bme688_temperature = models.FloatField(null=True, blank=True)
    bme688_humidity = models.FloatField(null=True, blank=True)
    bme688_pressure = models.FloatField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "env_data"
        indexes = [models.Index(fields=["device_id", "-timestamp"])]


class VocData(models.Model):
    id = models.AutoField(primary_key=True)
    device_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    sgp41_voc_index = models.IntegerField(null=True, blank=True)
    sgp41_nox_index = models.IntegerField(null=True, blank=True)
    zmod4410_voc_concentration = models.FloatField(null=True, blank=True)
    bme688_gas_resistance = models.FloatField(null=True, blank=True)
    tgs2602_odor_level = models.FloatField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "voc_data"
        indexes = [models.Index(fields=["device_id", "-timestamp"])]


class GasData(models.Model):
    id = models.AutoField(primary_key=True)
    device_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    mq135_air_quality = models.FloatField(null=True, blank=True)
    mq136_sulfur_level = models.FloatField(null=True, blank=True)
    tgs2600_contamination = models.FloatField(null=True, blank=True)
    ethylene_sensor_value = models.FloatField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "gas_data"
        indexes = [models.Index(fields=["device_id", "-timestamp"])]


class PmData(models.Model):
    id = models.AutoField(primary_key=True)
    device_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    pms7003_pm1 = models.FloatField(null=True, blank=True)
    pms7003_pm2_5 = models.FloatField(null=True, blank=True)
    pms7003_pm10 = models.FloatField(null=True, blank=True)
    sps30_pm1 = models.FloatField(null=True, blank=True)
    sps30_pm2_5 = models.FloatField(null=True, blank=True)
    sps30_pm10 = models.FloatField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "pm_data"
        indexes = [models.Index(fields=["device_id", "-timestamp"])]


class SpectralData(models.Model):
    id = models.AutoField(primary_key=True)
    device_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    as7341_channels = models.JSONField(null=True, blank=True)
    as7265x_channels = models.JSONField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "spectral_data"
        indexes = [models.Index(fields=["device_id", "-timestamp"])]


class ForceData(models.Model):
    id = models.AutoField(primary_key=True)
    device_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    loadcell_2kg_force = models.FloatField(null=True, blank=True)
    loadcell_5kg_force = models.FloatField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "force_data"
        indexes = [models.Index(fields=["device_id", "-timestamp"])]


class FlowData(models.Model):
    id = models.AutoField(primary_key=True)
    device_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    mpxv7002dp_pressure_diff = models.FloatField(null=True, blank=True)
    sfm3003_flow_rate = models.FloatField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "flow_data"
        indexes = [models.Index(fields=["device_id", "-timestamp"])]


class SystemData(models.Model):
    id = models.AutoField(primary_key=True)
    device_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    ds18b20_temperature = models.FloatField(null=True, blank=True)
    ina219_current = models.FloatField(null=True, blank=True)
    ina219_power = models.FloatField(null=True, blank=True)
    reed_switch_state = models.BooleanField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "system_data"
        indexes = [models.Index(fields=["device_id", "-timestamp"])]


class AcousticData(models.Model):
    id = models.AutoField(primary_key=True)
    device_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    inmp441_noise_level = models.FloatField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "acoustic_data"
        indexes = [models.Index(fields=["device_id", "-timestamp"])]


class DistanceData(models.Model):
    id = models.AutoField(primary_key=True)
    device_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    vl53l1x_fill_height = models.FloatField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "distance_data"
        indexes = [models.Index(fields=["device_id", "-timestamp"])]


class SensorData(models.Model):
    id = models.AutoField(primary_key=True)
    device_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    payload = models.JSONField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "sensor_data"
        indexes = [models.Index(fields=["device_id", "-timestamp"])]


class ImageMetadata(models.Model):
    id = models.AutoField(primary_key=True)
    device_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField()
    camera_id = models.CharField(max_length=50, null=True, blank=True)
    frame_id = models.BigIntegerField(null=True, blank=True)
    resolution = models.CharField(max_length=50, null=True, blank=True)
    format = models.CharField(max_length=20, null=True, blank=True)
    storage_path = models.CharField(max_length=500, null=True, blank=True)
    inference_applied = models.BooleanField(null=True, blank=True)
    detected_objects = models.JSONField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "image_metadata"
        indexes = [models.Index(fields=["device_id", "-timestamp"])]
