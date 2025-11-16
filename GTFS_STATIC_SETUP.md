# GTFS Static Feed Setup Guide

## Overview

The GTFS static feed provides mappings between stop names and stop IDs, route names and route IDs, which enables accurate matching between Google Maps transit data and TransLink GTFS-RT real-time data.

---

## Step 1: Download TransLink GTFS Static Feed

1. Visit TransLink's developer resources:
   https://www.translink.ca/about-us/doing-business-with-translink/app-developer-resources

2. Download the GTFS static feed (usually a ZIP file)

3. Extract the ZIP file - you'll see files like:
   - `stops.txt` - Stop information (names, IDs, locations)
   - `routes.txt` - Route information (names, IDs, types)
   - `trips.txt` - Trip information
   - `stop_times.txt` - Stop times for trips
   - `calendar.txt` - Service calendar
   - `agency.txt` - Agency information
   - etc.

---

## Step 2: Place GTFS Files in Project

Create a `gtfs` directory in your project root and copy all GTFS files there:

```bash
# From project root
cd /Users/jessicazhou/Repositories/destination.ai

# Create gtfs directory
mkdir -p gtfs

# Copy all GTFS files to gtfs/ directory
# (After extracting the ZIP file)
cp /path/to/extracted/gtfs/* gtfs/
```

**Expected structure:**
```
destination.ai/
├── backend/
├── frontend/
├── gtfs/              ← GTFS static feed files go here
│   ├── stops.txt
│   ├── routes.txt
│   ├── trips.txt
│   ├── stop_times.txt
│   └── ...
└── .env
```

---

## Step 3: Test GTFS Static Feed

Run the test script to verify the GTFS feed is loaded correctly:

```bash
# Activate virtual environment
source venv/bin/activate

# Run test
python backend/test_gtfs_static.py
```

**Expected output:**
```
✅ Loaded GTFS static feed successfully!
   - Stops: 5000+
   - Routes: 200+

✅ 'Commercial-Broadway Station' → 12345
✅ 'Waterfront Station' → 67890
...
```

---

## Step 4: How It Works

### Stop Name to Stop ID Mapping

When Google Maps provides a stop name like "Commercial-Broadway Station", the system:

1. **Looks up in GTFS static feed:**
   ```python
   stop_id = gtfs_static.get_stop_id_by_name("Commercial-Broadway Station")
   # Returns: "12345"
   ```

2. **Uses stop ID to match GTFS-RT data:**
   ```python
   real_time_data = get_stop_arrival_time(trip_updates, route_id, stop_id)
   ```

### Route Short Name to Route ID Mapping

When Google Maps provides route "99", the system:

1. **Looks up route ID:**
   ```python
   route_id = gtfs_static.get_route_id_by_short_name("99")
   # Returns: "99-123" (GTFS route ID)
   ```

2. **Matches with GTFS-RT trip updates**

---

## Step 5: Verify Integration

After setting up the GTFS static feed:

1. **Test GTFS-RT parsing:**
   ```bash
   python backend/test_gtfs_rt.py
   ```

2. **Make a route request** through your API - transit routes should now include:
   - Real-time delays
   - Accurate stop matching
   - Service alerts

---

## Troubleshooting

### "GTFS directory not found"

**Solution:** Make sure you created the `gtfs/` directory in the project root and copied all GTFS files there.

### "stops.txt not found"

**Solution:** Verify that `stops.txt` exists in the `gtfs/` directory. Check file names are correct (case-sensitive on some systems).

### "No stops found matching..."

**Possible causes:**
- Stop name doesn't match exactly (case-sensitive)
- GTFS feed is outdated
- Stop name format differs between Google Maps and GTFS

**Solution:** Use fuzzy matching or check stop names in `stops.txt`:
```python
# Fuzzy matching
matching_ids = parser.get_stop_ids_by_name_fuzzy("Commercial")
```

### Stop name doesn't match

Google Maps might use slightly different names than GTFS. The parser supports:
- Exact matching: `get_stop_id_by_name()`
- Fuzzy matching: `get_stop_ids_by_name_fuzzy()`
- Location-based: `find_stop_by_location()`

---

## Custom GTFS Path

If you want to use a different location for GTFS files:

```python
from app.gtfs_static import GTFSStaticParser

# Specify custom path
parser = GTFSStaticParser(gtfs_path=Path("/custom/path/to/gtfs"))
parser.load()
```

Or set environment variable:
```bash
export GTFS_PATH=/custom/path/to/gtfs
```

---

## Files Used

The parser currently uses:
- **stops.txt** - Stop name to ID mapping
- **routes.txt** - Route name to ID mapping

Other files (trips.txt, stop_times.txt, etc.) are available but not currently parsed. They can be added if needed for more advanced features.

---

## Next Steps

Once GTFS static feed is set up:

1. ✅ Stop names automatically map to stop IDs
2. ✅ Route short names map to route IDs
3. ✅ Real-time GTFS-RT data matches accurately
4. ✅ Routes show actual delays and arrival times

Your app now has **complete real-time transit accuracy**! 🚌

