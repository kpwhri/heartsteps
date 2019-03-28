import { Component, OnInit } from "@angular/core";
import { DateFactory } from "@infrastructure/date.factory";
import * as moment from 'moment';


@Component({
    templateUrl: './stats.page.html'
})
export class StatsPage implements OnInit {

    public days: Array<Date>

    constructor(
        private dateFactory: DateFactory
    ){
        this.days = [];
        const today = new Date();
        this.days.push(today);
        this.dateFactory.getCurrentWeek().reverse().forEach((day) => {
            if(moment(day).isBefore(today, 'day')) {
                this.days.push(day);
            }
        });
        const dayLastWeek: Date = moment().subtract(7, 'days').toDate();
        this.dateFactory.getWeek(dayLastWeek).reverse().forEach((day) => {
            this.days.push(day);
        });
    }

    ngOnInit() {

    }
    
}
