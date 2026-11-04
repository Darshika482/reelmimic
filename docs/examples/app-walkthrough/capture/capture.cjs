// Final screenshots for the walkthrough, in storyboard order. Each group starts from a fresh demo shop.
const { launch, snap, tap, text } = require('./lib.cjs');
const IMGD = __dirname + '/img/';
const chooser = async (page, trigger) => { const c = page.waitForEvent('filechooser', { timeout: 5000 }).catch(() => null); await trigger(); return c; };
const go = async (page, it) => { await tap(page, page.getByRole('button', { name: 'Menu' }).first()); await tap(page, page.locator('nav').getByText(it, { exact: true }).filter({ visible: true }).first(), 1300); };
const scrollTo = (page, t) => page.getByText(t, { exact: true }).first().evaluate((e) => e.scrollIntoView({ block: 'start' }));
const shot = async (page, name, fn, w = 1200) => { try { if (fn) await fn(); await page.waitForTimeout(w); await snap(page, name); } catch (e) { console.log('FAIL', name, e.message.split('\n')[0]); } };
const sec = async (name, fn, who = 'a1', opts) => { const { browser, page } = await launch(who, opts); try { await fn(page); } catch (e) { console.log('SEC FAIL', name, e.message.split('\n')[0]); } await browser.close(); };
const G = {
  intro: async () => {
    await sec('login', async (p) => { await shot(p, 's01_login'); }, null);
    await sec('dash', async (p) => {
      await shot(p, 's02_dashboard');
      await shot(p, 's03_dashboard_alerts', () => scrollTo(p, 'Shop Alerts'));
      await shot(p, 's04_sidebar', async () => { await p.evaluate(() => scrollTo(0, 0)); await tap(p, p.getByRole('button', { name: 'Menu' }).first()); });
    });
    await sec('mgr', async (p) => { await shot(p, 's05_manager_menu', () => tap(p, p.getByRole('button', { name: 'Menu' }).first())); }, 'h1');
    await sec('hi', async (p) => { await shot(p, 's06_hindi', () => tap(p, p.getByRole('button', { name: 'Language' }).first()), 1500); });
  },
  thaan: async () => {
    await sec('thaanlist', async (p) => { await go(p, 'Register'); await tap(p, p.getByRole('button', { name: 'Thaan', exact: true }).first(), 1000); await shot(p, 's07_thaan_list');
    });
    await sec('thaandetail', async (p) => { await tap(p, p.getByText('New Cutting', { exact: true }).first(), 1200); await tap(p, p.getByText('Ramesh Master').filter({ visible: true }).last(), 1200);
      await shot(p, 's11_thaan_detail', () => p.getByRole('button', { name: /Thaan details|Details/ }).filter({ visible: true }).last().click(), 1500); });
    await sec('thaanform', async (p) => {
      await tap(p, p.getByText('New Thaan', { exact: true }).first(), 1200);
      const c = await chooser(p, () => p.getByText('Gallery', { exact: true }).filter({ visible: true }).first().click());
      await c.setFiles([IMGD + 'roll_pink_floral.jpg', IMGD + 'roll_green_paisley.jpg', IMGD + 'roll_teal_zigzag.jpg']); await p.waitForTimeout(2500);
      const n = p.locator('input[type=number]'); await n.nth(0).fill('140'); await n.nth(1).fill('120'); await n.nth(2).fill('60');
      await p.getByPlaceholder('Who sent the cloth').fill('Mahavir Silk Mills'); await p.getByPlaceholder('e.g. Cotton Cambric').fill('Georgette Print');
      await p.getByPlaceholder('e.g. LR-4521').fill('LR-4960'); await p.getByPlaceholder('e.g. VRL Logistics').fill('Om Transport'); await p.getByPlaceholder('e.g. VRL Logistics').blur();
      await shot(p, 's08_thaan_photos', () => p.getByText('Thaan photos').first().evaluate((e) => e.scrollIntoView({ block: 'start' })));
      await shot(p, 's09_thaan_fields', () => p.getByText('Cloth counted in').first().evaluate((e) => e.scrollIntoView({ block: 'center' })));
      await p.getByText('Thaan photos').first().evaluate((e) => e.scrollIntoView({ block: 'start' }));
      await tap(p, p.getByRole('button', { name: 'Write' }).first(), 1500);
      const img = p.locator('img').filter({ visible: true }).last(); const b = await img.boundingBox();
      if (b) { await p.mouse.click(b.x + b.width * 0.3, b.y + b.height * 0.25); await p.waitForTimeout(700); await p.keyboard.type('60 m'); await p.waitForTimeout(400);
        const ok = p.getByRole('button', { name: /^(Done|OK|Add)$/ }).filter({ visible: true }).first(); if (await ok.count()) await ok.click(); }
      await shot(p, 's10_write_on_photo', null, 900);
    });
  },
  patterns: async () => {
    await sec('pat', async (p) => { await go(p, 'Register'); await tap(p, p.getByRole('button', { name: 'Patterns', exact: true }).first(), 1000); await shot(p, 's12_patterns');
      await shot(p, 's13_pattern_form', () => p.getByText('Edit Pattern').first().click(), 1300); });
  },
  cutting: async () => {
    await sec('cut', async (p) => {
      await tap(p, p.getByText('New Cutting', { exact: true }).first(), 1200); await shot(p, 's14_cut_master');
      await tap(p, p.getByText('Ramesh Master').filter({ visible: true }).last(), 1200);
      const c = await chooser(p, () => p.getByText('Choose from gallery').filter({ visible: true }).first().click());
      await c.setFiles([IMGD + 'roll_white_chikan.jpg']); await p.waitForTimeout(4000); await shot(p, 's15_cut_photo_match');
      await tap(p, p.getByText(/Use thaan T-006/).first(), 1200); await tap(p, p.getByText(/^Next/).filter({ visible: true }).first(), 1500);
      await tap(p, p.getByText('T-006/1').first(), 800); await tap(p, p.getByText(/Pick design for/).filter({ visible: true }).first(), 1200);
      await shot(p, 's16_cut_design_picker');
      await tap(p, p.getByRole('dialog').getByText(/104/).first(), 1000);
      await tap(p, p.getByText('T-006/2').first(), 800); await tap(p, p.getByText(/Pick design for/).filter({ visible: true }).first(), 1200);
      await tap(p, p.getByRole('dialog').getByText(/107/).first(), 1000);
      await tap(p, p.getByText(/Next: check/).filter({ visible: true }).first(), 1500); await shot(p, 's17_cut_check');
    });
    await sec('lots', async (p) => { await go(p, 'Register'); await shot(p, 's18_lot_register');
      await shot(p, 's19_lot_details', () => p.getByText('All details').filter({ visible: true }).first().click(), 1500); });
  },
  give: async () => {
    await sec('give', async (p) => {
      await tap(p, p.getByText('Give Maal to Karigar').first(), 1200); await tap(p, p.getByText('Salim').filter({ visible: true }).last(), 1200);
      await shot(p, 's20_give_choices');
      const cam = await chooser(p, () => p.getByText('Give bundles').click()); if (cam) await cam.setFiles([]); await p.waitForTimeout(600);
      const g = await chooser(p, () => p.getByText('Gallery', { exact: true }).filter({ visible: true }).first().click());
      await g.setFiles([IMGD + 'bundle_4.jpg', IMGD + 'bundle_5.jpg']); await p.waitForTimeout(2500);
      const bi = p.locator('input[type=number]'); await bi.nth(0).fill('6'); await bi.nth(1).fill('30'); await bi.nth(2).fill('3'); await bi.nth(3).fill('20'); await bi.nth(3).blur();
      await shot(p, 's21_give_bundles');
      await tap(p, p.getByText('Next: pick pattern'), 1200);
      const tiles = p.locator('button').filter({ hasText: /× \d+ = \d+ pcs/ });
      await tap(p, tiles.nth(0)); await tap(p, p.getByText(/Pick pattern for 1 photo/), 1000); await tap(p, p.getByRole('dialog').getByText(/104/).first(), 900);
      await tap(p, tiles.nth(1)); await tap(p, p.getByText(/Pick pattern for 1 photo/), 1000); await tap(p, p.getByRole('dialog').getByText(/No pattern for now/).first(), 900);
      await shot(p, 's22_give_patterns');
      await tap(p, p.getByText('Next: Check Entry'), 1500); await shot(p, 's23_give_check');
      await tap(p, p.getByText('Yes, Correct'), 2500); await shot(p, 's24_give_saved');
    });
  },
  take: async () => {
    await sec('take', async (p) => {
      await tap(p, p.getByText('Take Maal Back').first(), 1200); await tap(p, p.getByText('Pappu').filter({ visible: true }).last(), 1500);
      await shot(p, 's25_take_pick_lot');
      await tap(p, p.getByText(/Lot 6 · 104/).first(), 1500);
      const plus = p.getByRole('button', { name: /increase|\+|more/i }).filter({ visible: true }); if (await plus.count()) { for (let i = 0; i < 6; i++) await plus.first().click(); }
      await p.locator('input[type=number]').first().fill('51'); await p.locator('input[type=number]').first().blur();
      await shot(p, 's26_take_pieces');
      await tap(p, p.getByText(/^Next/).filter({ visible: true }).first(), 1500); await shot(p, 's27_take_check');
    });
  },
  workers: async () => {
    await sec('kar', async (p) => { await go(p, 'Karigars'); await shot(p, 's30_karigars'); await tap(p, p.getByText('Rohit').first(), 1300); await shot(p, 's28_karigar_page');
      await shot(p, 's28b_karigar_lots', () => scrollTo(p, 'Lots')); });
    await sec('mas', async (p) => { await go(p, 'Masters'); await tap(p, p.getByText('Ramesh Master').first(), 1300); await shot(p, 's29_master_page'); });
  },
  packing: async () => {
    await sec('pk', async (p) => { await tap(p, p.getByText('Packing Entry').first(), 1200); await tap(p, p.getByText('Vinod').filter({ visible: true }).last(), 1200); await shot(p, 's31_packing_form'); });
    await sec('pk2', async (p) => { await go(p, 'Register'); await tap(p, p.getByRole('button', { name: 'Packing', exact: true }).first(), 1000); await shot(p, 's32_packing_register'); });
  },
  pay: async () => {
    await sec('pay', async (p) => { await go(p, 'Payments'); await shot(p, 's33_payments'); await shot(p, 's34_pay_karigar', () => p.getByText('Rohit').filter({ visible: true }).first().click()); });
    await sec('pay2', async (p) => { await go(p, 'Payments'); await shot(p, 's35_pay_salary', () => p.getByText('Pooja').filter({ visible: true }).first().click()); });
  },
  att: async () => {
    await sec('att', async (p) => { await go(p, 'Staff'); await shot(p, 's36_attendance_today', () => scrollTo(p, 'Sonu').catch(() => {}));
      await p.evaluate(() => scrollTo(0, 0));
      await shot(p, 's40_staff_list', () => p.getByRole('button', { name: 'Staff', exact: true }).last().click());
      await shot(p, 's39_staff_calendar', () => p.getByText('Pooja').filter({ visible: true }).first().click()); });
    await sec('self', async (p) => { await shot(p, 's37_staff_self');
      await shot(p, 's38_staff_camera', () => p.getByText('Check in', { exact: true }).first().click(), 3500); }, 'st1',
      { mutate: (s) => { s['data:attendance'] = s['data:attendance'].filter((a) => !(a.staff_id === 'st1' && a.date === '2026-11-04')); return s; } });
  },
  insight: async () => {
    await sec('an', async (p) => { await go(p, 'Analytics'); await shot(p, 's41_analytics'); await shot(p, 's41b_analytics_people', () => scrollTo(p, 'Per Person')); });
    await sec('rec', async (p) => { await go(p, 'Records'); await shot(p, 's42_records'); });
    await sec('rep', async (p) => { await go(p, 'Reports'); await shot(p, 's43_reports'); await shot(p, 's44_hisaab_whatsapp', () => p.getByText('Rohit').filter({ visible: true }).first().click(), 2500); });
    await sec('pdf', async (p) => { await go(p, 'Reports'); await shot(p, 's45_pdf_preview', () => p.getByText('Preview PDF').first().click(), 5000); });
  },
  settings: async () => {
    await sec('set', async (p) => { await go(p, 'Settings'); await shot(p, 's46_settings_location');
      await shot(p, 's47_settings_salary', () => scrollTo(p, 'Staff Salary'), 600);
      await shot(p, 's48_settings_branches', () => scrollTo(p, 'Branches'), 600);
      await shot(p, 's48b_settings_telegram', () => scrollTo(p, 'Monthly Telegram report'), 600);
      await shot(p, 's49_settings_maint', () => scrollTo(p, 'Maintenance & Backups'), 600); });
    await sec('ppl', async (p) => { await go(p, 'Logins & People'); await shot(p, 's50_people'); await shot(p, 's51_add_person', () => p.getByText('Add Person').first().click()); });
  },
  extras: async () => {
    await sec('undo', async (p) => { await go(p, 'Register'); await tap(p, p.getByRole('button', { name: 'Packing', exact: true }).first(), 1000);
      await tap(p, p.getByText('Remove', { exact: true }).filter({ visible: true }).first(), 900);
      await tap(p, p.getByRole('button', { name: 'Remove', exact: true }).filter({ visible: true }).last(), 600); await shot(p, 's52_undo', null, 400); });
    await sec('offline', async (p) => { await p.context().setOffline(true); await p.waitForTimeout(800);
      await tap(p, p.getByText('Packing Entry').first(), 1200); await tap(p, p.getByText('Mohan').filter({ visible: true }).last(), 1200);
      await tap(p, p.getByText(/^Next/).filter({ visible: true }).first(), 1200); await tap(p, p.getByText('Yes, Correct'), 2000);
      const ok = p.getByText('OK', { exact: true }).filter({ visible: true }); if (await ok.count()) await tap(p, ok.first(), 1200);
      await shot(p, 's53_offline', null, 1500); });
    await sec('prof', async (p) => { await go(p, 'Profile'); await shot(p, 's54_profile'); });
  },
};
(async () => { const only = process.argv[2]; for (const [k, f] of Object.entries(G)) if (!only || only.split(',').includes(k)) { console.log('##', k); await f(); } })();
