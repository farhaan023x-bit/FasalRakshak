import re
import sys
from collections import Counter

def load(path):
    text = open(path, encoding="utf-8").read()
    nums = Counter(re.findall(r"\d+(?:[.,]\d+)*%?", text))
    cites = Counter(re.findall(
        r"\[\d+(?:[,\u2013-]\s*\d+)*\]|\([A-Z][A-Za-z]+(?: et al\.)?,? \d{4}\)", text))
    heads = re.findall(r"^#{1,6} .+$", text, re.M)
    verify_marks = len(re.findall(r"\[VERIFY:", text))
    return nums, cites, heads, len(text.split()), verify_marks

if len(sys.argv) != 3:
    print("Usage: verify.py original.md humanized.md")
    sys.exit(2)

o, h = load(sys.argv[1]), load(sys.argv[2])
bad = False

for name, a, b in (("number", o[0], h[0]), ("citation", o[1], h[1])):
    for k, v in (a - b).items():
        print(f"MISSING {name}: {k} (x{v})")
        bad = True
    for k, v in (b - a).items():
        print(f"ADDED {name}: {k} (x{v})")
        bad = True

if o[2] != h[2]:
    print("HEADINGS differ between original and humanized")
    bad = True

ratio = h[3] / max(o[3], 1)
print(f"Word count ratio: {ratio:.2f}")
if not 0.85 <= ratio <= 1.15:
    print("Length is outside +/-15%")
    bad = True

print(f"[VERIFY] markers remaining: {h[4]}")
print("FAIL" if bad else "PASS")
sys.exit(1 if bad else 0)
