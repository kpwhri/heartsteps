import { Component, OnInit } from '@angular/core';
import { AnalyticsService } from '@infrastructure/heartsteps/analytics.service';

@Component({
    templateUrl: './website.component.html'
})
export class HeartstepsWebsite implements OnInit {

    constructor(
        private analyticsService: AnalyticsService
    ) {}

    public ngOnInit() {
        this.analyticsService.setup();
    }
    
}
