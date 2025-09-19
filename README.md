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

# Password Wordlist Generator

**Educational Python tool to generate password wordlists** for ethical hacking practice, penetration testing in systems you own, and CTF challenges.

> ⚠️ **Disclaimer:** This tool is intended only for educational purposes. Do **NOT** use it to access accounts without permission. Misuse may be illegal.

---

## Installation

# Clone your GitHub repository
git clone https://github.com/aswinashi4/password-wordlist-generator.git && cd password-wordlist-generator && \
# Install Python dependencies (if any)
pip install -r requirements.txt 
# Add README.md or any changes
git add README.md 
# Commit changes with a message
git commit -m "Add installation and usage instructions" 
# Push to the main branch on GitHub
git push origin main 
# Example command to run the password generator
python generate_wordlist.py -w aswin,india --phone 78771252256 --phone-min 2 --phone-max 4 -s '@#' --caps --leet --years 2000 2004 --numbers 0 99 --include-common -o mywordlist.txt

