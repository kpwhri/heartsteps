import * as moment from 'moment';

export class Activity {

    public id:string;
    
    public type:string;
    public start:Date;
    public vigorous:boolean;
    public duration:number;
    public enjoyed: number;
    private complete:boolean;

    constructor(obj:any) {
        this.id = obj.id;
        this.type = obj.type;
        this.duration = obj.duration;
        this.vigorous = obj.vigorous || false;
        this.complete = obj.complete || false;

        if(obj.start) {
            const localMoment = moment.utc(obj.start).local();
            this.start = new Date(localMoment.toString());
        } else {
            this.start = new Date();
        }
    }

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

    serialize():any {
        let datestring:string = this.start.toISOString();
        let serialized: any = {
            type: this.type,
            start: datestring,
            duration: this.duration,
            vigorous: this.vigorous
        };
        if (this.complete) {
            serialized.complete = true;
        }
        if (this.enjoyed) {
            serialized.enjoyed = this.enjoyed;
        }
        return serialized;
    }
}