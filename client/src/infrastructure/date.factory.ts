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

    public getDateRange(start:Date, end:Date): Array<Date> {
        const dates: Array<Date> = [];
        let _date = moment(start);
        while(_date.isSameOrBefore(moment(end))) {
            dates.push(_date.toDate());
            _date = _date.add(1, 'days');
        }
        return dates;
    }

    public getWeek(date:Date):Array<Date> {
        const day:number = date.getDay();
        let monday: Date;
        if(day === 0) {
            monday = moment(date).subtract(6, 'days').toDate();
        } else {
            monday = moment(date).subtract(day - 1, 'days').toDate();
        }
        const sunday:Date = moment(monday).add(6, 'days').toDate();
        return this.getDateRange(monday, sunday);
    }

    public getCurrentWeek():Array<Date> {
        return this.getWeek(new Date());
    }

    public getPreviousWeek():Array<Date> {
        const dateLastWeek = moment().subtract(7, 'days').toDate();
        return this.getWeek(dateLastWeek);
    }

    public getNextWeek():Array<Date> {
        const dateLastWeek = moment().add(7, 'days').toDate();
        return this.getWeek(dateLastWeek);
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

    public getDatesFrom(start: Date): Array<Date> {
        return this.getDateRange(start, new Date());
    }
}