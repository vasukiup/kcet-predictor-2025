"""
Fix Annexure A column mapping.

Root cause: The PDF row layout is:
  [serial] [course name] [total_intake] [total_kea] [SNQ_5pct] [PH] [SPL] [HK] [RK] [TOT_HK_RK] [Over_SNQ_5pct]

The extractor reads numbers starting at total_intake. So:
  nums[0] = total_intake       ✓
  nums[1] = total_kea          ✓
  nums[2] = SNQ_5pct           -> stored as snq_5pct  (but our field says "snq_5pct" which is correct!)
  nums[3] = PH                 -> stored as kea_ph    ✓
  nums[4] = SPL                -> stored as kea_spl   ✓
  nums[5] = HK                 -> stored as kea_hk    ✓
  nums[6] = RK                 -> stored as kea_rk    ✓
  nums[7] = TOT_HK_RK          -> stored as kea_tot   ✓
  nums[8] = Over_SNQ_5pct      -> stored as over_above_5pct ✓

BUT the PDF total row says:
  PH=313, SPL=68, HK=1394, RK=4480, TOT=5874, Over=313

And our sums say:
  snq=310, ph=78, spl=1372, hk=4191, rk=5796, tot=576, over=15

That means our "snq" (310) ≈ PDF "PH" (313) -- OFF by 3 (the 3 from college #23 which has correct values)
Our "ph" (78) ≈ PDF "SPL" (68) -- OFF by 10
Our "spl" (1372) ≈ PDF "HK" (1394) -- OFF by 22
Our "hk" (4191) ≈ PDF "RK" (4480) -- OFF by 289
Our "rk" (5796) ≈ PDF "TOT" (5874) -- OFF by 78
Our "tot" (576) is completely off from PDF "Over" (313)

Wait - the pattern suggests the columns are shifted:
  our snq_5pct  = PDF's PH
  our kea_ph    = PDF's SPL
  our kea_spl   = PDF's HK
  our kea_hk    = PDF's RK
  our kea_rk    = PDF's TOT HK-RK
  our kea_tot   = PDF's Over_SNQ_5%

That means the extractor's nums[2] is actually PH (not SNQ), because the SNQ value is 
part of the text header "SNQ 5%" and the actual SNQ number in the data row comes AFTER
the intake and KEA numbers, but before PH... OR the SNQ column isn't a separate number
in the data rows - it's a header concept, not a data column.

Looking at the sample data from the image:
  Course row: 60 | 60 | 3 | 1 | 5 | 51 | 56 | 3
  
According to PDF header:
  Intake | KEA | SNQ 5% | PH | SPL | HK | RK | TOT HK-RK | Over SNQ 5%
  
But that's 9 columns for 8 numbers! The "SNQ 5%" column appears to be labeled separately
but doesn't have its own standalone number -- OR the column labeled "Over & Above Intake SNQ 5%"
IS the same as "SNQ 5%" and they share the same value.

Actually looking at the image more carefully:
Row: 60 | 60 | 3 | 1 | 5 | 51 | 56 | 3
     Intake|KEA|???|PH|SPL|HK |RK |TOT|???

The header shows "SNQ 5%" under "Intake" and "KEA PH SPL HK RK TOT" under "CAT-1 KEA SEATS"
And "Over & Above Intake SNQ 5%" is the last column.

So the actual columns are:
  nums[0] = total_intake
  nums[1] = total_kea  
  nums[2] = PH         <- This is what's labeled "PH 5%" in sub-header
  nums[3] = SPL
  nums[4] = HK
  nums[5] = RK
  nums[6] = TOT HK-RK  <- This should be ~HK+RK combined? No, it's HK+SPL+PH...
  nums[7] = Over & Above SNQ 5%

And the "SNQ 5% Intake" (= 5% of intake) column is the SAME as "Over & Above Intake SNQ 5%"
shown at the end - it's shown as both a header description AND the last column value.

So the correct mapping is:
  nums[0] -> total_intake
  nums[1] -> total_kea
  nums[2] -> kea_ph (PH 5%)
  nums[3] -> kea_spl (SPL)
  nums[4] -> kea_hk (HK)
  nums[5] -> kea_rk (RK)
  nums[6] -> kea_tot (TOT HK-RK SEATS)
  nums[7] -> over_above_5pct (Over & Above Intake SNQ 5%)

The "snq_5pct" field we stored is wrong -- it's actually the PH value!
"""

import json, sys
sys.stdout.reconfigure(encoding="utf-8")

