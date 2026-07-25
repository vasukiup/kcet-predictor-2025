"""
Check if we can write a robust, page-based course parsing strategy.
For each page:
1. Extract text.
2. Find all lines starting with "RK " or "HK " or containing "KM QUOTA".
3. Group these lines by course. Since each course starts with "RK " and can have optional subsequent "KM QUOTA" (belonging to RK), followed by optional "HK " and optional "KM QUOTA" (belonging to HK).
Let's see if we can model this state machine.
For a page:
A line can be:
- RK row: starts with "RK "
- HK row: starts with "HK "
- KM QUOTA row: starts with "KM QUOTA "
- TOT row: starts with "TOT "
- College header: matches college regex (usually at the start of a page or in the middle of a page, e.g. "20 VISVESVARAYA...")

Let's trace how many college headers are defined:
Usually, a college block starts with:
`\n(\d{1,3})\s+([A-Z][A-Za-z\s\(\)&\.\,\'\-\/]+)`
Wait! Let's check how many college headers are on a page. Some pages might have a college header, and some might not (if a college continues from the previous page).
Also, some pages might have college headers in the middle of the page (if the previous college finishes at the top of the page, and a new college starts in the middle).
Let's write a script to trace this state machine and build a robust parser.
"""
import re

# Let's test the state machine on pages 138-141.
# A course object:
# {
#   "name": "...",
#   "intake": ...,
#   "kea_rk": ...,
#   "kea_hk": ...,
#   "ph_rk": ...,
#   "ph_hk": ...,
#   "spl_rk": ...,
#   "spl_hk": ...
# }

# Let's define the parsing function.
