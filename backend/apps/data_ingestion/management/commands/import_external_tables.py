import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone as dj_timezone

from apps.data_ingestion.models import DataValidationRule, ImageCapture, SensorReading
from apps.device_manager.models import Device


def _quote_ident(name: str) -> str:
    # SQLite accepts ANSI quoting; this protects against weird column names.
    return '"' + name.replace('"', '""') + '"'


def _safe_str(v) -> str:
    if v is None:
        return ""
    return str(v)


def _parse_datetime(value):
    """
    Best-effort parsing into an aware datetime in UTC.
    Supports:
    - datetime objects
    - unix timestamps (int/float)
    - ISO-8601 strings
    - common sqlite-ish formats via fromisoformat fallback
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        dt = value
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    if isinstance(value, (int, float)):
        # Interpret as unix seconds if it looks like one.
        return datetime.fromtimestamp(float(value), tz=timezone.utc)

    s = str(value).strip()
    if not s:
        return None

    # Try ISO first.
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        pass

    # Try a couple of common formats (no guarantee).
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(s, fmt)
            dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue

    return None


def _pick_column_by_names(columns, *, include_substrings, prefer_exact=None):
    """
    columns: list[{"name": ..., "type": ...}]
    """
    lower_map = {c["name"]: c["name"].lower() for c in columns}

    if prefer_exact:
        for cand in prefer_exact:
            for c in columns:
                if c["name"].lower() == cand.lower():
                    return c["name"]

    for substr in include_substrings:
        s = substr.lower()
        for c in columns:
            if s in lower_map[c["name"]]:
                return c["name"]
    return None


def _pick_device_column(columns):
    # Heuristic: choose columns that look like device/external identifiers.
    return _pick_column_by_names(
        columns,
        prefer_exact=["external_id", "device_id", "deviceexternalid", "externalid"],
        include_substrings=[
            "external",
            "device",
            "dev_id",
            "devicename",
            "device_code",
            "devicecode",
        ],
    )


def _pick_timestamp_column(columns):
    return _pick_column_by_names(
        columns,
        prefer_exact=[
            "timestamp_utc",
            "source_timestamp",
            "captured_at",
            "created_at",
            "recorded_at",
            "collected_at",
        ],
        include_substrings=[
            "timestamp",
            "time",
            "captured",
            "recorded",
            "collected",
            "created",
            "date",
        ],
    )


def _pick_file_uri_column(columns):
    return _pick_column_by_names(
        columns,
        prefer_exact=[
            "file_uri",
            "uri",
            "url",
            "image_uri",
            "image_url",
            "file_path",
            "path",
        ],
        include_substrings=[
            "file_uri",
            "image_uri",
            "image_url",
            "file_path",
            "file",
            "uri",
            "url",
            "path",
        ],
    )


def _pick_camera_id_column(columns):
    return _pick_column_by_names(
        columns,
        prefer_exact=["camera_id", "cameraid"],
        include_substrings=["camera"],
    )


def _pick_sequence_column(columns):
    return _pick_column_by_names(
        columns,
        prefer_exact=["sequence_number"],
        include_substrings=["sequence", "seq"],
    )


@dataclass(frozen=True)
class TableMapping:
    source_table: str
    sensor_type: str | None


DEFAULT_SENSOR_TABLE_TO_TYPE = {
    # Data tables -> UI metric tabs (and DataValidationRule.sensor_type).
    "env_data": "ENV",
    "voc_data": "VOC",
    "gas_data": "Gas",
    "pm_data": "PM",
    "system_data": "System",
    "flow_data": "Flow",
    "force_data": "Force",
    "acoustic_data": "Acoustic",
    "distance_data": "Distance",
    "mcu_monitoring": "System",
    # Extra tables from your screenshot; map conservatively.
    "header_data": "System",
    "spectral_data": "ENV",
    "acoustic_data_log": "Acoustic",
}


class Command(BaseCommand):
    help = (
        "Import raw external *_data tables (SQLite) into your normalized Django tables "
        "(SensorReading and ImageCapture)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--source-db",
            required=True,
            help="Path to the external SQLite DB that contains env_data/voc_data/etc.",
        )
        parser.add_argument(
            "--tables",
            default="",
            help=(
                "Comma-separated list of raw tables to import. "
                "If omitted, imports all keys in DEFAULT_SENSOR_TABLE_TO_TYPE plus image_metadata."
            ),
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Do not write anything; only validate mapping and report counts.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=500,
            help="Bulk insert chunk size (and external fetch chunk size).",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Optional cap of rows per raw table (0 = no cap).",
        )

    def handle(self, *args, **options):
        source_db = options["source_db"]
        tables_opt = options["tables"].strip()
        dry_run = options["dry_run"]
        batch_size = options["batch_size"]
        limit = int(options["limit"] or 0)

        sensor_table_to_type = dict(DEFAULT_SENSOR_TABLE_TO_TYPE)
        raw_tables = []

        if tables_opt:
            raw_tables = [t.strip() for t in tables_opt.split(",") if t.strip()]
        else:
            raw_tables = list(sensor_table_to_type.keys()) + ["image_metadata"]

        self.stdout.write(self.style.NOTICE(f"Source DB: {source_db}"))
        self.stdout.write(self.style.NOTICE(f"Import tables: {', '.join(raw_tables)}"))
        if dry_run:
            self.stdout.write(self.style.WARNING("Dry-run mode enabled."))

        try:
            src_conn = sqlite3.connect(source_db)
        except sqlite3.Error as e:
            raise CommandError(f"Failed to connect to source DB: {e}")

        src_conn.row_factory = None

        # Cache: sensor_type -> active validation rules.
        validation_rules_by_type = {}

        # Cache Devices by external_id.
        device_cache = {}

        now = dj_timezone.now()

        sensor_tables = [t for t in raw_tables if t in sensor_table_to_type]
        image_table_names = [t for t in raw_tables if t == "image_metadata"]

        # Import sensor tables into SensorReading
        for raw_table in sensor_tables:
            sensor_type = sensor_table_to_type[raw_table]
            self.stdout.write(self.style.HTTP_INFO(f"Importing sensor table: {raw_table} -> {sensor_type}"))

            columns = self._get_sqlite_table_info(src_conn, raw_table)
            if not columns:
                self.stdout.write(self.style.WARNING(f"  - Skipping {raw_table}: no columns found"))
                continue

            device_col = _pick_device_column(columns)
            ts_col = _pick_timestamp_column(columns)
            seq_col = _pick_sequence_column(columns)

            if not device_col or not ts_col:
                self.stdout.write(
                    self.style.WARNING(
                        f"  - Skipping {raw_table}: could not detect device column ({device_col}) or timestamp column ({ts_col})"
                    )
                )
                continue

            # Build select list
            selectable_cols = [
                c["name"]
                for c in columns
                if c["name"] not in {device_col, ts_col}
            ]
            select_cols_sql = ", ".join(_quote_ident(c) for c in selectable_cols)

            sql = f'SELECT rowid, {select_cols_sql} FROM {_quote_ident(raw_table)}'
            cur = src_conn.cursor()

            # Since we selected without device/ts, map values by column names:
            # We'll fetch device/ts separately for mapping simplicity.
            # (If the table is huge, you can change this to select all columns at once.)
            sql_with_device_ts = (
                f'SELECT rowid, {_quote_ident(device_col)}, {_quote_ident(ts_col)}, {select_cols_sql} '
                f'FROM {_quote_ident(raw_table)}'
            )
            cur.execute(sql_with_device_ts)

            created_count = 0
            processed = 0
            to_create = []
            created_device_ext_ids = set()
            dry_created_device_ext_ids = set()

            # Fetch chunks
            col_names = [d[0] for d in cur.description]  # rowid + device_col + ts_col + payload cols
            while True:
                rows = cur.fetchmany(batch_size)
                if not rows:
                    break

                for row in rows:
                    processed += 1
                    if limit and processed > limit:
                        break

                    row_dict = dict(zip(col_names, row))
                    rowid = row_dict.get("rowid")
                    device_key = _safe_str(row_dict.get(device_col)).strip()
                    source_ts = _parse_datetime(row_dict.get(ts_col))
                    if not device_key or not rowid or not source_ts:
                        continue

                    signature = f"{device_key}:{raw_table}:{rowid}"

                    # Dedup by signature stored in SensorReading.topic.
                    if SensorReading.objects.filter(topic=signature).exists():
                        continue

                    payload = {
                        k: v
                        for k, v in row_dict.items()
                        if k not in {"rowid", device_col, ts_col}
                    }

                    # Sequence number (if present)
                    sequence_number = None
                    if seq_col and seq_col in row_dict:
                        try:
                            sequence_number = int(row_dict.get(seq_col))
                        except (TypeError, ValueError):
                            sequence_number = None

                    # Validation (mirrors SensorReadingSerializer.create)
                    if sensor_type not in validation_rules_by_type:
                        validation_rules_by_type[sensor_type] = list(
                            DataValidationRule.objects.filter(sensor_type=sensor_type, is_active=True)
                        )
                    active_rules = validation_rules_by_type[sensor_type]

                    errors = []
                    for rule in active_rules:
                        required_fields = rule.required_fields or []
                        for field_name in required_fields:
                            if field_name not in payload:
                                errors.append(f"Missing required field '{field_name}' for {sensor_type}.")

                    validation_status = (
                        SensorReading.ValidationStatus.INVALID if errors else SensorReading.ValidationStatus.VALID
                    )

                    reading = SensorReading(
                        device=self._get_device(device_cache, device_key),
                        sensor_type=sensor_type,
                        payload=payload,
                        source_timestamp=source_ts,
                        ingest_source="etl",
                        topic=signature,
                        sequence_number=sequence_number,
                        validation_status=validation_status,
                        validation_errors=errors,
                        processed_at=now,
                    )
                    if not reading.device:
                        # Device FK missing; skip.
                        continue

                    to_create.append(reading)
                    created_count += 1
                    created_device_ext_ids.add(device_key)
                    if dry_run:
                        dry_created_device_ext_ids.add(device_key)

                if limit and processed > limit:
                    break

                if to_create and not dry_run:
                    with transaction.atomic():
                        SensorReading.objects.bulk_create(to_create, batch_size=batch_size)
                    to_create = []

            # Flush any remaining
            if to_create and not dry_run:
                with transaction.atomic():
                    SensorReading.objects.bulk_create(to_create, batch_size=batch_size)

            if not dry_run and created_device_ext_ids:
                # Keep parity with serializer behavior: mark devices active.
                Device.objects.filter(external_id__in=created_device_ext_ids).exclude(
                    status=Device.DeviceStatus.RETIRED
                ).update(
                    status=Device.DeviceStatus.ACTIVE,
                    last_seen_at=now,
                    last_heartbeat_at=now,
                )

            self.stdout.write(self.style.SUCCESS(f"  - Done {raw_table}. Prepared {created_count} readings."))

        # Import image table into ImageCapture
        for image_table in image_table_names:
            self.stdout.write(self.style.HTTP_INFO(f"Importing image table: {image_table} -> ImageCapture"))
            columns = self._get_sqlite_table_info(src_conn, image_table)
            if not columns:
                self.stdout.write(self.style.WARNING(f"  - Skipping {image_table}: no columns found"))
                continue

            device_col = _pick_device_column(columns)
            ts_col = _pick_timestamp_column(columns)
            file_col = _pick_file_uri_column(columns)
            camera_col = _pick_camera_id_column(columns)

            if not ts_col or not file_col:
                self.stdout.write(
                    self.style.WARNING(
                        f"  - Skipping {image_table}: could not detect timestamp ({ts_col}) or file/uri column ({file_col})"
                    )
                )
                continue

            selectable_cols = [c["name"] for c in columns]
            col_select_sql = ", ".join(_quote_ident(c) for c in selectable_cols)
            sql = f'SELECT rowid, {col_select_sql} FROM {_quote_ident(image_table)}'
            cur = src_conn.cursor()
            cur.execute(sql)

            col_names = [d[0] for d in cur.description]  # rowid + all columns
            created_count = 0
            processed = 0
            to_create = []
            created_device_ext_ids = set()

            while True:
                rows = cur.fetchmany(batch_size)
                if not rows:
                    break
                for row in rows:
                    processed += 1
                    if limit and processed > limit:
                        break
                    row_dict = dict(zip(col_names, row))
                    rowid = row_dict.get("rowid")
                    file_uri = row_dict.get(file_col)
                    captured_at = _parse_datetime(row_dict.get(ts_col))
                    if not file_uri or not captured_at:
                        continue

                    file_uri = _safe_str(file_uri).strip()
                    if not file_uri:
                        continue

                    # Dedup: file_uri is usually stable.
                    if ImageCapture.objects.filter(file_uri=file_uri).exists():
                        continue

                    device_key = _safe_str(row_dict.get(device_col)).strip() if device_col else ""
                    device_obj = None
                    if device_key:
                        device_obj = self._get_device(device_cache, device_key)

                    camera_id = "camera_1"
                    if camera_col and camera_col in row_dict and row_dict.get(camera_col) is not None:
                        camera_id = _safe_str(row_dict.get(camera_col)).strip()[:64] or "camera_1"

                    # Store raw row excerpt for later debugging.
                    image_metadata = {
                        "source_table": image_table,
                        "raw_rowid": rowid,
                    }

                    img = ImageCapture(
                        device=device_obj,
                        camera_id=camera_id,
                        file_uri=file_uri,
                        captured_at=captured_at,
                        image_metadata=image_metadata,
                        created_at=now,
                    )
                    to_create.append(img)
                    created_count += 1
                    if device_key:
                        created_device_ext_ids.add(device_key)

                if limit and processed > limit:
                    break

                if to_create and not dry_run:
                    with transaction.atomic():
                        ImageCapture.objects.bulk_create(to_create, batch_size=batch_size)
                    to_create = []

            if to_create and not dry_run:
                with transaction.atomic():
                    ImageCapture.objects.bulk_create(to_create, batch_size=batch_size)

            if created_device_ext_ids and not dry_run:
                Device.objects.filter(external_id__in=created_device_ext_ids).exclude(
                    status=Device.DeviceStatus.RETIRED
                ).update(
                    status=Device.DeviceStatus.ACTIVE,
                    last_seen_at=now,
                    last_heartbeat_at=now,
                )

            self.stdout.write(self.style.SUCCESS(f"  - Done {image_table}. Prepared {created_count} captures."))

        self.stdout.write(self.style.SUCCESS("Import finished."))

    def _get_sqlite_table_info(self, src_conn, table_name: str):
        cur = src_conn.cursor()
        try:
            cur.execute(f"PRAGMA table_info({_quote_ident(table_name)})")
        except sqlite3.Error:
            return []
        rows = cur.fetchall()
        # PRAGMA columns: cid, name, type, notnull, dflt_value, pk
        out = []
        for r in rows:
            if len(r) < 2:
                continue
            out.append({"name": r[1], "type": r[2] if len(r) > 2 else ""})
        return out

    def _get_device(self, device_cache: dict, device_external_id: str):
        if device_external_id in device_cache:
            return device_cache[device_external_id]

        device = Device.objects.filter(external_id=device_external_id).first()
        device_cache[device_external_id] = device
        return device

