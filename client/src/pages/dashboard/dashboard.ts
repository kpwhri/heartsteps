import { Component } from '@angular/core';
import { IonicPage, NavController } from 'ionic-angular';
import { DateFactory } from '@heartsteps/date.factory';

@IonicPage()
@Component({
    selector: 'page-dashboard',
    templateUrl: 'dashboard.html'
})
export class DashboardPage {

    private remainingPlans: Array<any>
    private dates: Array<Date>

    constructor(
        private navCtrl: NavController,
        private dateFactory: DateFactory
    ) {
        this.dates = dateFactory.getRemainingDaysInWeek()
    }
}
