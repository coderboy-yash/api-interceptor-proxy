import psycopg2
from lxml import etree
from shapely.geometry import LineString
from datetime import datetime

# ==========================
# CONFIG
# ==========================
XML_FILE = "traffic.xml"

DB_CONFIG = {
    "dbname": "traffic",
    "user": "postgres",
    "password": "root",
    "host": "localhost",
    "port": 5432
}

# ==========================
# CONNECT
# ==========================
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# ==========================
# PARSE XML (NAMESPACE SAFE)
# ==========================
tree = etree.parse(XML_FILE)
root = tree.getroot()

NS = {"t": root.nsmap[None]}  # DEFAULT namespace

print("ROOT:", root.tag)

# ==========================
# INSERT FEED
# ==========================
cur.execute("""
INSERT INTO traffic_feed
(map_version, map_dvn, tmc_table_version, created_timestamp, schema_version, units)
VALUES (%s,%s,%s,%s,%s,%s)
RETURNING feed_id
""", (
    root.get("MAP_VERSION"),
    root.get("MAP_DVN"),
    root.get("TMC_TABLE_VERSION"),
    root.get("CREATED_TIMESTAMP"),
    root.get("VERSION"),
    root.get("UNITS")
))
feed_id = cur.fetchone()[0]
print("FEED INSERTED:", feed_id)

# ==========================
# WALK TREE
# ==========================
fi_count = 0

for rws in root.findall(".//t:RWS", namespaces=NS):
    cur.execute("""
    INSERT INTO rws
    (feed_id, type, map_dvn, ebu_country_code, extended_country_code, table_id)
    VALUES (%s,%s,%s,%s,%s,%s)
    RETURNING rws_id
    """, (
        feed_id,
        rws.get("TY"),
        rws.get("MAP_DVN"),
        rws.get("EBU_COUNTRY_CODE"),
        rws.get("EXTENDED_COUNTRY_CODE"),
        rws.get("TABLE_ID")
    ))
    rws_id = cur.fetchone()[0]

    for rw in rws.findall("t:RW", namespaces=NS):

        # ---- PBT FIX (timestamp-safe) ----
        pbt_raw = rw.get("PBT")
        pbt_val = None
        if pbt_raw:
            pbt_val = datetime.fromisoformat(pbt_raw.replace("Z", "+00:00"))

        cur.execute("""
        INSERT INTO rw
        (rws_id, location_id, description, pbt, mid)
        VALUES (%s,%s,%s,%s,%s)
        RETURNING rw_id
        """, (
            rws_id,
            rw.get("LI"),
            rw.get("DE"),
            pbt_val,
            rw.get("mid")
        ))
        rw_id = cur.fetchone()[0]

        for fi in rw.findall(".//t:FI", namespaces=NS):
            fi_count += 1

            has_tmc = fi.find("t:TMC", namespaces=NS) is not None
            has_shp = fi.find("t:SHP", namespaces=NS) is not None
            has_openlr = fi.find("t:TPEGOpenLRBase64", namespaces=NS) is not None

            cur.execute("""
            INSERT INTO fi
            (rw_id, has_tmc, has_shp, has_openlr)
            VALUES (%s,%s,%s,%s)
            RETURNING fi_id
            """, (rw_id, has_tmc, has_shp, has_openlr))
            fi_id = cur.fetchone()[0]

            # -------- TMC --------
            tmc = fi.find("t:TMC", namespaces=NS)
            if tmc is not None:
                cur.execute("""
                INSERT INTO fi_tmc
                (fi_id, pc, description, queue_dir, length)
                VALUES (%s,%s,%s,%s,%s)
                """, (
                    fi_id,
                    tmc.get("PC"),
                    tmc.get("DE"),
                    tmc.get("QD"),
                    tmc.get("LE")
                ))

            # -------- OpenLR --------
            olr = fi.find("t:TPEGOpenLRBase64", namespaces=NS)
            if olr is not None and olr.text:
                cur.execute("""
                INSERT INTO fi_openlr (fi_id, openlr_base64)
                VALUES (%s,%s)
                """, (fi_id, olr.text.strip()))

            # -------- SHP --------
            shp = fi.find("t:SHP", namespaces=NS)
            if shp is not None:
                coords = []
                for p in shp.findall("t:P", namespaces=NS):
                    lat = float(p.get("LAT"))
                    lon = float(p.get("LON"))
                    coords.append((lon, lat))

                geom_wkt = LineString(coords).wkt if len(coords) >= 2 else None

                cur.execute("""
                INSERT INTO fi_shp
                (fi_id, functional_class, link_id, length, form_of_way, geom)
                VALUES (%s,%s,%s,%s,%s,
                        CASE WHEN %s IS NULL THEN NULL
                             ELSE ST_GeomFromText(%s,4326)
                        END)
                """, (
                    fi_id,
                    shp.get("FC"),
                    shp.get("LID"),
                    shp.get("LE"),
                    shp.get("FW"),
                    geom_wkt,
                    geom_wkt
                ))

            # -------- CF --------
            cf = fi.find("t:CF", namespaces=NS)
            cur.execute("""
            INSERT INTO cf
            (fi_id, traffic_type, speed, speed_unfiltered, free_flow,
             jam_factor, confidence, traversability)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING cf_id
            """, (
                fi_id,
                cf.get("TY"),
                cf.get("SP"),
                cf.get("SU"),
                cf.get("FF"),
                cf.get("JF"),
                cf.get("CN"),
                cf.get("TS")
            ))
            cf_id = cur.fetchone()[0]

            # -------- SS --------
            for ss in cf.findall(".//t:SS", namespaces=NS):
                cur.execute("""
                INSERT INTO ss
                (cf_id, length, speed, speed_unfiltered, free_flow,
                 jam_factor, traversability)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                """, (
                    cf_id,
                    ss.get("LE"),
                    ss.get("SP"),
                    ss.get("SU"),
                    ss.get("FF"),
                    ss.get("JF"),
                    ss.get("TS")
                ))

# ==========================
# FINISH
# ==========================
conn.commit()
cur.close()
conn.close()

print("✅ DONE")
print("TOTAL FI INSERTED:", fi_count)
