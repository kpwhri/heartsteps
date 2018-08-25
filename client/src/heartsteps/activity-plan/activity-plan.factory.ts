import { Injectable } from "@angular/core";
import * as moment from 'moment';


@Injectable()
export class ActivityPlanFactory {

    constructor(){}

    getCurrentWeek():Array<Date> {
        let week:Array<Date> = []

        let today:any = new Date()

        const day:number = today.getDay()
        for(let i=0; i < 7; i++) {
            let offset:number = day - i
            let momentDate = moment(today)
            if(offset > 0) {
                momentDate.subtract(offset, 'days')
            }
            if(offset < 0) {
                momentDate.add(Math.abs(offset), 'days')
            }
            let newDate = new Date(momentDate.year(), momentDate.month(), momentDate.date())
            week.push(newDate)
        }
        return week
    }

}