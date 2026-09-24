const express = require('express');
const{ chromium } = require('playwright');

const PORT = process.env.PORT || 3000;
const NAVIGATION_TIMEOUT_MS = 10_000;
const ACTION_TIMEOUT_MS = 5_000;
const XSS_EXECUTION_WINDOW_MS = 1_500;
const app = express();
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
const APP_URL = process.env.APP_URL || 'http://report-app:5009';
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'admin123';
const FLAG = process.env.FLAG || 'Securinets{redacted}';

let visiting = false;
app.post('/visit', async (req, res) => {
    const reportId = req.body.report_id;
    if (!reportId) {
        return res.status(400).send('Report ID is required');
    }

    if (visiting) {
        return res.status(400).send('Bot is already visiting a report');
    }
    visiting = true;

    const url = `${APP_URL}/report/${reportId}`;
    let browser;
    try {
        browser = await chromium.launch({
            args: ['--no-sandbox', '--disable-setuid-sandbox'],
            timeout: NAVIGATION_TIMEOUT_MS,
        });
        const context = await browser.newContext();
        await context.addCookies([
            {
                name: 'flag',
                value: FLAG,
                url: APP_URL
            }
        ]);
        const page = await context.newPage();
        page.setDefaultTimeout(ACTION_TIMEOUT_MS);
        page.setDefaultNavigationTimeout(NAVIGATION_TIMEOUT_MS);

        await page.goto(`${APP_URL}/login`, { waitUntil: 'domcontentloaded' });
        await page.fill('input[name="username"]', 'admin');
        await page.fill('input[name="password"]', ADMIN_PASSWORD);
        await Promise.all([
            page.waitForURL('**/reports', { waitUntil: 'domcontentloaded' }),
            page.click('button[type="submit"]'),
        ]);
        await page.goto(url, {
            waitUntil: 'domcontentloaded',
        });
        await page.waitForTimeout(XSS_EXECUTION_WINDOW_MS);
        res.send('Report visited by bot');
        console.log(`Bot visited report ${reportId}`);
    } catch (error) {
        console.error('Error visiting report:', error);
        res.status(500).send('Error visiting report');
    } finally {
        if (browser) {
            await browser.close();
        }
        visiting = false;
    }
});

app.listen(PORT, () => {
    console.log(`Bot server is running on port ${PORT}`);
});
