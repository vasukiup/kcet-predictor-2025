"""
Diagnose the Annexure A column mapping problem.
Looking at the per-college data, the columns are clearly swapped for most colleges.
The PDF layout is: intake | kea | snq_5pct | kea_ph | kea_spl | kea_hk | kea_rk | kea_tot | over_above
But in many HK-heavy colleges, numbers look off.

Expected pattern for a 60-seat govt college:
  intake=60, kea=60, snq=3, ph=1, spl=~4, hk=~50, rk=~54, tot=3
  
Our extracted pattern for college #1:
  intake=30, kea=30, ph=1, spl=9 (wrong!), hk=27 (wrong!), rk=29 (wrong!)

The issue: for many rows the column parser is treating numbers incorrectly.
Let me check the raw parsed values vs what they should be by looking at
college #23 (which we manually entered) vs others.

College #23 (manual entry - correct):
  Course: AI&DS | intake=60 | kea=60 | ph=3 | spl=1 | hk=5 | rk=51 | tot=56 | over=3
  This gives kea_tot=56 per course

College #1 extracted:
  kea_ph=1, kea_spl=9, kea_hk=104, kea_rk=113, kea_tot=6, over=0
  --> kea_spl=9 is actually the SNQ quota, kea_hk is actually kea_rk, etc.
  --> The column called "kea_tot" in our data = over_above (SNQ 5%)
  --> And the column called "over_above" = 0 (missing)

So the mapping for extracted data is:
  nums[2] -> snq_5pct (stored as kea_ph) 
  nums[3] -> kea_ph   (stored as kea_spl)  -- BUT this should be 0 or 1
  nums[4] -> kea_spl  (stored as kea_hk)
  nums[5] -> kea_hk   (stored as kea_rk)
  nums[6] -> kea_rk   (stored as kea_tot)
  nums[7] -> kea_tot  (stored as over_above)
  nums[8] -> over_above = 0 (not captured)

Wait let me re-read the header from the PDF:
  Total Intake | Total KEA | SNQ 5% | PH | SPL | HK | RK | TOT HK-RK | Over&Above SNQ 5%

And our extractor code stored:
  nums[0] -> total_intake ✓
  nums[1] -> total_kea ✓
  nums[2] -> snq_5pct   (but stored in field "snq_5pct") 
  nums[3] -> kea_ph     ✓
  nums[4] -> kea_spl    ✓
  nums[5] -> kea_hk     ✓
  nums[6] -> kea_rk     ✓
  nums[7] -> kea_tot    ✓
  nums[8] -> over_above ✓

So field names are correct. Let me verify by checking what college #1 course values 
should look like from the PDF page 3.
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)

ann_a = sorted([c for c in d["colleges"] if c["annexure"] == "A"], key=lambda x: x["college_number"])

print("DETAILED COURSE DUMP - First 3 Annexure A colleges")
print("Expected pattern: intake=60, kea=60, snq=3, ph=1, spl=~4, hk=~50, rk=~54, tot=~56, over=3")
print()
for college in ann_a[:4]:
    print(f"#{college['college_number']} {college['college_name'][:55]}")
    for c in college["courses"]:
        print(f"  {c['course_name'][:40]:<42}"
              f" | intake={c.get('total_intake',0):>4}"
              f" | kea={c.get('total_kea_seats',0):>4}"
              f" | snq={c.get('snq_5pct',0):>3}"
              f" | ph={c.get('kea_ph',0):>2}"
              f" | spl={c.get('kea_spl',0):>3}"
              f" | hk={c.get('kea_hk',0):>3}"
              f" | rk={c.get('kea_rk',0):>3}"
              f" | tot={c.get('kea_tot',0):>3}"
              f" | over={c.get('over_above_5pct',0):>3}")
    print()

print()
print("College #23 (manually entered, known correct):")
col23 = next(c for c in ann_a if c["college_number"] == 23)
for c in col23["courses"]:
    print(f"  {c['course_name'][:40]:<42}"
          f" | intake={c.get('total_intake',0):>4}"
          f" | kea={c.get('total_kea_seats',0):>4}"
          f" | snq={c.get('snq_5pct',0):>3}"
          f" | ph={c.get('kea_ph',0):>2}"
          f" | spl={c.get('kea_spl',0):>3}"
          f" | hk={c.get('kea_hk',0):>3}"
          f" | rk={c.get('kea_rk',0):>3}"
          f" | tot={c.get('kea_tot',0):>3}"
          f" | over={c.get('over_above_5pct',0):>3}")

# Now compute what PDF totals imply about field mapping
print()
print("PDF grand total says:")
print("  PH=313, SPL=68, HK=1394, RK=4480, TOT=5874, Over=313")
print()
print("Our extracted sums say:")
our_ph  = sum(c.get("kea_ph",0)  for col in ann_a for c in col["courses"])
our_spl = sum(c.get("kea_spl",0) for col in ann_a for c in col["courses"])
our_hk  = sum(c.get("kea_hk",0)  for col in ann_a for c in col["courses"])
our_rk  = sum(c.get("kea_rk",0)  for col in ann_a for c in col["courses"])
our_tot = sum(c.get("kea_tot",0) for col in ann_a for c in col["courses"])
our_ovr = sum(c.get("over_above_5pct",0) for col in ann_a for c in col["courses"])
our_snq = sum(c.get("snq_5pct",0) for col in ann_a for c in col["courses"])
print(f"  snq={our_snq}, PH={our_ph}, SPL={our_spl}, HK={our_hk}, RK={our_rk}, TOT={our_tot}, Over={our_ovr}")
print()
print("Notice: our 'snq' matches PDF's PH (313 vs", our_snq, ")")
print("Notice: our 'kea_tot' matches PDF's Over (313 vs", our_tot, "? no..)")
print("Notice: our 'over' is", our_ovr)
print()
print("Let me check if snq=PH and kea_ph=SPL mapping:")
print(f"  snq={our_snq} vs PDF PH=313 -> {'MATCH' if our_snq==313 else 'no match'}")
print(f"  kea_ph={our_ph} vs PDF SPL=68 -> {'MATCH' if our_ph==68 else 'no match'}")
print(f"  kea_spl={our_spl} vs PDF HK=1394 -> {'MATCH' if our_spl==1394 else 'no match'}")
print(f"  kea_hk={our_hk} vs PDF RK=4480 -> {'MATCH' if our_hk==4480 else 'no match'}")
print(f"  kea_rk={our_rk} vs PDF TOT=5874 -> {'MATCH' if our_rk==5874 else 'no match'}")
print(f"  kea_tot={our_tot} vs PDF Over=313 -> {'MATCH' if our_tot==313 else 'no match'}")
