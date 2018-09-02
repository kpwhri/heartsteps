import { Component } from '@angular/core';
import { IonicPage } from 'ionic-angular';
import { ResourceLibraryPage } from '@pages/resource-library/resource-library';
import { DashboardPage } from '@pages/dashboard/dashboard';
import { PlanPage } from '@pages/activity-plan/plan.page';
import { ActivityLogPage } from '@pages/activity-log/activity-log';

@IonicPage()
@Component({
    selector: 'page-home',
    templateUrl: 'home.html'
})
export class HomePage {

    dashboard:any
    plan:any
    activityLog:any
    resourceLibrary: any

    constructor() {
        this.dashboard = DashboardPage
        this.plan = PlanPage
        this.activityLog = ActivityLogPage
        this.resourceLibrary = ResourceLibraryPage
    }
}
