import pandas as pd
import re
import json

df_msg = pd.read_csv('dataset/messages.csv')

def parse_message(row):
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

    if 'transfer between your two accounts' in text or 'transfer antara dua rekening Anda' in text:
        res['fact_type'] = 'internal_transfer'
        res['is_confirmed_cash'] = False
        res['summary'] = 'Internal account transfer; net-zero cash impact.'
        return res

    if 'displayed market value has increased substantially' in text or 'No units have been sold' in text or 'nilai pasar yang ditampilkan pada portofolio Anda telah meningkat' in text:
        res['fact_type'] = 'unrealized_investment'
        res['is_confirmed_cash'] = False
        res['summary'] = 'Unrealized investment valuation; no cash proceeds.'
        return res

    if 'refund has been initiated' in text or 'pengembalian dana Anda telah dimulai' in text or 'refund is still processing' in text:
        res['fact_type'] = 'pending_unconfirmed'
        res['is_confirmed_cash'] = False
        res['summary'] = 'Refund is pending; do not count until settled.'
        return res

    if 'bonus' in text.lower() and ('pending' in text.lower() or 'menunggu' in text.lower() or 'belum disetujui' in text.lower() or 'subject to' in text.lower()):
        res['fact_type'] = 'pending_unconfirmed'
        res['is_confirmed_cash'] = False
        res['summary'] = 'Bonus is pending/unapproved; do not count.'
        return res

    if 'payout is still pending' in text or 'pembayaran berikutnya' in text and 'masih tertunda' in text or 'isnt withdrawable' in text or 'belum dapat ditarik' in text:
        res['fact_type'] = 'pending_unconfirmed'
        res['is_confirmed_cash'] = False
        res['summary'] = 'Gig payout pending; not withdrawable until settled.'
        return res

    if 'komisi dari transaksi' in text.lower() or 'commission' in text.lower() and ('not been confirmed' in text.lower() or 'belum disetujui' in text.lower() or 'pending' in text.lower()):
        res['fact_type'] = 'pending_unconfirmed'
        res['is_confirmed_cash'] = False
        res['summary'] = 'Commission unconfirmed; do not count.'
        return res

    if 'seasonal contract has ended' in text or 'kontrak musiman saat ini telah berakhir' in text or 'No off-season income' in text:
        res['fact_type'] = 'contract_ended'
        res['is_confirmed_cash'] = False
        res['amount'] = 0.0
        res['summary'] = 'Seasonal contract ended; no upcoming salary from this contract.'
        return res

    if 'prize proceeds have reached your account' in text or 'hadiah telah masuk ke rekening Anda' in text:
        res['fact_type'] = 'prize_closed'
        res['is_confirmed_cash'] = False
        res['summary'] = 'Prize claim closed; no future payments scheduled.'
        return res
    if 'prize claim has been verified and is still in payment processing' in text:
        res['fact_type'] = 'pending_unconfirmed'
        res['is_confirmed_cash'] = False
        res['summary'] = 'Prize in processing; do not count until credited.'
        return res

    rent_m = re.search(r'rent by (\d+)%|sewa bulanan sebesar (\d+)%', text, re.I)
    if rent_m:
        pct = float(rent_m.group(1) or rent_m.group(2))
        res['fact_type'] = 'rent_increase'
        res['percentage_change'] = pct
        res['summary'] = 'Rent increased by ' + str(pct) + '%.'
        return res

    if 'payment was received on' in text or 'tote bag order was paid' in text:
        res['fact_type'] = 'receipt_reference'
        res['is_confirmed_cash'] = True
        res['summary'] = 'Receipt reference for paid expense.'
        return res

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
        res['summary'] = 'Confirmed invoice payout of ' + str(curr) + ' ' + str(amt)
        return res

    date_chg = re.search(r'(?:salary is now expected on|gaji Anda yang sudah dikonfirmasi kini diperkirakan pada)\s+(\d{4}-\d{2}-\d{2})', text, re.I)
    if date_chg:
        res['fact_type'] = 'salary_date_change'
        res['effective_date'] = date_chg.group(1)
        res['is_confirmed_cash'] = True
        res['summary'] = 'Salary payment date revised to ' + str(date_chg.group(1))
        return res

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
        res['summary'] = 'Salary updated to ' + str(curr) + ' ' + str(amt)
        return res

    if 'gaji rutin' in text.lower() or 'payroll' in text.lower() or 'salary' in text.lower():
        res['fact_type'] = 'salary_confirmed'
        res['is_confirmed_cash'] = True
        res['summary'] = 'Salary confirmed per standard schedule.'
        return res

    return res

results = [parse_message(r) for _, r in df_msg.iterrows()]
df_res = pd.DataFrame(results)
print('Fact type breakdown:')
print(df_res['fact_type'].value_counts())
unclass = df_res[df_res['fact_type'] == 'other']
print('Unclassified count:', len(unclass))
if len(unclass) > 0:
    for _, r in unclass.iterrows():
        print(r['message_id'], r['summary'])
