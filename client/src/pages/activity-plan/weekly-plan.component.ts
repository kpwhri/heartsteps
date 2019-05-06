import { Component, Input } from '@angular/core';
import { DateFactory } from '@infrastructure/date.factory';
import { Week } from '@heartsteps/weekly-survey/week.model';
import { ActivityPlanService } from '@heartsteps/activity-plans/activity-plan.service';

@Component({
    selector: 'heartsteps-weekly-plan',
    templateUrl: 'weekly-plan.component.html',
    providers: [DateFactory],
    inputs: ['week']
})
export class WeeklyPlanComponent {

    public dates:Array<Date>

    constructor(
        private activityPlanService: ActivityPlanService
    ) {}

    @Input()
    set week(week:Week) {
        if(week) {
            this.dates = week.getDays();
            this.activityPlanService.getPlans(week.start, week.end);
        }
    }
}
