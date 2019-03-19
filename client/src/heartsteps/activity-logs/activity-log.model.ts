import * as moment from 'moment';

export class ActivityLog {

    public id:string;
    
    public type:string;
    public start:Date;
    public duration: number;

    public vigorous:boolean;
    public earnedMinutes: number;

    public enjoyed: number;
    public effort: number;

    constructor() {}

    public isToday() {
        return moment(this.start).isSame(new Date(), 'day');
    }

    private formatTime(date:Date):string {
        return moment(date).format('h:mm a')
    }

    public formatStartTime():string {
        return this.formatTime(this.start);
    }

    public formatEndTime():string {
        const endTime:Date = moment(this.start).add(this.duration, 'minutes').toDate();
        return this.formatTime(endTime);
    }

    getStartTime():string {
        return moment(this.start).format("HH:mm")
    }

    updateStartTime(time:string) {
        this.start.setHours(Number(time.split(":")[0]));
        this.start.setMinutes(Number(time.split(":")[1]));
    }

    getStartDate():string {
        return moment(this.start).format("dddd, M/D")
    }

    updateStartDate(date:Date) {
        this.start.setFullYear(date.getFullYear());
        this.start.setMonth(date.getMonth());
        this.start.setDate(date.getDate());
    }

}