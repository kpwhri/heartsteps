import * as moment from 'moment';

export class DailySummary {
    public date: Date;
    public updated: Date;

    public moderateMinutes: number = 0;
    public vigorousMinutes: number = 0;
    public minutes: number = 0;

    public steps: number = 0;
    public miles: number = 0;

    public activitiesCompleted: number = 0;

    public isToday():boolean {
        return this.isDate(new Date());
    }

    public isDate(date: Date):boolean {
        return moment(date).isSame(this.date, 'day');
    }
}