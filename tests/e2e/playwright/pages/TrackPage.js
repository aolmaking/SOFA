// tests/e2e/pages/TrackPage.js
export class TrackPage {
    constructor(page) {
        this.page = page;
        this.statusBadge = page.locator('[data-testid="status-badge"]');
        this.timelineSteps = page.locator('[data-testid="timeline-step"]');
    }

    async goto(orderId) {
        await this.page.goto(`http://localhost:5000/track.html?order=${orderId}`);
    }

    async getStatusText() {
        return await this.statusBadge.textContent();
    }

    async getCompletedSteps() {
        const steps = await this.timelineSteps.all();
        let count = 0;
        for (const step of steps) {
            const cls = await step.getAttribute('class');
            if (cls && cls.includes('completed')) count++;
        }
        return count;
    }
}