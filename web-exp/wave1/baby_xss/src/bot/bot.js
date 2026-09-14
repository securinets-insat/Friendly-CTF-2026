const express = require('express');
const{ chromium } = require('playwright');

const PORT = process.env.PORT || 3000;
const app = express();
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
APP_URL = process.env.APP_URL || 'http://report-app:5009';
ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'admin123';
FLAG=process.env.FLAG || 'Securinets{redacted}';

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
        await page.goto(`${APP_URL}/login`);
        await page.fill('input[name="username"]', 'admin');
        await page.fill('input[name="password"]', ADMIN_PASSWORD);
        await page.click('button[type="submit"]');
        await page.waitForLoadState('networkidle');
        await page.goto(url, {
            waitUntil: 'networkidle',
            timeout: 10000
        });
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