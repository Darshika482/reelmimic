// A believable demo shop for the walkthrough screenshots. All names are invented.
const IMG = require('./img/images.json');
const TODAY = new Date('2026-11-04T10:30:00+05:30');
const iso = (dOff, h = 10, m = 0) => { const d = new Date(TODAY); d.setDate(d.getDate() + dOff); d.setHours(h, m, 0, 0); return d.toISOString(); };
const day = (dOff) => { const d = new Date(TODAY); d.setDate(d.getDate() + dOff); return d.toLocaleDateString('en-CA'); };
const T0 = iso(-40);
const prof = (id, name, role, phone, extra = {}) => ({ id, name, phone, role, master_id: null, pin: '', failed_attempts: 0, locked_until: null,
  is_active: true, language: 'en', consent_accepted_at: T0, created_at: T0, ...extra });
const profiles = [
  prof('a1', 'Admin', 'owner', '9800000001'),
  prof('h1', 'Manager', 'head', '9800000002'),
  prof('m1', 'Ramesh Master', 'master', '9811100001'),
  prof('m2', 'Dinesh Master', 'master', '9811100002'),
  prof('im1', 'Kailash (Independent)', 'master', '9811100003', { is_individual: true }),
  prof('k1', 'Rohit', 'karigar', '9822200001', { master_id: 'm1' }),
  prof('k2', 'Salim', 'karigar', '9822200002', { master_id: 'm1' }),
  prof('k3', 'Anil', 'karigar', '9822200003', { master_id: 'm2' }),
  prof('k4', 'Pappu', 'karigar', '9822200004', { master_id: 'm2' }),
  prof('s1', 'Imran (Individual)', 'karigar', '9822200005', { is_individual: true }),
  prof('pk1', 'Vinod', 'packer', '9833300001', { packing_rate: 4 }),
  prof('pk2', 'Mohan', 'packer', '9833300002', { packing_rate: 3.5 }),
  prof('st1', 'Pooja', 'staff', '9844400001', { monthly_salary: 12000, work_days_per_month: 26, work_hours_per_day: 8, pin: '1111' }),
  prof('st2', 'Sonu', 'staff', '9844400002', { monthly_salary: 10400, work_days_per_month: 26, work_hours_per_day: 8, pin: '2222' }),
  prof('st3', 'Neha', 'staff', '9844400003', { monthly_salary: 11000, work_days_per_month: 26, work_hours_per_day: 8, pin: '3333', branch_id: 'b1' }),
];
const P = (id, no, name, photo, avg, rate, mrate, prate = 0) => ({ id, pattern_no: no, name, photo_url: IMG[photo], default_avg_meters: avg, rate_per_piece: rate,
  master_rate_per_meter: mrate, packing_rate_per_piece: prate, is_active: true, created_at: iso(-38), created_by: 'a1' });
const patterns = [
  P('p1', '101', 'Kurta Set', 'design_1_kurta', 2.2, 32, 2, 0),
  P('p2', '102', 'Palazzo Pair', 'design_2_palazzo', 2.5, 45, 2),
  P('p3', '103', 'A-line Top', 'design_3_top', 1.4, 22, 1.5),
  P('p4', '104', 'Anarkali', 'design_4_anarkali', 3.2, 60, 2.5),
  P('p5', '105', 'Kids Frock', 'design_5_frock', 1.1, 18, 1.5),
  P('p6', '106', 'Co-ord Set', 'design_6_coord', 2.8, 40, 2),
  P('p7', '107', 'Straight Kurti', 'design_7_kurta', 2.0, 28, 2),
];
const TH = (id, code, dOff, party, fabric, lr, transport, rolls, notes = '') => ({ id, code, received_date: day(dOff), total_meters: rolls.reduce((s, r) => s + r[1], 0), unit: 'm',
  party_name: party, fabric_name: fabric, lr_code: lr, transport_name: transport, photo_url: IMG['roll_' + rolls[0][0]], extra_photo_urls: rolls.slice(1).map((r) => IMG['roll_' + r[0]]),
  photo_meters: Object.fromEntries(rolls.map((r) => [IMG['roll_' + r[0]], r[1]])), photo_taken_at: iso(dOff, 11), notes, deleted_at: null, created_at: iso(dOff, 11), created_by: 'a1' });
