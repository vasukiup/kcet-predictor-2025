"""
Locate where the course-level intake sum on page 122 (calculated as 240) differs from the sum of the RK row first values (intake values).
Wait! On page 122, we had 8 RK rows, each with intake 30.
8 * 30 = 240.
Let's see why on page 138:
TOT intake = 240, parsed RK intake = 420.
Let's check the RK rows parsed on page 138:
1. RK CE 60 (intake 60)
2. RK CS 60 (intake 60)
3. RK EC 60 (intake 60)
4. RK ME 60 (intake 60)
Total intake for KR Pet college = 240.
But wait! Page 138 also has college #19:
1. RK CE 30 (intake 30)
2. RK CS 60 (intake 60)
3. RK EC 60 (intake 60)
4. RK EE 30 (intake 30)
Total intake for college #19 RK rows parsed on page 138 = 30 + 60 + 60 + 30 = 180.
So on page 138, we have RK rows for BOTH KR Pet (240 intake) and college #19 (180 intake).
240 + 180 = 420!
So the total parsed RK intake on page 138 is indeed 420.
But wait! What is the page-level TOT intake on page 138?
In our log:
`TOT 240 226 12 2 34 15 5 2 2 6 2 1 1 180 79 31 12 8 27 7 7 9`
This TOT line has intake = 240!
Wait, why is page-level TOT intake 240, when there is another college's courses on the page?
Ah! Look at page 138 text again:
For KR Pet college (college #18):
`TOT 240 226 12 2 34 15 5 2 2 6 2 1 1 180 79 31 12 8 27 7 7 9`
This TOT row is the COLLEGE total (KR Pet college total)! It's not a PAGE total!
Let's look at the prefix of the TOT line:
It is: `TOT 240 226 ...`
Wait, does every college have its own TOT line?
Yes! In our earlier investigation of page 122:
`TOT 240 226 ...`
And underneath it:
`KM QUOTA 11 4 3 0 ...`
This is college #1 (Constituent College of VTU) total!
So "TOT" is the COLLEGE total, not the PAGE total!
And "TOT" rows are printed whenever a college's courses finish!
Let's verify this hypothesis.
If TOT is the college total:
- College #18 total is printed on page 138: intake = 240, KEA = 226.
- College #19 (University BDT College) starts on page 138, but doesn't finish on page 138. Its courses continue on page 139 and page 140.
- College #19 finishes on page 140. And on page 140, we see:
`TOT 550 518 28 4 77 34 14 6 3 12 2 3 3 415 182 71 28 16 62 17 18 21`
Wait! Is college #19's total intake 550?
Let's check the RK intakes of college #19 parsed across pages 138, 139, 140:
On page 138:
- CE: 30
- CS: 60
- EC: 60
- EE: 30
On page 139:
- EIE: 30
- ME: 35
- RAI: 30
- CE: 30
- CS: 60
- EC: 60
- EE: 30
- EIE: 30
- ME: 35
On page 140:
- RAI: 30
Let's sum these RK intakes for college #19:
Page 138: 30 + 60 + 60 + 30 = 180.
Page 139: 30 + 35 + 30 + 30 + 60 + 60 + 30 + 30 + 35 = 370.
Page 140: 30.
Grand total of RK intakes for college #19 = 180 + 370 + 30 = 580!
Wait, but the TOT row at the bottom of college #19 (page 140) says:
`TOT 550` (intake = 550)!
Wait, why is the parsed sum 580, but the printed total is 550? That is a difference of 30!
Let's look at the courses parsed:
Wait, on page 139 we parsed:
- CE: 30
- CS: 60
- EC: 60
- EE: 30
- EIE: 30
- ME: 35
Are these courses from college #19, or is there another college starting on page 139?
Wait! Let's check page 139 text again:
It has:
- HK 2
- RK EIE 30
- RK ME 35
- RK RAI 30
- RK CE 30
- RK CS 60
- RK EC 60
- RK EE 30
- RK EIE 30
- RK ME 35
Wait, why are there duplicate courses? E.g., RK CE 30, RK CS 60, RK EC 60, RK EE 30, RK EIE 30, RK ME 35 are listed twice!
Ah! Let's look at page 138 again:
College #19 is: `19 University B.D.T College of Engineering, Davanagere`
But wait, page 139 has:
- CE 30
- CS 60
- EC 60
- EE 30
- EIE 30
- ME 35
Wait, are there two colleges on page 138/139?
Wait, University B.D.T College of Engineering has two entries in the PDF?
Or is there a second set of rows?
Let's look at the header:
No new college header is printed on page 139, but the courses are listed.
Wait! Let's check if they have "RK" or "HK" or different quotas.
Ah! Look at the first set:
- RK CE 30 (on page 138)
- RK CS 60 (on page 138)
- RK EC 60 (on page 138)
- RK EE 30 (on page 138)
Then EIE 30, ME 35, RAI 30 (on page 139).
Then it lists:
- RK CE 30 (on page 139)
- RK CS 60 (on page 139)
- RK EC 60 (on page 139)
- RK EE 30 (on page 139)
- RK EIE 30 (on page 139)
- RK ME 35 (on page 139)
Wait, why does it list CE, CS, EC, EE, EIE, ME again?
Let's write a script to print lines around these courses on page 139 to see if they belong to a different category or college.
"""
import pdfplumber

pdf = pdfplumber.open("Seat_Matrix_05072025.pdf")
print("=== Lines 1 to 50 on page 139 ===")
lines = pdf.pages[138].extract_text().splitlines()
for i, l in enumerate(lines[:60]):
    print(f"{i+1:2d}: {l}")
