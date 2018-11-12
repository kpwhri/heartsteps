import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { IonicPage } from 'ionic-angular';
import { ActivityLogService } from '@heartsteps/activity/activity-log.service';

@IonicPage()
@Component({
    selector: 'page-dashboard',
    templateUrl: 'dashboard.html',
    providers: [ActivityLogService]
})
export class DashboardPage {
    @ViewChild('chart') chart: ElementRef;

    constructor() {
        
    }
}
