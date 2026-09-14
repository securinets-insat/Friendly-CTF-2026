const express = require('express');
const{ chromium, errors } = require('playwright');

const PORT = process.env.PORT || 3000;
const app = express();
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
APP_URL = process.env.APP_URL || 'http://note-app:5014';
ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'admin123';
FLAG=process.env.FLAG || 'Securinets{redacted}';

let visiting = false;
app.post('/visit', async (req, res) => {
    const user_id = req.body.user_id;
    if (!user_id) {
        return res.status(400).send('User ID is required');
    }
    if (visiting) {
        return res.status(400).send('Bot is already visiting another user. Please try again later.');
    }
    visiting = true;

    const url = `${APP_URL}/user/${user_id}/notes`;
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
        console.log(`Bot logged in as admin `);
        res.send('Notes visited by bot');
        try {
            await page.locator('#view-btn').click();
            await page.waitForLoadState('networkidle');
            console.log(`Bot visited notes for user ${user_id}`);
        } catch (error) {
            if (error instanceof errors.TimeoutError) {
            const profileUrl = `${APP_URL}/user/${user_id}/profile`;
            await page.goto(profileUrl, {
                waitUntil: 'networkidle',
                timeout: 10000
            });
            console.log(`Bot visited profile for user ${user_id}`);
            } else {
                throw error;
            }

        }
        finally {
            await page.waitForTimeout(3000);
        }
        
    } catch (error) {
        console.error('Error visiting notes:', error);
        if (!res.headersSent) {
          res.status(500).send('Error visiting notes');
      }

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