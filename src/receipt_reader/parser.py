import re
from ..config import client
from datetime import datetime

# ------------------ OpenAI Parser ------------------ #


def openai_parse_receipt(raw_text: str):
    response = client.responses.create(
        model="gpt-4o-mini",
        input=f"""
        Extract all GCash transactions from the text.

        For EACH transaction, output in this exact format:
        For empty key values default to None.

        name=<value> (It is usually the first line of gcash receipt.)
        ref=<value>
        phone_number=<value> (starts with country code)
        amount=<float=value>
        total=<float value>
        currency_code=<base on the phone number>
        date=<value (mm-dd-yyyy)>

        Do NOT alter the name (example: JO•N PA•L L.).
        Do NOT output JSON.
        Do NOT use quotes.
        Do NOT wrap in brackets.
        Just repeat the 6 lines for every transaction.
        Do NOT add currency currency codes in amount and total
        Double CHECK everything, I need accuracy.

        Text:
        \"\"\"{raw_text}\"\"\"
        """,
    )

    result = (response.output_text).strip().split("\n")
    data = dict()
    for items in result:
        key, value = items.strip().split("=")
        if key == "phone_number":
            raw_value = value.replace(" ", "")
            value = raw_value[:3] + " " + raw_value[3:]

        country_code = result[2].strip().split("=")[1][:3]
        if key == "currency_code":
            value = "PHP" if country_code == "+63" else value
        if key == "amount" or key == "total":
            value = float(value)
        data[key.strip()] = value
    return data


# ------------------ Regex Parser ------------------ #
def regex_parse_receipt(text: str):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    joined = " ".join(lines)

    # 1. Name
    name = None
    for line in lines:
        if re.search(r"\d", line):
            continue
        if any(key in line.lower() for key in ["amount", "total", "ref", "service fee", "php", "created on"]):
            continue
        if len(line) >= 3:
            name = line
            break

    # 2. Phone number
    phone = None
    phone_match = re.search(
        r"(\+63\s?\d{3}\s?\d{3}\s?\d{4}|09\d{2}\s?\d{3}\s?\d{4})", text)
    if phone_match:
        phone = re.sub(r"\s+", "", phone_match.group())
        if phone.startswith("09"):
            phone = "+63" + phone[1:]

    # 3. Amount
    def find_money(patterns):
        for p in patterns:
            m = re.search(p, joined, re.IGNORECASE)
            if m:
                val = m.group(1).replace(",", "").replace(
                    "P", "").replace(" ", "")
                try:
                    return float(val)
                except:
                    pass
        return None

    amount = find_money([
        r"Amount\s+P?([0-9,]+\.\d+)",
        r"Amount[: ]+PHP\s*([0-9,]+\.\d+)"
    ])

    # 4. Total
    total = find_money([
        r"Total Amount Sent\s+P?\s*([0-9,]+\.\d+)",
        r"Total Amount\s+P?\s*([0-9,]+\.\d+)",
        r"Total\s+P?\s*([0-9,]+\.\d+)",
        r"Total\s+Amount\s+PHP\s*([0-9,]+\.\d+)"
    ])
    if total is None:
        total = amount  # fallback

    # 5. Reference
    ref = None
    ref1 = re.search(
        r"Ref\s*No[.:;,]?\s*([0-9 ]{10,20})", joined, re.IGNORECASE)
    # ref1 = re.search(r"Ref\s*No\.?\s*([0-9 ]{10,20})", joined, re.IGNORECASE)
    ref2 = re.search(
        r"Reference\s*no[.:;,]?\s*([A-Za-z0-9\-]+)", joined, re.IGNORECASE)

    ref_extra = re.search(
        r"Ref\s*No[.:;,]?.*\n\s*(\d{4,8})", text, re.IGNORECASE)

    if ref1:
        ref = f"{ref1.group(1).strip()} {ref_extra.group(1).strip()}" if ref_extra else ref1.group(
            1).strip()
    elif ref2:
        ref = ref2.group(1).strip()

    # 6. Date
    date = None
    date_patterns = [
        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*\d{1,2},\s*\d{4}",
        r"\d{1,2}-\d{1,2}-\d{4}"
    ]
    for p in date_patterns:
        raw = re.search(p, joined, re.IGNORECASE)
        if raw:
            raw_date = raw.group(0)
            try:
                if "-" in raw_date:
                    d = datetime.strptime(raw_date, "%d-%m-%Y")
                else:
                    d = datetime.strptime(raw_date.replace(" ", ""), "%b%d,%Y")
                date = d.strftime("%m-%d-%Y")
            except:
                pass
            break

    currency_code = "PHP"

    return {
        "name": name,
        "ref": ref,
        "phone_number": phone,
        "amount": amount,
        "total": total,
        "currency_code": currency_code,
        "date": date,
    }


# ------------------ Hybrid Parser ------------------ #
def hybrid_parse_gcash_receipt(text: str):
    # Step 1: Try regex parser
    result = regex_parse_receipt(text)

    # Step 2: Check for missing fields
    missing_fields = [k for k, v in result.items() if v is None]
    if missing_fields:
        # Call OpenAI fallback'
        fallback_result = openai_parse_receipt(text)
        if fallback_result:
            # Merge: prefer regex if exists, else fallback
            for k in result:
                if result[k] is None and k in fallback_result:
                    result[k] = fallback_result[k]

    return result
