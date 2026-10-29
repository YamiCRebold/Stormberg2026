const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({executablePath: '/opt/pw-browsers/chromium'}).catch(async()=>await chromium.launch());
  const p = await b.newPage({viewport:{width:1280,height:900}});
  const errs=[]; p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
  await p.goto('file://'+process.argv[2]); await p.waitForTimeout(1500);
  console.log('takeaway:', (await p.textContent('#takeaway')).slice(0,250));
  await p.screenshot({path: process.argv[3]+'/s_resumen.png', fullPage:false});
  for (const t of ['tab-begbarker','tab-ayoba','tab-acciones']) { await p.click('#'+t); await p.waitForTimeout(600); await p.screenshot({path: process.argv[3]+'/s_'+t+'.png'}); }
  console.log('errors:', errs.slice(0,5));
  await b.close();
})();
