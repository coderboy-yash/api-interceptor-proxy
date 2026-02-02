# TrafficML → PostGIS Database Design (README)

This document explains the **complete database schema**, **table purposes**, **foreign key relationships**, and **query philosophy** used to store **HERE TrafficML (Flow 3.2.x)** data in **PostgreSQL + PostGIS**.

The design is **normalized, scalable, and production-oriented**, and correctly handles:

* TMC-based roads
* Off-TMC roads (SHP geometry)
* OpenLR (map-independent references)
* Segment-level and sub-segment-level traffic

---

## 1. Design Philosophy

### Core Principle

> **FI (Flow Item) is the atomic unit of traffic.**

Everything — location, geometry, OpenLR, traffic state — is attached to an FI.

### Why normalization is required

TrafficML is **hierarchical and sparse**:

* Not every FI has SHP
* Not every FI has TMC
* Not every CF has SSS/SS

Flattening into a single table would:

* Waste space
* Break when optional elements are missing
* Be impossible to evolve

---

## 2. High-Level Entity Relationship Overview

```
TRAFFIC_FEED
   └── RWS
        └── RW
             └── FI
                  ├── FI_TMC (optional)
                  ├── FI_OPENLR (optional)
                  ├── FI_SHP (optional, PostGIS)
                  └── CF (mandatory)
                       └── SS (optional, many)
```

---

## 3. Table-by-Table Schema

---

### 3.1 `traffic_feed`

**Purpose**
Represents one TrafficML XML file (one snapshot of the feed).

**Cardinality**
One feed → many RWS

```sql
traffic_feed (
  feed_id BIGSERIAL PRIMARY KEY,
  map_version TEXT,
  map_dvn TEXT,
  tmc_table_version TEXT,
  created_timestamp TIMESTAMP,
  schema_version TEXT,
  units TEXT
)
```

---

### 3.2 `rws` (Roadway Segment Set)

**Purpose**
Groups all roadways for a country / TMC table.

**Foreign Keys**

* `feed_id → traffic_feed.feed_id`

```sql
rws (
  rws_id BIGSERIAL PRIMARY KEY,
  feed_id BIGINT REFERENCES traffic_feed(feed_id),
  type TEXT,
  map_dvn TEXT,
  ebu_country_code TEXT,
  extended_country_code TEXT,
  table_id TEXT
)
```

---

### 3.3 `rw` (Roadway)

**Purpose**
Represents a logical road (e.g. a named highway or arterial).

**Foreign Keys**

* `rws_id → rws.rws_id`

```sql
rw (
  rw_id BIGSERIAL PRIMARY KEY,
  rws_id BIGINT REFERENCES rws(rws_id),
  location_id TEXT,
  description TEXT,
  pbt TIMESTAMP,
  mid TEXT
)
```

**Notes**

* `PBT` is stored as `TIMESTAMP` (TrafficML provides ISO-8601 values)

---

### 3.4 `fi` (Flow Item) — **CORE TABLE**

**Purpose**
Represents one continuous road segment with uniform traffic behavior.

**Foreign Keys**

* `rw_id → rw.rw_id`

```sql
fi (
  fi_id BIGSERIAL PRIMARY KEY,
  rw_id BIGINT REFERENCES rw(rw_id),
  has_tmc BOOLEAN,
  has_shp BOOLEAN,
  has_openlr BOOLEAN
)
```

**Notes**

* Every FI has exactly one CF
* Location references (TMC / SHP / OpenLR) are optional

---

### 3.5 `fi_tmc` (TMC Location)

**Purpose**
Stores Traffic Message Channel (TMC) location info.

**Foreign Keys**

* `fi_id → fi.fi_id` (1:1)

```sql
fi_tmc (
  fi_id BIGINT PRIMARY KEY REFERENCES fi(fi_id),
  pc TEXT,
  description TEXT,
  queue_dir CHAR(1),
  length FLOAT
)
```

**Exists only if FI is TMC-based**

---

### 3.6 `fi_openlr` (OpenLR Reference)

**Purpose**
Stores map-independent OpenLR location reference.

**Foreign Keys**

* `fi_id → fi.fi_id` (1:1)

```sql
fi_openlr (
  fi_id BIGINT PRIMARY KEY REFERENCES fi(fi_id),
  openlr_base64 TEXT
)
```

**Notes**

* OpenLR must be decoded before spatial use
* Stored raw for traceability

---

### 3.7 `fi_shp` (Off-TMC Geometry – PostGIS)

**Purpose**
Stores raw geometry for off-TMC roads.

**Foreign Keys**

* `fi_id → fi.fi_id` (1:1)

```sql
fi_shp (
  fi_id BIGINT PRIMARY KEY REFERENCES fi(fi_id),
  functional_class INTEGER,
  link_id TEXT,
  length FLOAT,
  form_of_way TEXT,
  geom GEOMETRY(LineString, 4326)
)
```

**Notes**

* Geometry is optional
* Only present for off-TMC segments

---

### 3.8 `cf` (Current Flow)

**Purpose**
Stores the real-time traffic state for an FI.

**Foreign Keys**

* `fi_id → fi.fi_id`

```sql
cf (
  cf_id BIGSERIAL PRIMARY KEY,
  fi_id BIGINT REFERENCES fi(fi_id),
  traffic_type TEXT,
  speed FLOAT,
  speed_unfiltered FLOAT,
  free_flow FLOAT,
  jam_factor FLOAT,
  confidence FLOAT,
  traversability TEXT
)
```

**Notes**

* Exactly one CF per FI

---

### 3.9 `ss` (Sub-Segment)

**Purpose**
Provides higher-granularity traffic inside an FI.

**Foreign Keys**

* `cf_id → cf.cf_id`

```sql
ss (
  ss_id BIGSERIAL PRIMARY KEY,
  cf_id BIGINT REFERENCES cf(cf_id),
  length FLOAT,
  speed FLOAT,
  speed_unfiltered FLOAT,
  free_flow FLOAT,
  jam_factor FLOAT,
  traversability TEXT
)
```

**Notes**

* Zero to many per CF

---

## 4. Foreign Key Summary

| Child Table | Parent Table | Relationship         |
| ----------- | ------------ | -------------------- |
| rws         | traffic_feed | many → one           |
| rw          | rws          | many → one           |
| fi          | rw           | many → one           |
| fi_tmc      | fi           | one → one (optional) |
| fi_openlr   | fi           | one → one (optional) |
| fi_shp      | fi           | one → one (optional) |
| cf          | fi           | one → one            |
| ss          | cf           | many → one           |

---

## 5. Query Philosophy

### Given OpenLR → Traffic

```
fi_openlr → fi → cf → rw
```

### Given Geometry → Traffic

```
fi_shp / decoded_openlr → fi → cf
```

### Given Road → Traffic

```
rw → fi → cf
```

---

## 6. Why This Design Works

* Handles **sparse XML** correctly
* Supports **TMC and Off-TMC** roads uniformly
* Scales to large feeds
* Compatible with PostGIS spatial indexing
* Interview-ready and production-safe

---

## 7. Key Takeaway

> TrafficML is hierarchical and optional by nature.
> Modeling FI as the atomic unit with optional child tables
> is the only correct way to store and query this data.

---


