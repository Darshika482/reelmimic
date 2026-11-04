#!/usr/bin/env python3
"""Writes SCRIPT.md — the narration script with real timestamps — from video/timeline.json."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent
tl = json.loads((ROOT / 'video' / 'timeline.json').read_text())
SHOT_LABEL = {
    's01_login': 'Sign-in screen (phone + PIN)', 's02_dashboard': 'Dashboard', 's03_dashboard_alerts': 'Dashboard: counts and shop alerts',
    's04_sidebar': 'Admin menu', 's05_manager_menu': 'Manager menu (fewer sections)', 's06_hindi': 'Dashboard in Hindi',
    's07_thaan_list': 'Thaan list', 's08_thaan_photos': 'New thaan: photos with meters', 's09_thaan_fields': 'New thaan: details and total',
    's10_write_on_photo': 'Write on photo', 's11_thaan_detail': 'Thaan details', 's12_patterns': 'Pattern catalog and rates',
    's13_pattern_form': 'Edit pattern', 's14_cut_master': 'New cutting: pick master', 's15_cut_photo_match': 'Find thaan by photo',
    's16_cut_design_picker': 'Pick design', 's17_cut_check': 'Check new cutting', 's18_lot_register': 'Lot register', 's19_lot_details': 'Lot details',
    's20_give_choices': 'Give maal: three choices', 's21_give_bundles': 'Bundles × pieces', 's22_give_patterns': 'Pick pattern per photo',
    's23_give_check': 'Check maal out', 's24_give_saved': 'Maal out recorded', 's25_take_pick_lot': 'Take back: pick lot',
    's26_take_pieces': 'Pieces count and hisaab', 's27_take_check': 'Check maal in', 's28_karigar_page': "Karigar's page",
    's28b_karigar_lots': "Karigar's lots", 's29_master_page': "Master's page", 's30_karigars': 'Karigar list', 's31_packing_form': 'Packing entry',
    's32_packing_register': 'Packing register', 's33_payments': 'Payments: who is owed', 's34_pay_karigar': 'Paying a karigar',
    's35_pay_salary': 'Staff salary worked out', 's36_attendance_today': "Today's check-ins (one flagged)", 's37_staff_self': "Staff member's own screen",
    's38_staff_camera': 'Live-photo check-in', 's39_staff_calendar': 'Attendance calendar', 's41_analytics': 'Work analytics',
    's41b_analytics_people': 'Analytics per person', 's42_records': 'Records (audit trail)', 's43_reports': 'Shop reports',
    's44_hisaab_whatsapp': 'Hisaab PDF + WhatsApp message', 's45_pdf_preview': 'Shop report PDF', 's46_settings_location': 'Settings: unit location',
    's47_settings_salary': 'Settings: salary rules', 's48_settings_branches': 'Settings: branches', 's48b_settings_telegram': 'Settings: Telegram report',
    's49_settings_maint': 'Settings: cleanup and backup', 's50_people': 'Logins & people', 's51_add_person': 'Add person',
    's52_undo': 'Undo a delete', 's53_offline': 'Offline: saved on the phone', 's54_profile': 'Profile',
}
def ts(s): return f'{int(s // 60)}:{s % 60:04.1f}'
out = [f"# Script: {json.loads((ROOT / 'script.json').read_text())['title']}", '',
       f"Length: **{ts(tl['total'])}** (16:9, 1920×1080, narrated). The app is never named, and every screen comes from a demo shop with invented names.", '',
       '| # | Time | Section | Narration (voice-over) | On screen |', '|---|---|---|---|---|']
for i, s in enumerate(tl['scenes']):
    sec = s['title'].replace('\n', ' ')
    shots = '<br>'.join(SHOT_LABEL.get(x, x) for x in s['shots'])
    pts = ' · '.join(s['points'])
    out.append(f"| {s['chapter'] or '—'} | {ts(s['start'])} | **{sec}** | {s['narration']} | *Text:* {pts}<br>*Phone:* {shots} |")
(ROOT / 'SCRIPT.md').write_text('\n'.join(out) + '\n')
print('wrote SCRIPT.md')