const thaans = [
  TH('t1', 'T-001', -30, 'Shree Ganesh Textiles', 'Rayon Print', 'LR-4521', 'VRL Logistics', [['maroon_floral', 120], ['navy_paisley', 110]]),
  TH('t2', 'T-002', -24, 'Laxmi Fabrics', 'Cotton Cambric', 'LR-4603', 'Gati Cargo', [['blue_stripe', 90], ['lilac_stripe', 80]]),
  TH('t3', 'T-003', -18, 'Shree Ganesh Textiles', 'Muslin Print', 'LR-4710', 'VRL Logistics', [['yellow_dots', 150]]),
  TH('t4', 'T-004', -12, 'Mahavir Silk Mills', 'Georgette', 'LR-4788', 'Om Transport', [['pink_floral', 140], ['green_paisley', 120], ['teal_zigzag', 60]]),
  TH('t5', 'T-005', -6, 'Laxmi Fabrics', 'Cotton Slub', 'LR-4852', 'Gati Cargo', [['black_check', 100], ['mustard', 80]]),
  TH('t6', 'T-006', -2, 'Krishna Textiles', 'Chanderi', 'LR-4901', 'Om Transport', [['white_chikan', 160], ['rust', 70]]),
];
const ph = (t, i) => [t.photo_url, ...(t.extra_photo_urls || [])][i];
let lotNo = 0;
const L = (id, dOff, t, pi, master, pattern, meters, avg, actual, status = 'open') => {
  const pat = patterns.find((p) => p.id === pattern); const exp = Math.floor(meters / avg);
  return { id, lot_no: ++lotNo, date: day(dOff), thaan_id: t.id, master_id: master, pattern_id: pattern, meters_used: meters, avg_meters: avg, expected_pieces: exp,
    actual_pieces: actual ?? exp, photo_url: pat.photo_url, photo_taken_at: iso(dOff, 12), thaan_photos: [ph(t, pi)], status, closed_at: status === 'closed' ? iso(dOff + 10) : null,
    master_rate_snapshot: pat.master_rate_per_meter, created_at: iso(dOff, 12), created_by: 'a1' };
};
const [t1, t2, t3, t4, t5, t6] = thaans;
const lots = [
  L('L1', -28, t1, 0, 'm1', 'p1', 110, 2.2, 50, 'closed'),
  L('L2', -27, t1, 1, 'm2', 'p2', 100, 2.5, 40),
  L('L3', -22, t2, 0, 'm1', 'p3', 84, 1.4, 60),
  L('L4', -20, t2, 1, 'm2', 'p7', 76, 2.0, 37),
  L('L5', -16, t3, 0, 'm1', 'p5', 132, 1.1, 118),
  L('L6', -10, t4, 0, 'm2', 'p4', 128, 3.2, 40),
  L('L7', -9, t4, 1, 'm1', 'p6', 112, 2.8, 40),
  L('L8', -4, t5, 0, 'm1', 'p1', 88, 2.2, 40),
  L('L9', -3, t4, 2, 'im1', 'p5', 55, 1.1, 50),
];
// A bundle lot: bundles given straight to a karigar, no thaan cutting.
lots.push({ id: 'L10', lot_no: ++lotNo, date: day(-2), thaan_id: null, master_id: null, pattern_id: 'p3', meters_used: null, avg_meters: null, expected_pieces: 120, actual_pieces: 120,
  photo_url: IMG.bundle_4, photo_taken_at: iso(-2, 15), thaan_photos: [], status: 'open', closed_at: null, created_at: iso(-2, 15), created_by: 'a1' });
let mv = 0;
const movements = [];
const M = (lot, k, type, pieces, dOff, extra = {}) => { const l = lots.find((x) => x.id === lot); const pat = patterns.find((p) => p.id === l.pattern_id);
  const rate = pat.rate_per_piece; movements.push({ id: 'mv' + ++mv, lot_id: lot, karigar_id: k, type, pieces, meters: null, rate_snapshot: rate, amount: type === 'in' ? pieces * rate : 0,
    status: 'approved', entered_by: 'a1', approved_by: 'a1', approved_at: iso(dOff, 17), reject_reason: null, is_paid: false, payment_id: null, photo_url: null,
    bundles: extra.bundles ?? null, bundle_size: extra.bundle_size ?? null, created_at: iso(dOff, extra.h ?? 11), ...extra.more }); return movements[movements.length - 1]; };
