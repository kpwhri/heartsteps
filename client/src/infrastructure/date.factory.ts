import { Injectable } from "@angular/core";
import * as moment from 'moment';

@Injectable()
export class DateFactory {

    constructor(){}

    isSameDay(a:Date, b:Date) {
        return moment(a).isSame(b, 'day');
    }

    formatDate(date:Date):String {
        return moment(date).format('YYYY-MM-DD');
    }

    parseDate(date:string):Date {
        return moment(date, 'YYYY-MM-DD').toDate();
    }

    formatTime(time:Date):String {
        return moment(time).format('H:mm');
    }

    parseTime(time:string):Date {
        return moment(time, 'H:mm').toDate();
    }

    public getWeek(date:Date):Array<Date> {
        let week:Array<Date> = []

        const day:number = date.getDay();
        let monday: Date;
        if(day === 0) {
            monday = moment(date).subtract(6, 'days').toDate();
        } else {
            monday = moment(date).subtract(day - 1, 'days').toDate();
        }

        for(let i=0; i <= 6; i++) {
            const momentDate = moment(monday);
            momentDate.add(i, 'days');
            let newDate = new Date(momentDate.year(), momentDate.month(), momentDate.date())
            week.push(newDate)
        }
        return week
    }

    public getCurrentWeek():Array<Date> {
        return this.getWeek(new Date());
    }

    public getRemainingDaysInWeek():Array<Date> {
        const now:Date = new Date();
        const today:Date = new Date(now.getFullYear(), now.getMonth(), now.getDate());

        let remainingDays:Array<Date> = [];
        this.getCurrentWeek().forEach((day) => {
            if(day >= today) {
                remainingDays.push(day);
            }
        });
        return remainingDays;
    }
}