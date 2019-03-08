import { WeekService } from "./week.service";
import * as moment from 'moment';

export class Week {
    id:string;
    start:Date;
    end:Date;
    goal:number;
    confidence: number;

    constructor(){}

    getDays():Array<Date> {
        const days:Array<Date> = [];
        let _date:Date = this.start;
        while(_date <= this.end) {
            days.push(_date);
            _date = moment(_date).add(1, 'days').toDate();
        }
        return days;
    }
}
