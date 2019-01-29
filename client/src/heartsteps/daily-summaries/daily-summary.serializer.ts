import { Injectable } from "@angular/core";
import { DailySummary } from "./daily-summary.model";
import * as moment from 'moment';

const dateFormat = 'YYYY-MM-DD';

@Injectable()
export class DailySummarySerializer {

    public serialize(summary: DailySummary): any {
        return {
            date: moment(summary.date).format(dateFormat),
            updated: summary.updated,
            moderateMinutes: summary.moderateMinutes,
            vigorousMinutes: summary.vigorousMinutes,
            minutes: summary.minutes,
            steps: summary.steps,
            miles: summary.miles
        }
    }

    public deserialize(data: any): DailySummary {
        const summary:DailySummary = new DailySummary();
        summary.date = moment(data.date, dateFormat).toDate();
        summary.updated = new Date();
        summary.moderateMinutes = data.moderateMinutes;
        summary.vigorousMinutes = data.vigorousMinutes;
        summary.minutes = data.minutes;
        summary.steps = data.steps;
        summary.miles = data.miles;
        return summary;
    }

}
