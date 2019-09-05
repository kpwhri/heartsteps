import { Injectable } from "@angular/core";
import { DailySummary } from "./daily-summary.model";
import * as moment from 'moment';

const dateFormat = 'YYYY-MM-DD';

@Injectable()
export class DailySummarySerializer {

    public formatDate(date: Date): string {
        return moment(date).format(dateFormat);
    }

    public parseDate(dateString: string): Date {
        return moment(dateString, dateFormat).toDate();
    }

    public serialize(summary: DailySummary): any {
        return {
            date: this.formatDate(summary.date),
            updated: summary.updated,
            moderateMinutes: summary.moderateMinutes,
            vigorousMinutes: summary.vigorousMinutes,
            minutes: summary.minutes,
            steps: summary.steps,
            miles: summary.miles,
            activitiesCompleted: summary.activitiesCompleted
        }
    }

    public deserialize(data: any): DailySummary {
        const summary:DailySummary = new DailySummary();
        summary.date = this.parseDate(data.date);
        summary.updated = new Date(data.updated);
        summary.moderateMinutes = data.moderateMinutes ? data.moderateMinutes : 0;
        summary.vigorousMinutes = data.vigorousMinutes ? data.vigorousMinutes : 0;
        summary.minutes = data.minutes ? data.minutes : 0;
        summary.steps = data.steps ? data.steps : 0;
        summary.miles = data.miles ? data.miles : 0;
        summary.activitiesCompleted = data.activitiesCompleted ? data.activitiesCompleted : 0;
        return summary;
    }

}
