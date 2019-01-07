import * as moment from 'moment';

export class ActivityPlan {

    public id:string;
    
    public type:string;
    public start:Date = new Date();
    public vigorous:boolean;
    public duration:number;
    public complete:boolean = false;

    constructor() {}

    isComplete() {
        return this.complete;
    }

    markComplete() {
        this.complete = true;
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