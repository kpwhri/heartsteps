import { Component, OnInit } from '@angular/core';
import { IonicPage } from 'ionic-angular';
import { ActivityLogService } from '@heartsteps/activity/activity-log.service';

@IonicPage()
@Component({
    selector: 'page-dashboard',
    templateUrl: 'dashboard.html',
    providers: [ActivityLogService]
})
export class DashboardPage {

    constructor() {
        
    }
}
