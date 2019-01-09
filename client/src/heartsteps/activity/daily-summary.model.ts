import * as moment from 'moment';

export class DailySummary {
    public date: Date;
    public updated: Date;

    public moderateMinutes: number = 0;
    public vigorousMinutes: number = 0;
    public totalMinutes: number = 0;

    public totalSteps: number = 0;
    public totalMiles: number = 0;

    public isToday():boolean {
        return moment(new Date()).isSame(this.date, 'day');
    }
}