import * as moment from 'moment';

export class ActivityLog {

    public id:string;
    
    public type:string;
    public start:Date;
    public end:Date;

    public vigorousMinutes:number;
    public moderateMinutes:number;
    public totalMinutes: number;

    constructor() {}

    private formatTime(date:Date):string {
        return moment(date).format('h:mm a')
    }

    public formatStartTime():string {
        return this.formatTime(this.start);
    }

    public formatEndTime():string {
        return this.formatTime(this.end);
    }

}