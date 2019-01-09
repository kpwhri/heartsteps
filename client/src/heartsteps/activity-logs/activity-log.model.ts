import * as moment from 'moment';
import { ActivityLogService } from './activity-log.service';

export class ActivityLog {

    public id:string;
    
    public type:string;
    public start:Date;
    public duration: number;

    public vigorous:boolean;
    public earnedMinutes: number;

    constructor(
        private activityLogService: ActivityLogService
    ) {}

    public save() {
        return this.activityLogService.save(this);
    }

    private formatTime(date:Date):string {
        return moment(date).format('h:mm a')
    }

    public formatStartTime():string {
        return this.formatTime(this.start);
    }

    public formatEndTime():string {
        // Add duration....
        return this.formatTime(this.start);
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