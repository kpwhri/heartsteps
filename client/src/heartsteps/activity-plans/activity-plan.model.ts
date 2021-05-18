// tslint:disable-next-line:no-unused-variable
import * as moment from 'moment';
import { ActivityLog } from '@heartsteps/activity-logs/activity-log.model';

export class ActivityPlan extends ActivityLog {

    public id:string;

    public date:Date = new Date();
    public timeOfDay:string;
    
    public type:string;
    public vigorous:boolean = false;
    public duration:number;
    public complete:boolean = false;

    public activityLogId: string;

    isComplete() {
        return this.complete;
    }

}