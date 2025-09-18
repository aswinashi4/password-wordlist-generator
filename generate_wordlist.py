#!/usr/bin/env python3
"""
generate_wordlist_aggressive.py

Aggressively generate many password permutations based on provided names + phone + numbers + years + symbols +
common name patterns, then shuffle.

Usage example:
  python generate_wordlist_aggressive.py \
    -w aswin,india -o out.txt \
    --phone 78771252256 --phone-min 2 --phone-max 4 \
    --years 2000 2004 \
    --numbers 0 99 \
    --seps '' _ @# \
    -s '@#' \
    --caps --leet \
    --include-common \
    --require-upper --require-symbol \
    --shuffle --max 500000

Notes:
 - Default: require at least one uppercase and one special symbol, shuffle the final result.
 - Increase --max to allow more outputs; default is 200000 (safety).
 - Use --no-shuffle, --no-enforce-upper, --no-enforce-symbol to relax defaults.
 - Be mindful of combinatorial explosion.
"""
from __future__ import annotations

import argparse
import itertools
import random
import sys
from typing import List, Set

# ---------------- common list (100-ish) ----------------
COMMON_100_INSTAGRAM = [
    '123456','123456789','password','12345678','qwerty','12345','1234567890','111111',
    '1234567','sunshine','qwerty123','iloveyou','princess','admin','welcome','666666',
    'abc123','football','123123','monkey','654321','charlie','aa123456','donald',
    'password1','qwerty1','letmein','dragon','baseball','superman','michael','shadow',
    'master','killer','trustno1','jordan','jennifer','zxcvbnm','asdfgh','hunter','buster',
    'soccer','harley','batman','andrew','tigger','sunshine1','iloveyou1','hello','freedom',
    'whatever','qazwsx','6543210','7777777','passw0rd','maggie','159753','aaaaaa','ginger',
    'princesa','pepper','11111111','131313','matthew','ashley','nicole','chelsea','biteme',
    'soccer1','mickey','bailey','access','flower','hannah','robert','cowboy','joshua','thomas',
    'andrea','tiffany','jasmine','liverpool','taylor','morgan','qwertyuiop','hottie','ginger1',
    'chelseA123','peanut','mustang','maverick','987654321','spiderman','qwert','abcd1234',
    '147258369','159357','donald1','lovely','112233','2000','2001','2002','2003','2004'
]

# ---------------- maps and defaults ----------------
LEET_MAP = {
    'a': ['4', '@'], 'b': ['8', '6'], 'e': ['3'], 'i': ['1', '!'],
    'l': ['1', '|'], 'o': ['0'], 's': ['5', '$'], 't': ['7']
}
DEFAULT_SPECIALS = list('!@#$%^&*()-_+=[]{};:,.<>?/\\|~`')

# ---------------- small helpers ----------------
def generate_leet_variants(s: str, max_variants: int = 8) -> Set[str]:
    s0 = s
    low = s.lower()
    variants = {s0, low}
    # single char replacements
    for i,ch in enumerate(low):
        if ch in LEET_MAP:
            for rep in LEET_MAP[ch]:
                arr = list(low)
                arr[i] = rep
                variants.add(''.join(arr))
                if len(variants) >= max_variants:
                    return set(list(variants)[:max_variants])
    # full mapped (first choice)
    mapped = ''.join(LEET_MAP[c][0] if c in LEET_MAP else c for c in low)
    variants.add(mapped)
    # mixed pattern
    mixed = list(low)
    repcount = 0
    for i,ch in enumerate(low):
        if ch in LEET_MAP and repcount % 2 == 0:
            mixed[i] = LEET_MAP[ch][0]
            repcount += 1
    variants.add(''.join(mixed))
    return set(list(variants)[:max_variants])

def cap_variants(s: str, caps: bool) -> Set[str]:
    v = {s}
    if not caps:
        return v
    v.add(s.lower())
    v.add(s.upper())
    v.add(s.capitalize())
    return v

def extract_phone_prefixes(phone: str, min_n: int, max_n: int) -> List[str]:
    digits = ''.join([c for c in phone if c.isdigit()])
    res = []
    if not digits:
        return res
    max_take = min(max_n, len(digits))
    for n in range(min_n, max_take+1):
        res.append(digits[:n])
    return res

