import { Component, Input } from '@angular/core';
import { DateFactory } from '@infrastructure/date.factory';
import { Week } from '@heartsteps/weekly-survey/week.model';
import { ActivityPlanService } from './activity-plan.service';

@Component({
    selector: 'heartsteps-weekly-plan',
    templateUrl: 'weekly-plan.component.html',
    providers: [DateFactory],
    inputs: ['week']
})
export class WeeklyPlanComponent {

    private _week: Week;
    dates:Array<Date>

    constructor(
        private activityPlanService: ActivityPlanService
    ) {}

    @Input()
    set week(week:Week) {
        if(week) {
            this._week = week;
            this.dates = week.getDays();
            this.activityPlanService.getPlans(week.start, week.end);
        }
    }
}
