import * as moment from 'moment';

import { Injectable } from "@angular/core";
import { Subject } from 'rxjs';
import { ActivityLogService } from './activity-log.service';

const storageKey = 'activityLogs';

export class WeeklyProgressSummary {
    public goal: number;
    public completed: number;
}

@Injectable()
export class WeeklyProgressService {

    constructor(
        private activityLogService: ActivityLogService
    ){

    }

    getSummary(start:Date, end:Date): Subject<WeeklyProgressSummary> {
        const weekSummary = new Subject<WeeklyProgressSummary>();
        setTimeout(() => {
            const summary = new WeeklyProgressSummary();
            summary.goal = 150;
            summary.completed = 15
            weekSummary.next(summary)
        }, 3000)
        return weekSummary;
    }
}