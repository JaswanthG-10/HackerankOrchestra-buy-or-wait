import json
import re
import pandas as pd
from pathlib import Path

def parse_all_messages(messages_csv_path: Path, output_cache_path: Path):
    df_msg = pd.read_csv(messages_csv_path)
    cache = {}

    for _, row in df_msg.iterrows():
        text = str(row['message_text']).strip()
        u_id = str(row['user_id'])
        m_id = str(row['message_id'])
        req_id = str(row['request_id']) if pd.notnull(row['request_id']) else None
        ev_id = str(row['related_event_id']) if pd.notnull(row['related_event_id']) else None
        src = str(row['source_type'])

        res = {
            'message_id': m_id,
            'user_id': u_id,
            'request_id': req_id,
            'related_event_id': ev_id,
            'source_type': src,
            'fact_type': 'other',
            'is_confirmed_cash': False,
            'amount': None,
            'currency': None,
            'effective_date': None,
            'percentage_change': None,
            'summary': ''
        }

        # 1. Internal transfer
        if 'transfer between your two accounts' in text or 'transfer antara dua rekening Anda' in text:
            res['fact_type'] = 'internal_transfer'
            res['is_confirmed_cash'] = False
            res['summary'] = 'Internal account transfer; net-zero cash impact.'
            cache[m_id] = res
            continue

        # 2. Advance fee scam / fraudulent cash prize
        if 'cash prize' in text.lower() and ('pay the release charge' in text.lower() or 'pay the processing charge' in text.lower()) or ('hadiah uang tunai' in text.lower() and 'bayar biaya pencairan' in text.lower()):
            res['fact_type'] = 'scam_ignored'
            res['is_confirmed_cash'] = False
            res['summary'] = 'Advance-fee prize notice ignored; fraudulent non-cash.'
            cache[m_id] = res
            continue

        # 3. Unrealized investment valuation change
        if 'displayed market value has increased' in text or 'No units have been sold' in text or 'nilai pasar yang ditampilkan' in text or 'The holding has not been sold and there has been no cash transaction' in text or 'Investasi tersebut belum dijual dan tidak ada transaksi tunai' in text or 'displayed value of the investment has fallen' in text:
            res['fact_type'] = 'unrealized_investment'
            res['is_confirmed_cash'] = False
            res['summary'] = 'Unrealized investment valuation; no cash proceeds.'
            cache[m_id] = res
            continue

        # 4. Investment sale proceeds settled in cash
        if 'proceeds from your investment sale have settled' in text or 'Hasil penjualan investasi Anda sudah masuk ke rekening tunai' in text:
            res['fact_type'] = 'investment_sale_settled'
            res['is_confirmed_cash'] = True
            res['summary'] = 'Investment sale proceeds confirmed settled in cash account.'
            cache[m_id] = res
            continue

        # 5. Pending card dispute reversal
        if 'reversal has not been posted' in text or 'dana pembalikannya belum tercatat' in text or 'extra card charge is still being investigated' in text or 'Tagihan kartu tambahan masih dalam penyelidikan' in text:
            res['fact_type'] = 'pending_unconfirmed'
            res['is_confirmed_cash'] = False
            res['summary'] = 'Card dispute reversal pending; do not count until posted.'
            cache[m_id] = res
            continue

        # 6. Failed debit retry (outstanding bill still due)
        if 'previous debit attempt failed' in text or 'debit attempt failed' in text or 'tagihan masih belum terbayar dan debit lain akan dicoba' in text:
            res['fact_type'] = 'failed_debit_retry'
            res['is_confirmed_cash'] = False
            res['summary'] = 'Previous debit failed; bill is still outstanding and will be retried.'
            cache[m_id] = res
            continue

        # 7. Foreign currency settlement notice
        if 'bill was charged in a foreign currency' in text or 'Tagihan dikenakan dalam mata uang asing' in text:
            res['fact_type'] = 'foreign_currency_notice'
            res['is_confirmed_cash'] = False
            res['summary'] = 'Foreign currency charge; will convert on settlement date.'
            cache[m_id] = res
            continue

        # 8. Pending refunds
        if 'refund has been initiated' in text or 'pengembalian dana Anda telah dimulai' in text or 'refund is still processing' in text or 'Pengembalian dana sudah diproses, tetapi belum masuk' in text:
            res['fact_type'] = 'pending_unconfirmed'
            res['is_confirmed_cash'] = False
            res['summary'] = 'Refund is pending; do not count until settled.'
            cache[m_id] = res
            continue

        # 9. Pending bonus / commission / gig payout
        if 'bonus' in text.lower() and ('pending' in text.lower() or 'menunggu' in text.lower() or 'belum disetujui' in text.lower() or 'subject to' in text.lower()):
            res['fact_type'] = 'pending_unconfirmed'
            res['is_confirmed_cash'] = False
            res['summary'] = 'Bonus is pending/unapproved; do not count.'
            cache[m_id] = res
            continue

        if 'payout is still pending' in text or ('pembayaran berikutnya' in text and 'masih tertunda' in text) or 'isnt withdrawable' in text or 'belum dapat ditarik' in text:
            res['fact_type'] = 'pending_unconfirmed'
            res['is_confirmed_cash'] = False
            res['summary'] = 'Gig payout pending; not withdrawable until settled.'
            cache[m_id] = res
            continue

        if 'komisi dari transaksi' in text.lower() or ('commission' in text.lower() and ('not been confirmed' in text.lower() or 'belum disetujui' in text.lower() or 'pending' in text.lower())):
            res['fact_type'] = 'pending_unconfirmed'
            res['is_confirmed_cash'] = False
            res['summary'] = 'Commission unconfirmed; do not count.'
            cache[m_id] = res
            continue

        # 10. Seasonal contract ended
        if 'seasonal contract has ended' in text or 'kontrak musiman saat ini telah berakhir' in text or 'No off-season income' in text:
            res['fact_type'] = 'contract_ended'
            res['is_confirmed_cash'] = False
            res['amount'] = 0.0
            res['summary'] = 'Seasonal contract ended; no upcoming salary.'
            cache[m_id] = res
            continue

        # 11. Prize claim closed / completed or pending
        if 'prize proceeds have reached your account' in text or 'hadiah telah masuk ke rekening Anda' in text:
            res['fact_type'] = 'prize_closed'
            res['is_confirmed_cash'] = False
            res['summary'] = 'Prize claim closed; no future payments scheduled.'
            cache[m_id] = res
            continue
        if 'prize claim has been verified and is still in payment processing' in text or 'Klaim hadiah Anda sudah diverifikasi dan masih dalam proses' in text:
            res['fact_type'] = 'pending_unconfirmed'
            res['is_confirmed_cash'] = False
            res['summary'] = 'Prize in processing; do not count until credited.'
            cache[m_id] = res
            continue

        # 12. Multiple card accounts note
        if 'separate card accounts' in text:
            res['fact_type'] = 'card_notice'
            res['is_confirmed_cash'] = False
            res['summary'] = 'Minimum payments due on separate card accounts.'
            cache[m_id] = res
            continue

        # 13. Rent increase
        rent_m = re.search(r'rent by (\d+)%|sewa bulanan sebesar (\d+)%', text, re.I)
        if rent_m:
            pct = float(rent_m.group(1) or rent_m.group(2))
            res['fact_type'] = 'rent_increase'
            res['percentage_change'] = pct
            res['summary'] = f'Rent increased by {pct}%.'
            cache[m_id] = res
            continue

        # 14. Receipt reference
        if 'payment was received on' in text or 'tote bag order was paid' in text:
            res['fact_type'] = 'receipt_reference'
            res['is_confirmed_cash'] = True
            res['summary'] = 'Receipt reference for paid expense.'
            cache[m_id] = res
            continue

        # 15. Invoice approved
        inv_m = re.search(r'(?:invoice payment of|pembayaran faktur sebesar)\s+([A-Z]{3})\s+([\d,\.]+)', text, re.I)
        if inv_m:
            curr = inv_m.group(1)
            raw_val = inv_m.group(2).replace(',', '').rstrip('.')
            amt = float(raw_val)
            date_m = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', text)
            eff_date = date_m.group(1) if date_m else None
            res['fact_type'] = 'confirmed_income'
            res['amount'] = amt
            res['currency'] = curr
            res['effective_date'] = eff_date
            res['is_confirmed_cash'] = True
            res['summary'] = f'Confirmed invoice payout of {curr} {amt:,.2f}'
            cache[m_id] = res
            continue

        # 16. Salary date change
        date_chg = re.search(r'(?:salary is now expected on|gaji Anda yang sudah dikonfirmasi kini diperkirakan pada)\s+(\d{4}-\d{2}-\d{2})', text, re.I)
        if date_chg:
            res['fact_type'] = 'salary_date_change'
            res['effective_date'] = date_chg.group(1)
            res['is_confirmed_cash'] = True
            res['summary'] = f'Salary payment date revised to {date_chg.group(1)}'
            cache[m_id] = res
            continue

        # 17. Salary amount updates
        sal_m = re.search(r'(?:naik menjadi|increased to|gaji bulanan sementara Anda adalah|temporary monthly pay is|reduced to|turun menjadi|first salary will be|gaji pertama.*?adalah|gaji pertama dari perusahaan baru adalah|remaining confirmed monthly salary is|sisa gaji bulanan yang dikonfirmasi adalah|regular salary of|gaji pokok yang dikonfirmasi adalah|gaji rutin.*?adalah|regular salary.*?is)\s+([A-Z]{3})\s+([\d,\.]+)', text, re.I)
        if sal_m:
            curr = sal_m.group(1)
            raw_val = sal_m.group(2).replace(',', '').rstrip('.')
            amt = float(raw_val)
            date_m = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', text)
            eff_date = date_m.group(1) if date_m else None
            res['fact_type'] = 'salary_update'
            res['amount'] = amt
            res['currency'] = curr
            res['effective_date'] = eff_date
            res['is_confirmed_cash'] = True
            res['summary'] = f'Salary updated to {curr} {amt:,.2f}'
            cache[m_id] = res
            continue

        # 18. General salary confirmation
        if 'gaji rutin' in text.lower() or 'payroll' in text.lower() or 'salary' in text.lower():
            res['fact_type'] = 'salary_confirmed'
            res['is_confirmed_cash'] = True
            res['summary'] = 'Salary confirmed per standard schedule.'
            cache[m_id] = res
            continue

        cache[m_id] = res

    with open(output_cache_path, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2)

    return cache

c = parse_all_messages(Path('dataset/messages.csv'), Path('code/cache/messages.json'))
print('Parsed total messages:', len(c))
counts = {}
for m in c.values():
    ft = m['fact_type']
    counts[ft] = counts.get(ft, 0) + 1
print('Breakdown:', counts)
print('Unclassified (\"other\") count:', counts.get('other', 0))