M('L1', 'k1', 'out', 30, -27, { bundles: 3, bundle_size: 10, more: { photo_url: IMG.bundle_1 } }); M('L1', 'k2', 'out', 20, -27, { bundles: 2, bundle_size: 10 });
const paidA = [M('L1', 'k1', 'in', 30, -20, { h: 17 }), M('L1', 'k2', 'in', 19, -19, { h: 16 })];
M('L1', 'k2', 'short', 1, -19, { h: 16, more: { reject_reason: 'Cut piece damaged' } });
M('L2', 'k3', 'out', 40, -26, { bundles: 4, bundle_size: 10, more: { photo_url: IMG.bundle_1 } }); M('L2', 'k3', 'in', 24, -12, { h: 17 });
M('L3', 'k1', 'out', 30, -21, { bundles: 3, bundle_size: 10, more: { photo_url: IMG.bundle_2 } }); M('L3', 'k2', 'out', 30, -21, { bundles: 5, bundle_size: 6 });
M('L3', 'k1', 'in', 30, -9, { h: 18 }); M('L3', 'k2', 'in', 18, -6, { h: 18 });
M('L4', 'k4', 'out', 37, -19, { bundles: 1, bundle_size: 37 }); M('L4', 'k4', 'in', 20, -8, { h: 17 });
M('L5', 's1', 'out', 60, -15, { bundles: 6, bundle_size: 10 }); M('L5', 'k1', 'out', 58, -15, { bundles: 2, bundle_size: 29 }); M('L5', 's1', 'in', 45, -5, { h: 17 }); M('L5', 'k1', 'in', 30, -3, { h: 17 });
M('L6', 'k3', 'out', 20, -9, { bundles: 2, bundle_size: 10, more: { photo_url: IMG.bundle_3 } }); M('L6', 'k4', 'out', 20, -9, { bundles: 2, bundle_size: 10 }); M('L6', 'k3', 'in', 12, -2, { h: 17 });
M('L7', 'k2', 'out', 40, -8, { bundles: 4, bundle_size: 10, more: { photo_url: IMG.bundle_4 } }); M('L7', 'k2', 'in', 16, -1, { h: 18 });
M('L8', 'k1', 'out', 24, -3, { bundles: 4, bundle_size: 6, more: { photo_url: IMG.bundle_1 } });
M('L9', 'im1', 'out', 50, -3); M('L9', 'im1', 'in', 30, 0, { h: 9 });
M('L10', 'k4', 'out', 120, -2, { bundles: 4, bundle_size: 30, more: { photo_url: IMG.bundle_4 } });
const payments = [{ id: 'pay1', karigar_id: 'k1', amount: paidA[0].amount, date: day(-15), mode: 'upi', note: 'Lot 1', movement_ids: [paidA[0].id], created_at: iso(-15, 18), created_by: 'a1' },
  { id: 'pay2', karigar_id: 'k2', amount: paidA[1].amount, date: day(-15), mode: 'cash', note: '', movement_ids: [paidA[1].id], created_at: iso(-15, 18), created_by: 'a1' }];
paidA.forEach((m, i) => { m.is_paid = true; m.payment_id = payments[i].id; });
lots[0].master_payment_id = 'pay3';
payments.push({ id: 'pay3', karigar_id: 'm1', amount: 110 * 2, date: day(-14), mode: 'cash', note: 'Cutting Lot 1', movement_ids: [], lot_ids: ['L1'], created_at: iso(-14, 18), created_by: 'a1' });
let pe = 0; const packingEntries = [];
const PK = (pk, dOff, lot, packages, ppp, paid = false) => { const rate = profiles.find((p) => p.id === pk).packing_rate; packingEntries.push({ id: 'pe' + ++pe, packer_id: pk, date: day(dOff), lot_id: lot,
  packages, pieces_per_package: ppp, pieces: packages * ppp, rate_snapshot: rate, rate_per: 'package', amount: packages * rate, status: 'approved', note: '', photo_url: pe % 2 ? IMG.boxes_1 : IMG.boxes_2,
  entered_by: 'a1', approved_by: 'a1', approved_at: iso(dOff, 18), reject_reason: null, is_paid: paid, payment_id: null, created_at: iso(dOff, 17) }); };
