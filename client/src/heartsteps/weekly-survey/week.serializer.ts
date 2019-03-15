import { Injectable } from "@angular/core";
import * as moment from 'moment';
import { Week } from "./week.model";

const dateFormat = 'YYYY-MM-DD';

@Injectable()
export class WeekSerializer {

    public serialize(week: Week): any {
        const serialized:any = {
            id: week.id,
            start: moment(week.start).format(dateFormat),
            end: moment(week.end).format(dateFormat),
        };
        if(week.goal !== undefined) {
            serialized['goal'] = week.goal;
        }
        if(week.confidence !== undefined) {
            serialized['confidence'] = week.confidence;
        }
        return serialized;
    }

    public deserialize(data: any): Week {
        const week = new Week();
        week.id = data.id;
        week.start = moment(data.start, dateFormat).toDate();
        week.end = moment(data.end, dateFormat).endOf('day').toDate();
        if(data.goal) week.goal = data.goal;
        if(data.confidence) week.confidence = data.confidence;
        return week;
    }

}
