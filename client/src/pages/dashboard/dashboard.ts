import { Component, ViewChild, ElementRef } from '@angular/core';
import { IonicPage } from 'ionic-angular';
import { ActivityLogService } from '@heartsteps/activity/activity-log.service';
import { DateFactory } from '@infrastructure/date.factory';

@IonicPage()
@Component({
    selector: 'page-dashboard',
    templateUrl: 'dashboard.html',
    providers: [
        ActivityLogService,
        DateFactory
    ]
})
export class DashboardPage {
    @ViewChild('chart') chart: ElementRef;

    public remainingDaysOfWeek: Array<Date>;

    constructor(
        private dateFactory:DateFactory
    ) {
        this.remainingDaysOfWeek = this.dateFactory.getRemainingDaysInWeek();
    }
}
