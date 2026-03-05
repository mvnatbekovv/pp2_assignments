import re
import json


def money_to_float(s: str) -> float:
    """
    '18 009,00' -> 18009.00
    '1 200,00'  -> 1200.00
    """
    s = s.replace("\xa0", " ").replace(" ", "").replace(",", ".")
    return float(s)


def parse_receipt(text: str) -> dict:
    # --- HEADER ---
    shop = None
    bin_number = None

    m_shop = re.search(r"(?m)^Филиал\s+(.+)$", text)
    if m_shop:
        shop = m_shop.group(1).strip()

    m_bin = re.search(r"(?m)^БИН\s+(\d+)\s*$", text)
    if m_bin:
        bin_number = m_bin.group(1)

    # --- DATE/TIME ---
    date_str = None
    time_str = None
    m_dt = re.search(r"Время:\s*(\d{2}\.\d{2}\.\d{4})\s+(\d{2}:\d{2}:\d{2})", text)
    if m_dt:
        date_str, time_str = m_dt.group(1), m_dt.group(2)

    # --- PAYMENT + TOTALS ---
    payment_method = None
    payment_amount = None

    m_card = re.search(r"Банковская карта:\s*\n([\d\s]+,\d{2})", text)
    if m_card:
        payment_method = "CARD"
        payment_amount = money_to_float(m_card.group(1))

    m_total = re.search(r"ИТОГО:\s*\n([\d\s]+,\d{2})", text)
    total_amount = money_to_float(m_total.group(1)) if m_total else None

    m_vat = re.search(r"в т\.ч\.\s*НДС\s*12%:\s*\n([\d\s]+,\d{2})", text)
    vat_12 = money_to_float(m_vat.group(1)) if m_vat else None

    # Пример блока:
    # 1.
    # Натрия хлорид ...
    # 2,000 x 154,00
    # 308,00
    item_pattern = re.compile(
        r"(?m)^\s*(\d+)\.\s*\n"         # номер
        r"(.+?)\n"                     # название
        r"(\d+,\d{3})\s*x\s*([\d\s]+,\d{2})\n"   # qty x unit price
        r"([\d\s]+,\d{2})"             # line total
    )

    items = []
    for m in item_pattern.finditer(text):
        idx = int(m.group(1))
        name = m.group(2).strip()
        qty = float(m.group(3).replace(",", "."))
        unit_price = money_to_float(m.group(4))
        line_total = money_to_float(m.group(5))

        items.append({
            "index": idx,
            "name": name,
            "qty": qty,
            "unit_price": unit_price,
            "line_total": line_total,
        })

    calc_total = round(sum(i["line_total"] for i in items), 2)

    return {
        "shop": shop,
        "bin": bin_number,
        "date": date_str,
        "time": time_str,
        "payment": {
            "method": payment_method,
            "amount": payment_amount
        },
        "totals": {
            "total": total_amount,
            "vat_12": vat_12,
            "calculated_from_items": calc_total
        },
        "items": items
    }


def main():
    with open("raw.txt", "r", encoding="utf-8") as f:
        text = f.read()

    data = parse_receipt(text)

    print(json.dumps(data, ensure_ascii=False, indent=2))

    print("\n--- SUMMARY ---")
    print(f"Shop: {data.get('shop')}")
    print(f"BIN: {data.get('bin')}")
    print(f"Date/Time: {data.get('date')} {data.get('time')}")
    print(f"Payment: {data['payment']['method']}  Amount: {data['payment']['amount']}")
    print(f"Total (receipt): {data['totals']['total']}")
    print(f"Total (calculated): {data['totals']['calculated_from_items']}")
    print(f"Items count: {len(data['items'])}")


if __name__ == "__main__":
    main()