# ---------------- name-common-patterns ----------------
COMMON_NAME_SUFFIXES = [
    '123','1234','12345','111','1111','0000','007','1','12','123456','2020','2021','2022','2023','2024','@123','#1','!','!1'
]
COMMON_NAME_PREFIXES = ['123','007','111','1','!','@']

def generate_name_common_patterns(names: List[str], symbols: List[str], years: List[str]) -> Set[str]:
    out = set()
    sym_list = symbols if symbols else DEFAULT_SPECIALS
    for name in names:
        low = name.lower()
        cap = name.capitalize()
        # suffixes and symbol combos
        for suf in COMMON_NAME_SUFFIXES:
            out.add(low + suf)
            out.add(cap + suf)
            # with symbol between name and suffix
            for sym in sym_list[:5]:
                out.add(low + sym + suf)
                out.add(cap + sym + suf)
        # prefixes
        for pre in COMMON_NAME_PREFIXES:
            out.add(pre + low)
            out.add(pre + cap)
            for sym in sym_list[:5]:
                out.add(pre + sym + low)
        # years
        for y in (years or []):
            out.add(low + y)
            out.add(cap + y)
            for sym in sym_list[:5]:
                out.add(low + sym + y)
                out.add(cap + sym + y)
    return out

# ---------------- generate many permutations ----------------
def insert_symbol_positions(name: str, symbols: List[str], seps: List[str]) -> Set[str]:
    """Produce variants where a symbol is inserted at different positions inside or around the name."""
    out = set()
    sym_list = symbols if symbols else DEFAULT_SPECIALS
    # prefix/suffix
    for sym in sym_list:
        out.add(sym + name)
        out.add(name + sym)
    # insert after first char, after second, middle, before last
    L = len(name)
    indices = [1, 2, max(1, L//2), max(1, L-1)]
    for i in set(indices):
        if i < L:
            for sym in sym_list:
                out.add(name[:i] + sym + name[i:])
                # with separators as well
                for sep in seps:
                    out.add(name[:i] + sep + sym + sep + name[i:])
    return out

def combine_all(name_variants: List[str],
                phone_prefixes: List[str],
                numbers: List[str],
                years: List[str],
                symbols: List[str],
                seps: List[str],
                include_inner_symbol_positions: bool = True) -> Set[str]:
    out = set()
    sym_list = symbols if symbols else DEFAULT_SPECIALS

    # Basic combos: name + phoneprefix, name + number, name + year, and with separators
    for name in name_variants:
        out.add(name)
        # append numbers
        for n in numbers:
            out.add(name + n)
            for sep in seps:
                out.add(name + sep + n)
                out.add(n + sep + name)
                for sym in sym_list[:4]:
                    out.add(name + sep + sym + n)
                    out.add(name + sep + n + sym)
        # phone prefixes
        for p in phone_prefixes:
            out.add(name + p)
            for sep in seps:
                out.add(name + sep + p)
                out.add(p + sep + name)
                for sym in sym_list[:4]:
                    out.add(name + sep + sym + p)
        # years
        for y in years:
            out.add(name + y)
            for sep in seps:
                out.add(name + sep + y)
                out.add(y + sep + name)
                for sym in sym_list[:4]:
                    out.add(name + sep + y + sym)
        # append symbols
        for sym in sym_list[:6]:
            out.add(name + sym)
            for sep in seps:
                out.add(name + sep + sym)
        # insert symbol inside name
        if include_inner_symbol_positions:
            for v in insert_symbol_positions(name, symbols, seps):
                out.add(v)
    return out

# ---------------- ensure requirements ----------------
def has_upper(s: str) -> bool:
    return any(c.isupper() for c in s)

def has_symbol(s: str, symbol_pool: List[str]) -> bool:
    if symbol_pool:
        return any(c in symbol_pool for c in s)
    return any(not c.isalnum() for c in s)

def minimally_enforce(s: str, require_upper: bool, require_symbol: bool, symbol_pool: List[str]) -> str:
    out = s
    # uppercase
    if require_upper and not has_upper(out):
        # capitalize first alphabetical char if exists else prepend 'A'
        lst = list(out)
        for i,ch in enumerate(lst):
            if ch.isalpha():
                lst[i] = lst[i].upper()
                out = ''.join(lst)
                break
        else:
            out = 'A' + out
    # symbol
    if require_symbol and not has_symbol(out, symbol_pool):
        if symbol_pool:
            out = out + symbol_pool[0]
        else:
            out = out + '!'
    return out

# ---------------- main orchestrator ----------------
def generate_aggressive(base_words: List[str],
                        include_common: bool,
                        phone: str,
                        phone_min: int,
                        phone_max: int,
                        numbers_from: List[str],
                        years_range: List[str],
                        seps: List[str],
                        symbols: List[str],
                        caps: bool,
                        leet: bool,
                        repeat: int,
                        combo: int,
                        max_items: int,
                        require_upper: bool,
                        require_symbol: bool,
                        shuffle_final: bool,
                        append_common_verbatim: bool) -> List[str]:

    # Expand and dedupe base names (with repeats)
    names = []
    if base_words:
        for w in base_words:
            if w:
                names.append(w)
                for r in range(2, repeat+1):
                    names.append(w * r)
    # dedupe keep order
    seen = set(); dedup_names = []
    for n in names:
        if n not in seen:
            seen.add(n); dedup_names.append(n)
    names = dedup_names

    # name variants: caps + leet
    name_variants = []
    for n in names:
        for c in cap_variants(n, caps):
            name_variants.append(c)
            if leet:
                for lv in generate_leet_variants(c):
                    name_variants.append(lv)
    # dedupe
    seen = set(); nv = []
    for n in name_variants:
        if n not in seen:
            seen.add(n); nv.append(n)
    name_variants = nv

    # prepare numbers list (either explicit numbers_from or default small range)
    numbers = numbers_from or []
    # prepare years
    years = years_range or []

    # phone prefixes
    phone_prefixes = extract_phone_prefixes(phone, phone_min, phone_max)

    # Generate name-common patterns and include them
    name_common = generate_name_common_patterns(names, symbols, years)
    # Expand name_common with caps/leet optionally
    expanded_name_common = set()
    for p in name_common:
        for c in cap_variants(p, caps):
            expanded_name_common.add(c)
            if leet:
                for lv in generate_leet_variants(c):
                    expanded_name_common.add(lv)

    # Combine permutations for each name variant
    generated = set()
    # base combine
    generated.update(combine_all(name_variants, phone_prefixes, numbers, years, symbols, seps, include_inner_symbol_positions=True))
    # combos across names up to 'combo' length (joined with separators)
    if combo > 1:
        for r in range(2, combo+1):
            for tup in itertools.permutations(name_variants, r):
                for sep in seps:
                    generated.add(sep.join(tup))
    # include expanded name_common
    generated.update(expanded_name_common)

    # minimally enforce requirements for each generated password
    symbol_pool = symbols if symbols else DEFAULT_SPECIALS
    # deterministic ordering before enforcement
    gen_sorted = sorted(generated)
    final_gen = []
    for p in gen_sorted:
        p2 = minimally_enforce(p, require_upper, require_symbol, symbol_pool)
        final_gen.append(p2)

    # Append common list if requested (either verbatim or enforced)
    final = list(final_gen)
    if include_common:
        if append_common_verbatim:
            final.extend(COMMON_100_INSTAGRAM)
        else:
            for p in COMMON_100_INSTAGRAM:
                p2 = p
                # transform to meet requirements minimally
                p2 = minimally_enforce(p2, require_upper, require_symbol, symbol_pool)
                final.append(p2)

    # dedupe preserving order-ish
    seen = set(); ordered = []
    for p in final:
        if p not in seen:
            seen.add(p); ordered.append(p)

    # shuffle if requested
    if shuffle_final:
        random.shuffle(ordered)

    # cap
    if len(ordered) > max_items:
        ordered = ordered[:max_items]

    return ordered

# ---------------- CLI ----------------
def parse_args():
    ap = argparse.ArgumentParser(description="Aggressive name-based password generator (many permutations + shuffle)")
    ap.add_argument('-w','--words', help='Comma-separated names/words (e.g. aswin,india)', default='')
    ap.add_argument('-f','--file', help='File with one word per line', default=None)
    ap.add_argument('-o','--output', help='Output file', default='wordlist.txt')
    ap.add_argument('--phone', help='Phone number to derive prefixes', default='')
    ap.add_argument('--phone-min', type=int, default=2)
    ap.add_argument('--phone-max', type=int, default=6)
    ap.add_argument('--numbers', nargs='*', type=int, help='Specific numbers to include (space separated)', default=None)
    ap.add_argument('--years', nargs=2, type=int, help='Year range: START END', default=None)
    ap.add_argument('--years-list', nargs='*', type=int, help='Specific years', default=None)
    ap.add_argument('--seps', nargs='+', help='Separators to use between tokens (quote empty: \"\" )', default=[''])
    ap.add_argument('-s','--symbols', help='Symbols string to prefer (e.g. \"@#\")', default='')
    ap.add_argument('--caps', action='store_true', help='Produce capitalization variants')
    ap.add_argument('--leet', action='store_true', help='Produce leetspeak variants')
    ap.add_argument('--repeat', type=int, default=1, help='Repeat each name up to N times (e.g. 2 -> name+name)')
    ap.add_argument('--combo', type=int, default=2, help='Max number of names to concat in combos')
    ap.add_argument('--max', type=int, default=200000, help='Maximum passwords to output (safety cap)')
    ap.add_argument('--include-common', action='store_true', help='Append common-100 list')
    ap.add_argument('--append-common-verbatim', action='store_true', help='Append the common list verbatim')
    ap.add_argument('--no-shuffle', dest='shuffle', action='store_false', help='Do NOT shuffle final list')
    ap.add_argument('--no-enforce-upper', dest='enforce_upper', action='store_false', help='Do NOT enforce uppercase requirement')
    ap.add_argument('--no-enforce-symbol', dest='enforce_symbol', action='store_false', help='Do NOT enforce symbol requirement')
    ap.set_defaults(shuffle=True, enforce_upper=True, enforce_symbol=True)
    return ap.parse_args()

def main():
    args = parse_args()

    base_words = []
    if args.words:
        base_words += [w.strip() for w in args.words.split(',') if w.strip()]
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as fh:
                for L in fh:
                    t = L.strip()
                    if t:
                        base_words.append(t)
        except FileNotFoundError:
            print("File not found:", args.file, file=sys.stderr)
            sys.exit(2)

    if not base_words and not args.include_common:
        print("No input words and not including common list. Provide --words, --file, or --include-common.", file=sys.stderr)
        sys.exit(2)

    numbers_from = [str(n) for n in args.numbers] if args.numbers else []
    years_range = []
    if args.years:
        s,e = args.years
        if s > e: s,e = e,s
        # safety trim
        if e - s > 300:
            e = s + 300
        years_range = [str(y) for y in range(s, e+1)]
    if args.years_list:
        years_range.extend(str(y) for y in args.years_list)

    seps = args.seps
    symbols = list(args.symbols) if args.symbols else []

    out = generate_aggressive(
        base_words=base_words,
        include_common=args.include_common,
        phone=args.phone,
        phone_min=args.phone_min,
        phone_max=args.phone_max,
        numbers_from=numbers_from,
        years_range=years_range,
        seps=seps,
        symbols=symbols,
        caps=args.caps,
        leet=args.leet,
        repeat=args.repeat,
        combo=args.combo,
        max_items=args.max,
        require_upper=args.enforce_upper,
        require_symbol=args.enforce_symbol,
        shuffle_final=args.shuffle,
        append_common_verbatim=args.append_common_verbatim
    )

    try:
        with open(args.output, 'w', encoding='utf-8') as fh:
            for item in out:
                fh.write(item + '\n')
        print(f"Wrote {len(out)} passwords to {args.output} (max cap {args.max})")
        print(f"Shuffled: {args.shuffle}, enforced uppercase: {args.enforce_upper}, enforced symbol: {args.enforce_symbol}")
    except Exception as e:
        print("Error writing output:", e, file=sys.stderr)
        sys.exit(3)

if __name__ == '__main__':
    main()