with open("seat_matrix_data.json", encoding="utf-8") as f:
    d = json.load(f)

ann_a_before = [c for c in d["colleges"] if c["annexure"] == "A"]

# Fix the column mapping for all Annexure A, B colleges (same format)
# Current (wrong for A/B):  snq=PH, ph=SPL, spl=HK, hk=RK, rk=TOT, tot=over, over=0
# Correct:                  ph=snq, spl=ph, hk=spl, rk=hk, tot=spl+hk, over=rk
#
# Actually the simplest fix: shift all fields left by one:
#   new kea_ph    = old snq_5pct
#   new kea_spl   = old kea_ph
#   new kea_hk    = old kea_spl
#   new kea_rk    = old kea_hk
#   new kea_tot   = old kea_rk
#   new over_above= old kea_tot
#   new snq_5pct  = 0 (or compute as over_above)

fixed_count = 0
for college in d["colleges"]:
    # Only fix A and B (same format), skip college #23 which was manually entered correctly
    if college["annexure"] not in ["A", "B"]:
        continue
    if college["college_number"] == 23 and college["annexure"] == "A":
        continue  # Already correct

    for c in college["courses"]:
        old_snq  = c.get("snq_5pct", 0)
        old_ph   = c.get("kea_ph", 0)
        old_spl  = c.get("kea_spl", 0)
        old_hk   = c.get("kea_hk", 0)
        old_rk   = c.get("kea_rk", 0)
        old_tot  = c.get("kea_tot", 0)
        old_over = c.get("over_above_5pct", 0)

        # Shift: snq->ph, ph->spl, spl->hk, hk->rk, rk->tot, tot->over
        c["kea_ph"]          = old_snq   # PH
        c["kea_spl"]         = old_ph    # SPL
        c["kea_hk"]          = old_spl   # HK
        c["kea_rk"]          = old_hk    # RK
        c["kea_tot"]         = old_rk    # TOT HK-RK
        c["over_above_5pct"] = old_tot   # Over & Above SNQ 5%
        c["snq_5pct"]        = old_over  # SNQ = Over value (they're the same)
        fixed_count += 1

with open("seat_matrix_data.json", "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print(f"Fixed {fixed_count} course rows in Annexure A and B.")

# Now recheck against PDF totals
PDF_TOTALS = {
    "kea_ph":          313,
    "kea_spl":         68,
    "kea_hk":          1394,
    "kea_rk":          4480,
    "kea_tot":         5874,
    "over_above_5pct": 313,
}

ann_a = [c for c in d["colleges"] if c["annexure"] == "A"]
sums = {k: 0 for k in PDF_TOTALS}
intake_sum = 0
kea_sum = 0
for college in ann_a:
    for c in college["courses"]:
        intake_sum += c.get("total_intake", 0)
        kea_sum    += c.get("total_kea_seats", 0)
        for k in PDF_TOTALS:
            sums[k] += c.get(k, 0)

LABELS = {
    "kea_ph": "PH 5%", "kea_spl": "SPL", "kea_hk": "HK",
    "kea_rk": "RK", "kea_tot": "TOT HK-RK", "over_above_5pct": "Over SNQ 5%"
}

SEP = "-" * 60
print(SEP)
print("  ANNEXURE A RE-CHECK AFTER COLUMN FIX")
print(SEP)
print(f"  {'Field':<20} {'PDF':>8} {'Ours':>8} {'Diff':>8} {'Status'}")
print(SEP)
print(f"  {'Total Intake':<20} {6255:>8} {intake_sum:>8} {intake_sum-6255:>+8}  {'OK' if intake_sum==6255 else 'MISMATCH'}")
print(f"  {'Total KEA':<20} {6255:>8} {kea_sum:>8} {kea_sum-6255:>+8}  {'OK' if kea_sum==6255 else 'MISMATCH'}")
all_ok = (intake_sum == 6255 and kea_sum == 6255)
for k, label in LABELS.items():
    pdf_v = PDF_TOTALS[k]
    our_v = sums[k]
    diff  = our_v - pdf_v
    ok    = "OK" if diff == 0 else f"OFF {diff:+d}"
    if diff != 0:
        all_ok = False
    print(f"  {label:<20} {pdf_v:>8} {our_v:>8} {diff:>+8}  {ok}")
print(SEP)
print(f"  RESULT: {'ALL MATCH - PERFECT' if all_ok else 'STILL HAS MISMATCHES'}")
print(f"  Total colleges in A: {len(ann_a)}/23")
