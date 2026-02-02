import xml.etree.ElementTree as ET
import psycopg2
import uuid

# ---------------- DB CONFIG ----------------
DB_CONFIG = {
    "dbname": "trafficdb",
    "user": "postgres",
    "password": "root",
    "host": "localhost",
    "port": 5432
}

# ---------------- UTILS ----------------
def strip_ns(tag):
    """Remove XML namespace"""
    return tag.split("}")[-1]

def is_valid_uuid(value):
    try:
        uuid.UUID(value)
        return True
    except Exception:
        return False

# ---------------- MAIN ----------------
def insert_traffic_data(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # -------- Iterate over ALL RW nodes --------
    for elem in root.iter():
        if strip_ns(elem.tag) != "RW":
            continue

        mid = elem.attrib.get("mid")

        # ❌ Skip non-UUID RW (TrafficPatterns etc.)
        if not mid or not is_valid_uuid(mid):
            continue

        # -------- traffic_message --------
        cur.execute(
            """
            INSERT INTO traffic_message
            (message_id, location_id, road_name, published_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (message_id) DO NOTHING
            RETURNING id
            """,
            (
                mid,
                elem.attrib.get("LI"),
                elem.attrib.get("DE"),
                elem.attrib.get("PBT")
            )
        )

        row = cur.fetchone()
        if row:
            traffic_message_id = row[0]
        else:
            cur.execute(
                "SELECT id FROM traffic_message WHERE message_id = %s",
                (mid,)
            )
            traffic_message_id = cur.fetchone()[0]

        # -------- FIS --------
        for child in elem:
            if strip_ns(child.tag) != "FIS":
                continue

            # -------- FI --------
            for fi in child:
                if strip_ns(fi.tag) != "FI":
                    continue

                tmc = None
                openlr = None
                cf = None

                for fi_child in fi:
                    tag = strip_ns(fi_child.tag)
                    if tag == "TMC":
                        tmc = fi_child
                    elif tag == "TPEGOpenLRBase64":
                        openlr = fi_child.text
                    elif tag == "CF":
                        cf = fi_child

                if tmc is None or cf is None:
                    continue

                # -------- road_segment --------
                cur.execute(
                    """
                    INSERT INTO road_segment
                    (message_id, tmc_place_code, road_name, direction, length_km, openlr_base64)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        traffic_message_id,
                        tmc.attrib.get("PC"),
                        tmc.attrib.get("DE"),
                        tmc.attrib.get("QD"),
                        float(tmc.attrib.get("LE")),
                        openlr
                    )
                )
                road_segment_id = cur.fetchone()[0]

                # -------- traffic_flow --------
                cur.execute(
                    """
                    INSERT INTO traffic_flow
                    (segment_id, flow_type, speed, speed_uncapped,
                     free_flow_speed, jam_factor, confidence, traffic_state)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        road_segment_id,
                        cf.attrib.get("TY"),
                        float(cf.attrib.get("SP")),
                        float(cf.attrib.get("SU")),
                        float(cf.attrib.get("FF")),
                        float(cf.attrib.get("JF")),
                        float(cf.attrib.get("CN")),
                        cf.attrib.get("TS")
                    )
                )
                traffic_flow_id = cur.fetchone()[0]

                # -------- traffic_sub_segment --------
                for cf_child in cf:
                    if strip_ns(cf_child.tag) != "SSS":
                        continue

                    for ss in cf_child:
                        if strip_ns(ss.tag) != "SS":
                            continue

                        cur.execute(
                            """
                            INSERT INTO traffic_sub_segment
                            (traffic_flow_id, length_km, speed, speed_uncapped,
                             free_flow_speed, jam_factor, traffic_state)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """,
                            (
                                traffic_flow_id,
                                float(ss.attrib.get("LE")),
                                float(ss.attrib.get("SP")),
                                float(ss.attrib.get("SU")),
                                float(ss.attrib.get("FF")),
                                float(ss.attrib.get("JF")),
                                ss.attrib.get("TS")
                            )
                        )

    conn.commit()
    cur.close()
    conn.close()
    print("✅ TrafficML XML stored successfully")

# ---------------- RUN ----------------
if __name__ == "__main__":
    insert_traffic_data("test.xml")
