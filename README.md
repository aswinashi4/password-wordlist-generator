# Password Wordlist Generator

**Educational Python tool to generate password wordlists** for penetration testing, CTF challenges, or systems you own and have permission to test.  

> ⚠️ **Disclaimer:** This tool is intended **only for ethical and educational purposes**. Do **NOT** use it to access accounts or systems without permission. Misuse may be illegal.

---

## Features

- Generates password permutations based on:
  - Names / words
  - Phone numbers
  - Years / numeric ranges
  - Special characters
  - Common name-based password patterns (like `Aswin123`, `aswin@2020`, etc.)
- Supports capitalization variants and leetspeak substitutions.
- Includes optional 100 most common Instagram passwords.
- Shuffles generated wordlist for maximum variation.
- Enforces:
  - At least one capital letter
  - At least one special symbol

---

## Installation

## Installation

1. **Clone the Repository:**

```bash
git clone https://github.com/aswinashi4/password-wordlist-generator.git
cd password-wordlist-generator

pip install -r requirements.txt

---

## 3️⃣ Add a **Usage** Section

Right after the installation, add:

```markdown
## Usage

To generate a password wordlist, run:

```bash
python generate_wordlist.py -w aswin,india --phone 78771252256 --phone-min 2 --phone-max 4 -s '@#' --caps --leet --years 2000 2004 --numbers 0 99 --include-common -o mywordlist.txt


-w aswin,india → Base words/names

--phone 78771252256 → Phone number prefixes

--phone-min 2 / --phone-max 4 → Number of phone digits to append

-s '@#' → Special characters

--caps → Capitalization variants

--leet → Leetspeak substitutions

--years 2000 2004 → Year range

--numbers 0 99 → Numeric suffixes

--include-common → Include common passwords

-o mywordlist.txt → Output file



---

## 4️⃣ Commit and Push Changes

Run the following commands in your terminal from the repository folder:

```bash
git add README.md
git commit -m "Add installation and usage instructions"
git push origin main