PK('pk1', -18, 'L1', 10, 5); PK('pk2', -17, 'L1', 9, 5); PK('pk1', -8, 'L3', 12, 4); PK('pk1', -5, 'L3', 9, 4); PK('pk2', -4, 'L5', 15, 5); PK('pk1', -1, 'L5', 12, 5); PK('pk2', 0, 'L2', 8, 3); PK('pk1', 0, 'L7', 6, 2);
// Attendance: three staff, Oct 1 → today, Sundays off, a couple of late days and one flagged check-in.
const attendance = []; let at = 0;
const UL = 28.6507, UG = 77.2662;
const staff = [['st1', IMG.avatar_1], ['st2', IMG.avatar_2], ['st3', IMG.avatar_4]];
for (let d = -34; d <= 0; d++) {
  const dt = new Date(TODAY); dt.setDate(dt.getDate() + d); if (dt.getDay() === 0) continue;
  staff.forEach(([sid, photo], si) => {
    if ((d + si * 5) % 11 === 0 && d !== 0) return; // a few absent days
    const late = (d + si) % 7 === 3; const lm = late ? 12 + ((-d) % 15) : 0;
    const flagged = sid === 'st2' && d === 0;
    const inAt = iso(d, 9, late ? lm + 10 : 2 + ((si * 3 - d) % 8));
    const out = d === 0 ? null : iso(d, 18, ((si * 7 - d * 3) % 40 + 40) % 40);
    attendance.push({ id: 'at' + ++at, staff_id: sid, date: day(d), check_in_at: inAt, photo_url: photo, lat: UL + (flagged ? 0.006 : 0.0002 * si), lng: UG + 0.0001, gps_accuracy_m: 12,
      distance_m: flagged ? 640 : 18 + si * 9, inside_area: !flagged, is_late: late, late_minutes: lm, review_status: flagged ? 'flagged' : 'ok', reviewed_by: null, reviewed_at: null,
      payment_id: null, check_out_at: out, check_out_by: out ? 'a1' : null, check_out_photo_url: out ? photo : null, branch_id: sid === 'st3' ? 'b1' : null });
  });
}
// October salary already paid for each staff member.
staff.forEach(([sid], i) => { const days = attendance.filter((a) => a.staff_id === sid && a.date < '2026-11-01');
  const pid = 'sal' + i; const prof_ = profiles.find((p) => p.id === sid);
  payments.push({ id: pid, karigar_id: sid, amount: prof_.monthly_salary, date: '2026-11-01', mode: i === 1 ? 'cash' : 'upi', note: 'October salary', movement_ids: [],
    attendance_ids: days.map((a) => a.id), salary_month: '2026-10-01', created_at: iso(-3, 11), created_by: 'a1' });
  days.forEach((a) => (a.payment_id = pid)); });
const settings = { unit_lat: UL, unit_lng: UG, area_radius_m: 150, reporting_time: '09:00', late_grace_minutes: 10, photo_retention_days: 30, shortage_allowance_percent: 2,
  default_packing_rate: 3, default_daily_rate: 0, default_monthly_salary: 10000, work_days_per_month: 26, work_hours_per_day: 8, pay_by_day: true, pay_by_hour: true, attendance_gps: true,
  branches: [{ id: 'b1', name: 'Gandhi Nagar Branch', lat: 28.6612, lng: 77.2771, radius_m: 150 }], report_day: 1, telegram_bot_username: 'shop_report_bot', telegram_linked_at: iso(-20) };
module.exports = (who = 'a1') => {
  const me = profiles.find((p) => p.id === who);
  return { session: { token: 'test', profile: me }, data_owner: who, 'data:profiles': profiles, 'data:patterns': patterns, 'data:thaans': thaans, 'data:lots': lots,
    'data:movements': movements, 'data:packingEntries': packingEntries, 'data:payments': payments, 'data:attendance': attendance, 'data:settings': settings,
    'data:auditLogs': [], 'data:rateHistory': [], 'last_sync': iso(0, 10, 25) };
};
module.exports.IMG = IMG;
