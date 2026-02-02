## 1️⃣ `TRAFFICML_REALTIME` (Root Tag)

**Meaning:**
Top-level container for the entire real-time traffic feed snapshot.

**Purpose:**
Defines metadata about **what map**, **what version**, **what unit system**, and **when** this traffic data was generated.

**Key attributes:**

* `xmlns` → XML namespace
* `MAP_VERSION` → HERE map release used for referencing roads
* `MAP_DVN` → Internal map data version number
* `TMC_TABLE_VERSION` → Version of TMC location tables
* `CREATED_TIMESTAMP` → Time when this file was generated (UTC)
* `VERSION` → TrafficML schema version (e.g. 3.2.2)
* `UNITS` → Metric or Imperial (important for speed/length)

---

## 2️⃣ `FEATURES`

**Meaning:**
Capability declaration block.

**Purpose:**
Tells the consumer **which advanced features are active in this feed** so your parser doesn’t break when new elements appear.

**Your listed features mean:**

* `LANES` → Lane-level traffic possible
* `FORM_OF_WAY` → Road type info (motorway, single carriageway, etc.)
* `EXPRESS` → Express road classification
* `OPEN_LR` → OpenLR (map-independent) location referencing
* `DLR_AGGREGATION` → Multiple SHP geometries can be aggregated
* `HOV` → High-Occupancy Vehicle lane traffic

---

## 3️⃣ `RWS` (Roadway Segment Set)

**Meaning:**
A **collection of roadways** for a geographic region.

**Purpose:**
Groups all traffic data belonging to a **specific TMC table + country**.

**Attributes:**

* `TY` → Type of feed (usually `TMC`)
* `MAP_DVN` → Map version used
* `EBU_COUNTRY_CODE` → Country code (traffic standard)
* `EXTENDED_COUNTRY_CODE` → Disambiguates shared country codes
* `TABLE_ID` → TMC table identifier

---

## 4️⃣ `RW` (Roadway)

**Meaning:**
A **logical road entity** (e.g., a named highway).

**Purpose:**
Groups multiple traffic segments (FIs) belonging to the same road.

**Attributes:**

* `LI` → Location identifier
* `DE` → Road description / name
* `PBT` → Predictive Base Time (used for forecasts)
* `mid` → Message / correlation ID

---

## 5️⃣ `FIS` (Flow Item Set)

**Meaning:**
Container for traffic **segments** on a roadway.

**Purpose:**
Holds multiple `FI` elements that together describe traffic along the road.

**Attributes:**
None (pure grouping element).

---

## 6️⃣ `FI` (Flow Item)

**Meaning:**
**Atomic traffic segment** — this is where traffic data actually applies.

**Purpose:**
Represents one continuous stretch of road with uniform traffic behavior.

**Key behavior:**


* Can be **TMC-based** or **Off-TMC**
* May or may not contain `SHP`
* Always paired with a `CF`
* this tag mostly has three more tags inside it,
these are ->
TMC,
TPEGOpenLRBase64,
CF

---

## 7️⃣ `TMC`

**Meaning:**
Traffic Message Channel reference.

**Purpose:**
Defines the **official traffic-coded location** of the segment.

**Attributes:**

* `PC` → TMC location code
* `DE` → Road description
* `QD` → Queue direction (`+` or `-`)
* `LE` → Length of segment

---

## 8️⃣ `TPEGOpenLRBase64`

**Meaning:**
Map-independent location reference (OpenLR).

**Purpose:**
Allows clients to map traffic to **any map provider**, not just HERE.

**Details:**

* Base64-encoded binary OpenLR data
* Decoded → matched to road geometry

---

## 9️⃣ `CF` (Current Flow)

**Meaning:**
**Actual traffic state** for the FI.

**Purpose:**
This is the **most important tag** — speeds, congestion, confidence.

**Attributes:**

* `TY` → Traffic type (e.g. TR)
* `SP` → Speed
* `SU` → Speed unfiltered
* `FF` → Free-flow speed
* `JF` → Jam factor (0–10)
* `CN` → Confidence
* `TS` → Traversability state (Open, Closed, RNR)

---
**sometimes CF tag has one more tag inside it, and that is SSS tag.**


## 🔟 `SSS` (Sub-Segment Set)

**Meaning:**
Breaks an FI into **smaller pieces** when traffic varies internally.

**Purpose:**
Higher granularity traffic (lane changes, partial congestion).

---

## 1️⃣1️⃣ `SS` (Sub-Segment)

**Meaning:**
Traffic info for a **portion of the FI**.

**Attributes:**

* `LE` → Sub-segment length
* `SP` → Speed
* `SU` → Speed unfiltered
* `FF` → Free flow
* `JF` → Jam factor
* `TS` → Traversability

---
**one behaviour of this XML file is that not all FI tags have <SHP>tags, entire xml is divided in two parts one where FI tag has SHP tag and other where FI tag does not have SHP tag.**

## 1️⃣2️⃣ `SHP` (Shape)

**Meaning:**
Raw **geometry** of off-TMC roads.

**Purpose:**
Used when traffic is reported on roads **not covered by TMCs**.

**Attributes:**

* `FC` → Functional road class
* `LID` → Link ID
* `LE` → Length
* `FW` → Form of way

**Important behavior (you observed correctly):**

* FI **with SHP** → Off-TMC / DLR road
* FI **without SHP** → TMC-coded road

---

## 🔚 Diagnostic Tag

**Meaning:**
Feed-level diagnostics.

**Attributes:**

* `sfile` → Source file identifier
* `pdd` → Processing / delivery diagnostic data

**Purpose:**
Debugging, ingestion tracking, SLA monitoring.

---

## 🧠 Mental Model (keep this)

```
TRAFFICML_REALTIME
 └─ RWS
    └─ RW
       └─ FIS
          └─ FI
             ├─ TMC / SHP / OpenLR
             └─ CF
                └─ SSS
                   └─ SS
```

---


