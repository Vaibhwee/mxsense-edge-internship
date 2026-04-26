import json
import logging
from typing import Optional

from django.db import connection

logger = logging.getLogger(__name__)
_logged_connection_success = False

RAW_TELEMETRY_TABLES = [
    "sensor_data",
    "env_data_new",
    "voc_data_new",
    "gas_data_new",
    "pm_data_new",
    "flow_data",
    "force_data",
    "acoustic_data",
    "distance_data",
    "system_data",
    "mcu_monitoring",
    "spectral_data",
    "header_data",
]

TABLE_TO_SENSOR_TYPE = {
    "env_data": "env",
    "env_data_new": "env",
    "voc_data": "voc",
    "voc_data_new": "voc",
    "gas_data": "gas",
    "gas_data_new": "gas",
    "pm_data": "pm",
    "pm_data_new": "pm",
}


def _fetch_all_dicts(sql: str):
    global _logged_connection_success
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            columns = [col[0] for col in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            if not _logged_connection_success:
                _logged_connection_success = True
                db_name = connection.settings_dict.get("NAME", "<unknown>")
                db_host = connection.settings_dict.get("HOST", "<unknown>")
                logger.info("Database connection successful (name=%s host=%s).", db_name, db_host)
            return [dict(zip(columns, row)) for row in rows]
    except Exception as exc:
        logger.error("Database query failed: %s", exc)
        raise


def _fetch_all_dicts_params(sql: str, params):
    global _logged_connection_success
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            columns = [col[0] for col in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            if not _logged_connection_success:
                _logged_connection_success = True
                db_name = connection.settings_dict.get("NAME", "<unknown>")
                db_host = connection.settings_dict.get("HOST", "<unknown>")
                logger.info("Database connection successful (name=%s host=%s).", db_name, db_host)
            return [dict(zip(columns, row)) for row in rows]
    except Exception as exc:
        logger.error("Database query failed: %s", exc)
        raise


def _try_fetch_all_dicts(sql: str):
    try:
        return _fetch_all_dicts(sql)
    except Exception:
        return None


def _try_fetch_all_dicts_params(sql: str, params):
    try:
        return _fetch_all_dicts_params(sql, params)
    except Exception:
        return None


def _quote_ident(name: str) -> str:
    return '"' + str(name).replace('"', '""') + '"'


def _table_exists(table_name: str) -> bool:
    rows = _try_fetch_all_dicts(
        f"""
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema='public' AND table_name='{table_name}'
        LIMIT 1;
        """
    )
    return bool(rows)


def _get_table_columns(table_name: str):
    rows = _try_fetch_all_dicts(
        f"""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema='public' AND table_name='{table_name}'
        ORDER BY ordinal_position;
        """
    )
    return [r["column_name"] for r in (rows or [])]


def _pick_first(columns, candidates):
    cols_lower = {c.lower(): c for c in columns}
    for cand in candidates:
        if cand.lower() in cols_lower:
            return cols_lower[cand.lower()]
    return None


def _pick_device_col(columns):
    return _pick_first(
        columns,
        [
            "device_id",
            "device",
            "external_id",
            "device_code",
            "device_name",
            "node_id",
            "node",
            "source_id",
        ],
    )


def _pick_timestamp_col(columns):
    return _pick_first(
        columns,
        [
            "timestamp",
            "timestamp_utc",
            "source_timestamp",
            "captured_at",
            "recorded_at",
            "created_at",
            "updated_at",
            "time",
            "datetime",
            "ts",
        ],
    )


def _pick_image_col(columns):
    return _pick_first(
        columns,
        [
            "image_url",
            "file_uri",
            "url",
            "uri",
            "image_uri",
            "path",
            "file_path",
        ],
    )


def _normalize_payload(row_dict, skip_cols):
    payload = {}
    for key, value in row_dict.items():
        if key in skip_cols:
            continue
        # Keep simple scalar values only for chart-friendly payloads.
        if isinstance(value, (int, float, str, bool)) or value is None:
            payload[key] = value
    return payload


def _to_iso_timestamp(value):
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _get_device_identities():
    rows = []

    if _table_exists("devices"):
        cols = _get_table_columns("devices") or []
        uid_candidates = [c for c in ("device_uid", "external_id", "device_code", "device_name", "name") if c in cols]
        coalesce_parts = [f"NULLIF({_quote_ident(c)}::text, '')" for c in uid_candidates]
        coalesce_parts.append("id::text")
        uid_expr = "COALESCE(" + ", ".join(coalesce_parts) + ")"
        rows = _try_fetch_all_dicts(
            f"""
            SELECT
                id::text AS device_id,
                {uid_expr} AS device_uid
            FROM devices
            WHERE id IS NOT NULL;
            """
        ) or []

    if not rows and _table_exists("device_manager_device"):
        rows = _try_fetch_all_dicts(
            """
            SELECT
                id::text AS device_id,
                COALESCE(NULLIF(external_id::text, ''), id::text) AS device_uid
            FROM device_manager_device
            WHERE id IS NOT NULL;
            """
        ) or []

    by_id = {}
    by_uid = {}
    for row in rows:
        device_id = str(row.get("device_id") or "").strip()
        device_uid = str(row.get("device_uid") or "").strip()
        if not device_id:
            continue
        if not device_uid:
            device_uid = device_id
        by_id[device_id] = device_uid
        by_uid[device_uid] = device_id
    return by_id, by_uid


def _resolve_device_identity(raw_value, by_id, by_uid):
    value = str(raw_value or "").strip()
    if not value:
        return "", ""

    if value in by_id:
        return value, by_id[value]
    if value in by_uid:
        return by_uid[value], value
    return value, value


def resolve_device_identity(raw_value):
    by_id, by_uid = _get_device_identities()
    return _resolve_device_identity(raw_value, by_id, by_uid)


def _map_telemetry_json_fields(payload):
    if not isinstance(payload, dict):
        return payload

    telemetry_json = payload.get("telemetry_json")
    if not isinstance(telemetry_json, dict):
        return payload

    mapped = dict(payload)
    mapped["soc_temp"] = telemetry_json.get("soc_temp", telemetry_json.get("temperature"))
    mapped["gpu_load"] = telemetry_json.get("gpu_load", telemetry_json.get("gpu"))
    mapped["ram"] = telemetry_json.get("ram", telemetry_json.get("ram_mb"))
    mapped["fan"] = telemetry_json.get("fan", telemetry_json.get("fan_rpm"))
    return mapped


def _coerce_float(value):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _get_latest_system_metrics_map(by_id=None, by_uid=None):
    """Latest per-device system metrics from ``telemetry_data``.

    Returns a dict keyed by both the device UUID and the human ``device_uid`` so
    callers can look up either form. Values contain ``soc_temp``, ``gpu_load``,
    ``ram``, ``fan`` and ``timestamp`` drawn from ``telemetry_json`` / columns.
    """
    if not _table_exists("telemetry_data"):
        return {}

    cols = _get_table_columns("telemetry_data") or []
    if not cols:
        return {}

    has_cpu_temp = "cpu_temp_c" in cols
    has_gpu_load = "gpu_load" in cols
    has_ram_mb = "ram_mb" in cols
    has_fan_rpm = "fan_rpm" in cols
    has_json = "telemetry_json" in cols
    ts_col = "timestamp_utc" if "timestamp_utc" in cols else _pick_timestamp_col(cols)
    if not ts_col:
        return {}

    soc_expr = (
        "COALESCE((t.telemetry_json->>'soc_temp')::double precision, t.cpu_temp_c::double precision)"
        if has_json and has_cpu_temp
        else ("(t.telemetry_json->>'soc_temp')::double precision" if has_json else
              ("t.cpu_temp_c::double precision" if has_cpu_temp else "NULL::double precision"))
    )
    gpu_expr = (
        "COALESCE((t.telemetry_json->>'gpu_load')::double precision, t.gpu_load::double precision)"
        if has_json and has_gpu_load
        else ("(t.telemetry_json->>'gpu_load')::double precision" if has_json else
              ("t.gpu_load::double precision" if has_gpu_load else "NULL::double precision"))
    )
    ram_expr = (
        "COALESCE((t.telemetry_json->>'ram')::double precision, (t.telemetry_json->>'ram_mb')::double precision, t.ram_mb::double precision)"
        if has_json and has_ram_mb
        else ("COALESCE((t.telemetry_json->>'ram')::double precision, (t.telemetry_json->>'ram_mb')::double precision)" if has_json else
              ("t.ram_mb::double precision" if has_ram_mb else "NULL::double precision"))
    )
    fan_expr = (
        "COALESCE((t.telemetry_json->>'fan')::double precision, (t.telemetry_json->>'fan_rpm')::double precision, t.fan_rpm::double precision)"
        if has_json and has_fan_rpm
        else ("COALESCE((t.telemetry_json->>'fan')::double precision, (t.telemetry_json->>'fan_rpm')::double precision)" if has_json else
              ("t.fan_rpm::double precision" if has_fan_rpm else "NULL::double precision"))
    )

    rows = _try_fetch_all_dicts(
        f"""
        SELECT DISTINCT ON (t.device_id)
            t.device_id::text AS device_id,
            {soc_expr} AS soc_temp,
            {gpu_expr} AS gpu_load,
            {ram_expr} AS ram,
            {fan_expr} AS fan,
            t.{_quote_ident(ts_col)} AS timestamp
        FROM telemetry_data t
        WHERE t.device_id IS NOT NULL
        ORDER BY t.device_id, t.{_quote_ident(ts_col)} DESC;
        """
    ) or []

    if not rows:
        return {}

    if by_id is None or by_uid is None:
        by_id, by_uid = _get_device_identities()

    result = {}
    for row in rows:
        raw = str(row.get("device_id") or "").strip()
        if not raw:
            continue
        did, duid = _resolve_device_identity(raw, by_id, by_uid)
        payload = {
            "soc_temp": _coerce_float(row.get("soc_temp")),
            "gpu_load": _coerce_float(row.get("gpu_load")),
            "ram": _coerce_float(row.get("ram")),
            "fan": _coerce_float(row.get("fan")),
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        entry = {
            "timestamp": row.get("timestamp"),
            "payload": payload,
        }
        if did:
            result[did] = entry
        if duid:
            result[duid] = entry
    return result


def _get_latest_device_health_map():
    if not _table_exists("device_health"):
        return {}

    cols = _get_table_columns("device_health")
    device_col = _pick_device_col(cols) or _pick_first(cols, ["device_id"])
    ts_col = _pick_timestamp_col(cols)
    if not device_col:
        return {}

    select_cols = ", ".join(_quote_ident(c) for c in cols)
    order_col = _quote_ident(ts_col) if ts_col else _quote_ident(device_col)
    rows = _try_fetch_all_dicts(
        f"""
        SELECT DISTINCT ON ({_quote_ident(device_col)})
            {select_cols}
        FROM device_health
        WHERE {_quote_ident(device_col)} IS NOT NULL
        ORDER BY {_quote_ident(device_col)}, {order_col} DESC;
        """
    ) or []

    health_map = {}
    for row in rows:
        device_key = str(row.get(device_col) or "").strip()
        if not device_key:
            continue
        payload = _normalize_payload(
            row,
            {
                "id",
                device_col,
                ts_col,
                "created_at",
                "updated_at",
            },
        )
        health_map[device_key] = {
            "timestamp": row.get(ts_col) if ts_col else None,
            "payload": payload,
        }
    return health_map


def get_devices_data():
    by_id, by_uid = _get_device_identities()
    health_map = _get_latest_device_health_map()
    system_map = _get_latest_system_metrics_map(by_id, by_uid)

    def _merge_system_metrics(payload, device_id, device_uid):
        sys_entry = system_map.get(device_uid) or system_map.get(device_id) or {}
        sys_payload = sys_entry.get("payload") or {}
        if not sys_payload:
            return payload or {}
        merged = dict(payload or {})
        merged.update(sys_payload)
        return merged

    def _latest_ts(primary, device_id, device_uid):
        sys_entry = system_map.get(device_uid) or system_map.get(device_id) or {}
        sys_ts = sys_entry.get("timestamp")
        if sys_ts and primary:
            try:
                return sys_ts if sys_ts > primary else primary
            except TypeError:
                return sys_ts
        return sys_ts or primary

    # If we already have canonical devices in device_health, use it as a strict allow-list.
    # This prevents orphan IDs from raw telemetry tables (e.g., test rows) from leaking into UI.
    canonical_device_ids = set(health_map.keys())

    # First choice: explicit devices table (if present).
    rows = _try_fetch_all_dicts("SELECT * FROM devices;")
    if rows is not None and len(rows) > 0:
        normalized = []
        for idx, r in enumerate(rows):
            raw_device_id = r.get("id") or r.get("device_id") or r.get("external_id") or f"raw-{idx+1}"
            device_id, resolved_uid = _resolve_device_identity(raw_device_id, by_id, by_uid)
            device_uid = (
                str(r.get("device_uid") or "").strip()
                or str(r.get("external_id") or "").strip()
                or str(r.get("device_name") or "").strip()
                or resolved_uid
            )
            health = health_map.get(str(device_uid)) or health_map.get(str(device_id)) or {}
            base_ts = (
                health.get("timestamp")
                or r.get("last_seen_at")
                or r.get("timestamp")
                or r.get("created_at")
            )
            normalized.append(
                {
                    "id": str(device_id),
                    "device_id": str(device_id),
                    "device_uid": str(device_uid),
                    "external_id": str(device_uid),
                    "name": str(r.get("name") or device_uid),
                    "location": str(r.get("location") or r.get("site") or "N/A"),
                    "last_seen_at": _latest_ts(base_ts, str(device_id), str(device_uid)),
                    "health_payload": _merge_system_metrics(
                        health.get("payload") or {}, str(device_id), str(device_uid)
                    ),
                }
            )
        return normalized

    # Build device list from available raw telemetry tables.
    device_map = {}
    for table_name in RAW_TELEMETRY_TABLES:
        query = f"""
            SELECT
                device_id::text AS external_id,
                MAX(timestamp) AS last_seen_at
            FROM {_quote_ident(table_name)}
            WHERE device_id IS NOT NULL
            GROUP BY device_id
            LIMIT 500;
        """
        rows = _try_fetch_all_dicts(query) or []
        for r in rows:
            raw_device = str(r.get("external_id") or "").strip()
            if not raw_device:
                continue
            device_id, device_uid = _resolve_device_identity(raw_device, by_id, by_uid)
            if canonical_device_ids and device_uid not in canonical_device_ids and device_id not in canonical_device_ids:
                continue
            prev = device_map.get(device_uid)
            if prev is None:
                health = health_map.get(device_uid) or health_map.get(device_id) or {}
                base_ts = health.get("timestamp") or r.get("last_seen_at")
                device_map[device_uid] = {
                    "id": device_id,
                    "device_id": device_id,
                    "device_uid": device_uid,
                    "external_id": device_uid,
                    "name": device_uid,
                    "location": "N/A",
                    "last_seen_at": _latest_ts(base_ts, device_id, device_uid),
                    "health_payload": _merge_system_metrics(
                        health.get("payload") or {}, device_id, device_uid
                    ),
                }
            else:
                health = health_map.get(device_uid) or health_map.get(device_id) or {}
                if health.get("timestamp"):
                    prev["last_seen_at"] = health.get("timestamp")
                elif r.get("last_seen_at"):
                    prev["last_seen_at"] = r.get("last_seen_at")
                if health.get("payload"):
                    prev["health_payload"] = health.get("payload")
                prev["health_payload"] = _merge_system_metrics(
                    prev.get("health_payload") or {}, device_id, device_uid
                )
                prev["last_seen_at"] = _latest_ts(
                    prev.get("last_seen_at"), device_id, device_uid
                )

    if device_map:
        return list(device_map.values())

    # Fallback to Django-managed table
    rows = _fetch_all_dicts(
        """
        SELECT
            id,
            external_id,
            name,
            device_type,
            location,
            assigned_line,
            status,
            last_seen_at,
            created_at,
            updated_at
        FROM device_manager_device
        ORDER BY created_at DESC;
        """
    )
    for row in rows:
        row["device_id"] = str(row.get("id") or "")
        row["device_uid"] = (
            str(row.get("external_id") or "").strip()
            or str(row.get("name") or "").strip()
            or row["device_id"]
        )
        ext = str(row.get("external_id") or "").strip()
        rid = str(row.get("id") or "").strip()
        health = health_map.get(ext) or health_map.get(rid) or {}
        if health.get("timestamp"):
            row["last_seen_at"] = health.get("timestamp")
        row["health_payload"] = _merge_system_metrics(
            health.get("payload") or {}, rid, ext or row["device_uid"]
        )
        row["last_seen_at"] = _latest_ts(
            row.get("last_seen_at"), rid, ext or row["device_uid"]
        )
    return rows


def get_latest_image_data(device_id: Optional[str] = None):
    """Return the newest image row from the platform DB (raw tables or Django ORM).

    When ``device_id`` is set, results are scoped to that device (external_id, camera_id,
    or a matching device column on raw tables). When omitted, the latest row across all
    devices is returned.
    """
    device_id = (device_id or "").strip() or None

    # Primary raw `images` table (column names vary by deployment)
    if _table_exists("images"):
        cols = _get_table_columns("images")
        image_col = _pick_image_col(cols) or _pick_first(cols, ["image_key"])
        if image_col:
            ts_col = _pick_timestamp_col(cols)
            dev_col = _pick_device_col(cols)
            order_col = _quote_ident(ts_col) if ts_col else _quote_ident(image_col)
            ts_select = f", {_quote_ident(ts_col)} AS timestamp" if ts_col else ""
            base = (
                f"SELECT {_quote_ident(image_col)}::text AS image_url{ts_select} "
                f"FROM images WHERE {_quote_ident(image_col)} IS NOT NULL"
            )
            if device_id and dev_col:
                sql = f"{base} AND {_quote_ident(dev_col)}::text = %s ORDER BY {order_col} DESC LIMIT 1;"
                rows = _try_fetch_all_dicts_params(sql, [device_id])
            elif not device_id:
                sql = f"{base} ORDER BY {order_col} DESC LIMIT 1;"
                rows = _try_fetch_all_dicts(sql)
            else:
                rows = None
            if rows is not None and len(rows) > 0:
                return rows[0]

    # Raw image_metadata with dynamic column selection.
    if _table_exists("image_metadata"):
        cols = _get_table_columns("image_metadata")
        image_col = _pick_image_col(cols)
        ts_col = _pick_timestamp_col(cols)
        dev_col = _pick_device_col(cols)
        if image_col:
            order_col = _quote_ident(ts_col) if ts_col else _quote_ident(image_col)
            ts_select = f", {_quote_ident(ts_col)} AS timestamp" if ts_col else ""
            null_img = f"{_quote_ident(image_col)} IS NOT NULL"
            if device_id and dev_col:
                sql = f"""
                SELECT
                    {_quote_ident(image_col)}::text AS image_url{ts_select}
                FROM image_metadata
                WHERE {null_img} AND {_quote_ident(dev_col)}::text = %s
                ORDER BY {order_col} DESC
                LIMIT 1;
                """
                rows = _try_fetch_all_dicts_params(sql, [device_id])
            elif not device_id:
                sql = f"""
                SELECT
                    {_quote_ident(image_col)}::text AS image_url{ts_select}
                FROM image_metadata
                WHERE {null_img}
                ORDER BY {order_col} DESC
                LIMIT 1;
                """
                rows = _try_fetch_all_dicts(sql)
            else:
                rows = None
            if rows is not None and len(rows) > 0:
                return rows[0]

    # Django-managed captures (join device for external_id match)
    try:
        if device_id:
            rows = _fetch_all_dicts_params(
                """
                SELECT
                    ic.file_uri AS image_url,
                    ic.captured_at AS timestamp
                FROM data_ingestion_imagecapture ic
                LEFT JOIN device_manager_device d ON ic.device_id = d.id
                WHERE d.external_id = %s OR ic.camera_id = %s
                ORDER BY ic.captured_at DESC
                LIMIT 1;
                """,
                [device_id, device_id],
            )
        else:
            rows = _fetch_all_dicts(
                """
                SELECT
                    file_uri AS image_url,
                    captured_at AS timestamp
                FROM data_ingestion_imagecapture
                ORDER BY captured_at DESC
                LIMIT 1;
                """
            )
    except Exception:
        rows = []
    return rows[0] if rows else {}


def get_telemetry_data():
    by_id, by_uid = _get_device_identities()
    # Prefer normalized telemetry_data when available (DB-managed timestamps).
    if _table_exists("telemetry_data"):
        tcols = _get_table_columns("telemetry_data") or []
        ts_field = "timestamp_utc" if "timestamp_utc" in tcols else _pick_timestamp_col(tcols)
        has_json = "telemetry_json" in tcols
        has_cpu = "cpu_temp_c" in tcols
        if ts_field:
            telemetry_rows = _try_fetch_all_dicts(
                f"""
                SELECT
                    t.id::text AS id,
                    t.device_id::text AS device_id,
                    'system' AS sensor_type,
                    {"t.telemetry_json" if has_json else "NULL::jsonb"} AS telemetry_json,
                    {"t.cpu_temp_c::double precision" if has_cpu else "NULL::double precision"} AS cpu_temp_c,
                    t.{_quote_ident(ts_field)} AS source_timestamp,
                    t.{_quote_ident(ts_field)} AS created_at
                FROM telemetry_data t
                ORDER BY t.{_quote_ident(ts_field)} DESC
                LIMIT 500;
                """
            )
            if telemetry_rows is not None and len(telemetry_rows) > 0:
                for row in telemetry_rows:
                    raw_json = row.pop("telemetry_json", None)
                    if isinstance(raw_json, str):
                        try:
                            raw_json = json.loads(raw_json)
                        except (TypeError, ValueError):
                            raw_json = {}
                    if not isinstance(raw_json, dict):
                        raw_json = {}
                    cpu_temp = row.pop("cpu_temp_c", None)
                    payload = dict(raw_json)
                    if payload.get("soc_temp") is None and cpu_temp is not None:
                        payload["soc_temp"] = cpu_temp
                    for bk in ("ram_mb", "fan_rpm"):
                        if bk in payload and payload.get(bk.split("_")[0]) is None:
                            payload[bk.split("_")[0]] = payload[bk]
                    payload = {k: v for k, v in payload.items() if v is not None}
                    row["payload"] = payload
                    did, duid = _resolve_device_identity(row.get("device_id"), by_id, by_uid)
                    row["device_id"] = did
                    row["device_uid"] = duid
                    row["device"] = duid
                return telemetry_rows

    # Primary raw table (requested)
    rows = _try_fetch_all_dicts("SELECT * FROM telemetry;")
    if rows is not None and len(rows) > 0:
        for row in rows:
            raw_device = row.get("device_id") or row.get("device")
            device_id, device_uid = _resolve_device_identity(raw_device, by_id, by_uid)
            row["device_id"] = device_id
            row["device_uid"] = device_uid
            if "device" not in row:
                row["device"] = device_uid
        return rows

    # Normalize raw table family into frontend-friendly schema.
    normalized = []
    for table_name in RAW_TELEMETRY_TABLES:
        rows = _try_fetch_all_dicts(
            f"""
            SELECT
                id::text AS row_id,
                device_id::text AS device,
                timestamp AS source_timestamp,
                (to_jsonb(t) - 'id' - 'device_id' - 'timestamp') AS payload
            FROM {_quote_ident(table_name)} t
            WHERE device_id IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT 500;
            """
        ) or []

        sensor_type = TABLE_TO_SENSOR_TYPE.get(table_name, table_name.replace("_data", ""))
        for row in rows:
            device_id, device_uid = _resolve_device_identity(row.get("device"), by_id, by_uid)
            payload = _map_telemetry_json_fields(row.get("payload") or {})
            normalized.append(
                {
                    "id": f"{table_name}:{row.get('row_id') or len(normalized)+1}",
                    "device": device_uid,
                    "device_id": device_id,
                    "device_uid": device_uid,
                    "sensor_type": sensor_type,
                    "payload": payload,
                    "source_timestamp": row.get("source_timestamp"),
                    "created_at": row.get("source_timestamp"),
                }
            )

    if normalized:
        return normalized

    # Fallback to Django-managed table
    rows = _fetch_all_dicts(
        """
        SELECT
            r.id,
            r.device_id::text AS device_id,
            COALESCE(NULLIF(d.external_id::text, ''), r.device_id::text) AS device_uid,
            COALESCE(NULLIF(d.external_id::text, ''), r.device_id::text) AS device,
            r.sensor_type,
            r.payload,
            r.source_timestamp,
            r.created_at
        FROM data_ingestion_sensorreading r
        LEFT JOIN device_manager_device d ON r.device_id = d.id
        ORDER BY created_at DESC;
        """
    )
    for row in rows:
        row["payload"] = _map_telemetry_json_fields(row.get("payload") or {})
    return rows


def get_locations_data():
    by_id, by_uid = _get_device_identities()
    # Primary raw table (requested)
    rows = _try_fetch_all_dicts(
        """
        SELECT
            id::text AS device_id,
            COALESCE(NULLIF(device_uid::text, ''), NULLIF(external_id::text, ''), id::text) AS device_uid,
            lat,
            lng
        FROM devices;
        """
    )
    if rows is not None and len(rows) > 0:
        return rows

    # Try to infer from any raw table with lat/lng columns.
    for table_name in ["sensor_data", "header_data", "system_data"]:
        if not _table_exists(table_name):
            continue
        cols = _get_table_columns(table_name)
        device_col = _pick_device_col(cols)
        lat_col = _pick_first(cols, ["lat", "latitude"])
        lng_col = _pick_first(cols, ["lng", "longitude", "lon"])
        if not (device_col and lat_col and lng_col):
            continue
        rows = _try_fetch_all_dicts(
            f"""
            SELECT
                {_quote_ident(device_col)}::text AS device_id,
                {_quote_ident(lat_col)} AS lat,
                {_quote_ident(lng_col)} AS lng
            FROM {_quote_ident(table_name)}
            WHERE {_quote_ident(device_col)} IS NOT NULL
            LIMIT 1000;
            """
        )
        if rows is not None and len(rows) > 0:
            for row in rows:
                _, device_uid = _resolve_device_identity(row.get("device_id"), by_id, by_uid)
                row["device_uid"] = device_uid
            return rows

    # Fallback to Django-managed device + site tables
    return _fetch_all_dicts(
        """
        SELECT
            d.id::text AS device_id,
            COALESCE(NULLIF(d.external_id::text, ''), d.id::text) AS device_uid,
            s.latitude AS lat,
            s.longitude AS lng
        FROM device_manager_device d
        LEFT JOIN device_manager_site s ON d.site_id = s.id;
        """
    )


SECTION_TABLE_CONFIG = {
    "ENV": {
        "table": "env_data_new",
        "fields": [
            "sht45_temperature",
            "sht45_humidity",
            "bme688_temperature",
            "bme688_humidity",
            "bme688_pressure",
        ],
    },
    "GAS": {
        "table": "gas_data_new",
        "fields": [
            "ethylene_sensor_value",
            "mq135_air_quality",
            "mq136_sulfur_level",
            "tgs2600_contamination",
        ],
    },
    "PM": {
        "table": "pm_data_new",
        # pm_data columns vary by sensor/ingestion version.
        # Include the common PMS7003 + SPS30 column names (and keep generic aliases as fallback).
        "fields": [
            "pms7003_pm1",
            "pms7003_pm2_5",
            "pms7003_pm10",
            "sps30_pm1",
            "sps30_pm2_5",
            "sps30_pm10",
            "pm1",
            "pm25",
            "pm10",
            "particle_count",
        ],
    },
    "VOC": {
        "table": "voc_data_new",
        "fields": [
            "sgp41_voc_index",
            "sgp41_nox_index",
            "zmod4410_voc_concentration",
            "bme688_gas_resistance",
            "tgs2602_odor_level",
        ],
    },
    "SYSTEM": {
        "table": "system_data",
        "fields": ["soc_temp", "gpu_load", "ram_mb", "fan_rpm"],
    },
    "THERMAL": {
        "table": "sensor_data",
        "fields": ["temperature"],
    },
    "SPECTRAL": {
        "table": "sensor_data",
        "fields": ["spectral"],
    },
    "DISTANCE": {
        "table": "sensor_data",
        "fields": ["distance"],
    },
}

SECTION_SENSOR_CODE_PREFIX = {
    "ENV": "CH0",
    "VOC": "CH1",
    "GAS": "CH2",
    "PM": "CH4",
    "THERMAL": "CH5",
    "SPECTRAL": "CH6",
    "DISTANCE": "CH8",
}

SECTION_JSON_METRIC_MAP = {
    "ENV": {
        "temperature": ["temperature_c", "temperature"],
        "humidity": ["humidity_pct", "humidity"],
    },
    "VOC": {
        "voc": ["voc_index", "voc"],
    },
    "GAS": {
        "value": ["value", "gas_ppm", "gas"],
    },
    "PM": {
        "pm1": ["pm1_0", "pm1"],
        "pm25": ["pm2_5", "pm25", "pm2.5"],
        "pm10": ["pm10_0", "pm10"],
    },
    "THERMAL": {
        "temperature": ["temperature_c", "temperature"],
    },
}


def get_section_timeseries(section: str, device_id: str, limit: int = 20):
    section_key = str(section or "").upper().strip()
    config = SECTION_TABLE_CONFIG.get(section_key)
    sensor_prefix = SECTION_SENSOR_CODE_PREFIX.get(section_key)
    if not config:
        raise ValueError(f"Unsupported section '{section}'.")
    if not device_id:
        raise ValueError("device_id is required.")

    table_name = config["table"]
    if not _table_exists(table_name):
        if section_key != "SYSTEM" and not sensor_prefix:
            return []
        table_name = None

    if table_name:
        cols = _get_table_columns(table_name)
        device_col = _pick_device_col(cols)
        ts_col = _pick_timestamp_col(cols)
        if not device_col or not ts_col:
            table_name = None
    else:
        cols = []
        device_col = None
        ts_col = None

    safe_limit = max(1, min(int(limit or 20), 200))

    resolved_device_id, resolved_device_uid = resolve_device_identity(device_id)
    candidate_values = list(
        dict.fromkeys(
            [
                str(device_id or "").strip(),
                str(resolved_device_id or "").strip(),
                str(resolved_device_uid or "").strip(),
            ]
        )
    )
    candidate_values = [value for value in candidate_values if value]

    placeholders = ", ".join(["%s"] * len(candidate_values))

    # GAS must come from raw_sensor_data joined with sensors.
    # Do not use legacy gas_data tables for this section.
    if section_key == "GAS":
        if not candidate_values:
            return []
        if not _table_exists("raw_sensor_data") or not _table_exists("sensors"):
            logger.info(
                "[GAS] Skipping query because required tables are missing (raw_sensor_data/sensors)."
            )
            return []

        raw_cols = _get_table_columns("raw_sensor_data") or []
        sensor_cols = _get_table_columns("sensors") or []
        required_raw = {"sensor_id", "device_id", "timestamp_utc", "raw_value_json"}
        required_sensor = {"id", "sensor_code"}
        if not required_raw.issubset(set(raw_cols)) or not required_sensor.issubset(set(sensor_cols)):
            logger.info("[GAS] Required columns missing in raw_sensor_data/sensors.")
            return []

        safe_limit = max(1, min(int(limit or 1000), 1000))
        device_placeholders = ", ".join(["%s"] * len(candidate_values))

        has_sensor_name = "sensor_name" in sensor_cols
        has_confidence_in_json = True  # JSON lookup is safe even if key missing

        # Dynamic filtering: pull all sensors whose sensor_code starts with the gas
        # channel prefix OR whose code/name contains a known gas-sensor family.
        # This avoids hardcoding sensor codes.
        gas_code_prefix = SECTION_SENSOR_CODE_PREFIX.get("GAS", "CH2")
        sensor_filter_sql = "(s.sensor_code ILIKE %s"
        sensor_filter_params = [f"{gas_code_prefix}%"]
        gas_keywords = ["gas", "tgs", "bme", "sgp", "mq", "zmod", "ze07", "me3"]
        for kw in gas_keywords:
            sensor_filter_sql += " OR s.sensor_code ILIKE %s"
            sensor_filter_params.append(f"%{kw}%")
            if has_sensor_name:
                sensor_filter_sql += " OR s.sensor_name ILIKE %s"
                sensor_filter_params.append(f"%{kw}%")
        sensor_filter_sql += ")"

        sensor_name_select = "s.sensor_name AS sensor_name," if has_sensor_name else "NULL::text AS sensor_name,"

        gas_sql = f"""
            SELECT
                rsd.timestamp_utc AS timestamp,
                s.sensor_code AS sensor_code,
                {sensor_name_select}
                COALESCE(
                    NULLIF(rsd.raw_value_json->>'gas_ppm', '')::double precision,
                    NULLIF(rsd.raw_value_json->>'voc_index', '')::double precision,
                    NULLIF(rsd.raw_value_json->>'value', '')::double precision,
                    NULLIF(rsd.raw_value_json->>'gas', '')::double precision,
                    NULLIF(rsd.raw_value_json->>'ppm', '')::double precision,
                    NULLIF(rsd.raw_value_json->>'concentration', '')::double precision
                ) AS value,
                NULLIF(rsd.raw_value_json->>'confidence', '')::double precision AS confidence
            FROM raw_sensor_data rsd
            JOIN sensors s ON rsd.sensor_id = s.id
            WHERE TRIM(rsd.device_id::text) IN ({device_placeholders})
              AND {sensor_filter_sql}
            ORDER BY rsd.timestamp_utc ASC
            LIMIT %s;
        """
        gas_rows = _try_fetch_all_dicts_params(
            gas_sql,
            [*candidate_values, *sensor_filter_params, safe_limit],
        ) or []
        logger.info(
            "[GAS] Query executed for device_input=%s resolved_id=%s resolved_uid=%s raw_rows=%s",
            str(device_id or "").strip(),
            str(resolved_device_id or "").strip(),
            str(resolved_device_uid or "").strip(),
            len(gas_rows),
        )
        result = []
        for row in gas_rows:
            ts = row.get("timestamp")
            value = _coerce_float(row.get("value"))
            if ts is None or value is None:
                continue
            item = {
                "timestamp": _to_iso_timestamp(ts),
                "sensor_code": row.get("sensor_code"),
                "value": value,
            }
            sensor_name = row.get("sensor_name")
            if sensor_name:
                item["sensor_name"] = sensor_name
            confidence = _coerce_float(row.get("confidence"))
            if confidence is not None:
                item["confidence"] = confidence
            result.append(item)
        logger.info("[GAS] Returning %s rows after value filtering.", len(result))
        return result

    rows = []
    selected_fields = []

    # Non-system sections: prefer unified sensor stream by sensor_code prefix + raw JSON.
    if section_key != "SYSTEM" and sensor_prefix:
        metric_map = SECTION_JSON_METRIC_MAP.get(section_key, {})
        # Primary path: raw_sensor_data with explicit device_uid -> device_id mapping.
        if metric_map and _table_exists("raw_sensor_data"):
            raw_cols = _get_table_columns("raw_sensor_data") or []
            has_required_raw = all(c in raw_cols for c in ("device_id", "sensor_id", "raw_value_json", "timestamp_utc"))
            if has_required_raw:
                selected_fields = list(metric_map.keys())
                sensor_table = None
                for candidate_sensor_table in ("sensors", "data_ingestion_sensor"):
                    if _table_exists(candidate_sensor_table):
                        sensor_cols = _get_table_columns(candidate_sensor_table) or []
                        if "id" in sensor_cols and "sensor_code" in sensor_cols:
                            sensor_table = candidate_sensor_table
                            break
                if not sensor_table:
                    sensor_table = "sensors"

                metric_sql_parts = []
                for alias, json_key in metric_map.items():
                    keys = json_key if isinstance(json_key, list) else [json_key]
                    key_exprs = [f"NULLIF(rs.raw_value_json->>'{k}', '')::double precision" for k in keys]
                    metric_sql_parts.append(
                        f"COALESCE({', '.join(key_exprs)}) AS {_quote_ident(alias)}"
                    )
                metric_sql = ", ".join(metric_sql_parts)
                if _table_exists("devices"):
                    dev_cols = _get_table_columns("devices") or []
                    uid_candidates = [
                        c for c in ("device_uid", "external_id", "device_code", "device_name", "name") if c in dev_cols
                    ]
                    uid_parts = [f"NULLIF(d.{_quote_ident(c)}::text, '')" for c in uid_candidates]
                    uid_parts.append("d.id::text")
                    uid_expr = "COALESCE(" + ", ".join(uid_parts) + ")"
                    sql = f"""
                        SELECT *
                        FROM (
                            SELECT
                                rs.timestamp_utc AS timestamp,
                                s.sensor_code AS sensor_code,
                                {metric_sql}
                            FROM raw_sensor_data rs
                            JOIN {_quote_ident(sensor_table)} s ON rs.sensor_id = s.id
                            JOIN devices d ON rs.device_id = d.id
                            WHERE (
                                {uid_expr} = %s
                                OR d.id::text = %s
                                OR rs.device_id::text = %s
                            )
                              AND s.sensor_code LIKE %s
                            ORDER BY rs.timestamp_utc DESC
                            LIMIT %s
                        ) recent
                        ORDER BY timestamp ASC;
                    """
                    rows = _try_fetch_all_dicts_params(
                        sql,
                        [
                            str(resolved_device_uid or device_id or "").strip(),
                            str(resolved_device_id or "").strip(),
                            str(resolved_device_id or device_id or "").strip(),
                            f"{sensor_prefix}%",
                            safe_limit,
                        ],
                    ) or []
                else:
                    sql = f"""
                        SELECT *
                        FROM (
                            SELECT
                                rs.timestamp_utc AS timestamp,
                                s.sensor_code AS sensor_code,
                                {metric_sql}
                            FROM raw_sensor_data rs
                            JOIN {_quote_ident(sensor_table)} s ON rs.sensor_id = s.id
                            WHERE rs.device_id::text = %s
                              AND s.sensor_code LIKE %s
                            ORDER BY rs.timestamp_utc DESC
                            LIMIT %s
                        ) recent
                        ORDER BY timestamp ASC;
                    """
                    rows = _try_fetch_all_dicts_params(
                        sql,
                        [
                            str(resolved_device_id or device_id or "").strip(),
                            f"{sensor_prefix}%",
                            safe_limit,
                        ],
                    ) or []

        sensor_source = None
        for candidate_table in ("sensor_data", "telemetry_data"):
            if not _table_exists(candidate_table):
                continue
            candidate_cols = _get_table_columns(candidate_table) or []
            if "raw_value_json" not in candidate_cols or "sensor_code" not in candidate_cols:
                continue
            candidate_ts = "timestamp_utc" if "timestamp_utc" in candidate_cols else _pick_timestamp_col(candidate_cols)
            candidate_dev = _pick_device_col(candidate_cols)
            if candidate_ts and candidate_dev:
                sensor_source = (candidate_table, candidate_dev, candidate_ts)
                break

        if not rows and sensor_source and metric_map:
            sensor_table, sensor_device_col, sensor_ts_col = sensor_source
            selected_fields = list(metric_map.keys())
            metric_sql_parts = []
            for alias, json_key in metric_map.items():
                keys = json_key if isinstance(json_key, list) else [json_key]
                key_exprs = [f"NULLIF(t.raw_value_json->>'{k}', '')::double precision" for k in keys]
                metric_sql_parts.append(
                    f"COALESCE({', '.join(key_exprs)}) AS {_quote_ident(alias)}"
                )
            metric_sql = ", ".join(metric_sql_parts)
            prefix_param = f"{sensor_prefix}%"
            sql = f"""
                SELECT *
                FROM (
                    SELECT
                        t.{_quote_ident(sensor_ts_col)} AS timestamp,
                        t.sensor_code AS sensor_code,
                        {metric_sql}
                    FROM {_quote_ident(sensor_table)} t
                    WHERE TRIM(t.{_quote_ident(sensor_device_col)}::text) IN ({placeholders})
                      AND t.sensor_code LIKE %s
                    ORDER BY t.{_quote_ident(sensor_ts_col)} DESC
                    LIMIT %s
                ) recent
                ORDER BY timestamp ASC;
            """
            rows = _try_fetch_all_dicts_params(
                sql,
                [*candidate_values, prefix_param, safe_limit],
            ) or []

        # Fallback: Django ingestion tables (sensor code on joined sensor table).
        json_expr = None
        if not rows and metric_map and _table_exists("data_ingestion_sensorreading") and _table_exists("data_ingestion_sensor"):
            reading_cols = _get_table_columns("data_ingestion_sensorreading") or []
            has_raw_json = "raw_value_json" in reading_cols
            has_payload = "payload" in reading_cols
            if has_raw_json or has_payload:
                json_expr = (
                    "COALESCE(r.raw_value_json, r.payload)"
                    if has_raw_json and has_payload
                    else ("r.raw_value_json" if has_raw_json else "r.payload")
                )
                selected_fields = list(metric_map.keys())
                metric_sql_parts = []
                for alias, json_key in metric_map.items():
                    keys = json_key if isinstance(json_key, list) else [json_key]
                    key_exprs = [f"NULLIF(({json_expr})->>'{k}', '')::double precision" for k in keys]
                    metric_sql_parts.append(
                        f"COALESCE({', '.join(key_exprs)}) AS {_quote_ident(alias)}"
                    )
                metric_sql = ", ".join(metric_sql_parts)
                sql = f"""
                    SELECT *
                    FROM (
                        SELECT
                            COALESCE(r.source_timestamp, r.created_at) AS timestamp,
                            s.sensor_code AS sensor_code,
                            {metric_sql}
                        FROM data_ingestion_sensorreading r
                        LEFT JOIN data_ingestion_sensor s ON r.sensor_id = s.id
                        WHERE TRIM(r.device_id::text) IN ({placeholders})
                          AND s.sensor_code LIKE %s
                        ORDER BY COALESCE(r.source_timestamp, r.created_at) DESC
                        LIMIT %s
                    ) recent
                    ORDER BY timestamp ASC;
                """
                rows = _try_fetch_all_dicts_params(
                    sql,
                    [*candidate_values, f"{sensor_prefix}%", safe_limit],
                ) or []

    if table_name and not rows:
        # Keep only columns that actually exist in the target table.
        raw_fields = config.get("fields", [])
        selected_fields = [field for field in raw_fields if field in cols]

        select_fields_sql = ", ".join(
            f"{_quote_ident(field)} AS {_quote_ident(field)}" for field in selected_fields
        )
        select_fields_clause = f", {select_fields_sql}" if select_fields_sql else ""

        sql = f"""
            SELECT *
            FROM (
                SELECT
                    {_quote_ident(ts_col)} AS timestamp
                    {select_fields_clause}
                FROM {_quote_ident(table_name)}
                WHERE TRIM({_quote_ident(device_col)}::text) IN ({placeholders})
                ORDER BY {_quote_ident(ts_col)} DESC
                LIMIT %s
            ) recent
            ORDER BY timestamp ASC;
        """
        rows = _fetch_all_dicts_params(sql, [*candidate_values, safe_limit])

    # SYSTEM fallback: use telemetry_data with DB timestamp_utc when section tables are empty/missing.
    if section_key == "SYSTEM" and not rows and _table_exists("telemetry_data"):
        tcols = _get_table_columns("telemetry_data") or []
        ts_field = "timestamp_utc" if "timestamp_utc" in tcols else _pick_timestamp_col(tcols)
        has_json = "telemetry_json" in tcols
        has_cpu = "cpu_temp_c" in tcols
        has_gpu_col = "gpu_load" in tcols
        has_ram_col = "ram_mb" in tcols
        has_fan_col = "fan_rpm" in tcols

        soc_expr = "COALESCE(" + ", ".join(
            x for x in [
                "(t.telemetry_json->>'soc_temp')::double precision" if has_json else None,
                "t.cpu_temp_c::double precision" if has_cpu else None,
            ] if x
        ) + ")" if (has_json or has_cpu) else "NULL::double precision"
        gpu_expr = "COALESCE(" + ", ".join(
            x for x in [
                "(t.telemetry_json->>'gpu_load')::double precision" if has_json else None,
                "t.gpu_load::double precision" if has_gpu_col else None,
            ] if x
        ) + ")" if (has_json or has_gpu_col) else "NULL::double precision"
        ram_expr = "COALESCE(" + ", ".join(
            x for x in [
                "(t.telemetry_json->>'ram')::double precision" if has_json else None,
                "(t.telemetry_json->>'ram_mb')::double precision" if has_json else None,
                "t.ram_mb::double precision" if has_ram_col else None,
            ] if x
        ) + ")" if (has_json or has_ram_col) else "NULL::double precision"
        fan_expr = "COALESCE(" + ", ".join(
            x for x in [
                "(t.telemetry_json->>'fan')::double precision" if has_json else None,
                "(t.telemetry_json->>'fan_rpm')::double precision" if has_json else None,
                "t.fan_rpm::double precision" if has_fan_col else None,
            ] if x
        ) + ")" if (has_json or has_fan_col) else "NULL::double precision"

        if ts_field:
            telemetry_sql = f"""
                SELECT *
                FROM (
                    SELECT
                        t.{_quote_ident(ts_field)} AS timestamp,
                        {soc_expr} AS soc_temp,
                        {gpu_expr} AS gpu_load,
                        {ram_expr} AS ram_mb,
                        {fan_expr} AS fan_rpm
                    FROM telemetry_data t
                    WHERE TRIM(t.device_id::text) IN ({placeholders})
                    ORDER BY t.{_quote_ident(ts_field)} DESC
                    LIMIT %s
                ) recent
                ORDER BY timestamp ASC;
            """
            rows = _try_fetch_all_dicts_params(
                telemetry_sql,
                [*candidate_values, safe_limit],
            ) or []
            selected_fields = ["soc_temp", "gpu_load", "ram_mb", "fan_rpm"]

    structured = []
    for row in rows:
        item = {"timestamp": _to_iso_timestamp(row.get("timestamp"))}
        if row.get("sensor_code") is not None:
            item["sensor_code"] = row.get("sensor_code")
        for field in selected_fields:
            item[field] = row.get(field)
        structured.append(item)
    return structured

