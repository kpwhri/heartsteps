import { Component, OnInit, Input } from '@angular/core';
import * as moment from 'moment';

@Component({
    selector: 'activity-day-plan',
    templateUrl: './day-plan.component.html',
    inputs: ['date']
})
export class DayPlanComponent implements OnInit {

    @Input() date:Date
    dateFormatted:string

    constructor() {}

    ngOnInit(){
        console.log(this.date)
        this.dateFormatted = moment(this.date).format("dddd, M/D")
    }
}
