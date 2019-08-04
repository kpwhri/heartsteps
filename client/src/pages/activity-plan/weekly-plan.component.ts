import { Component, Input } from '@angular/core';
import { DateFactory } from '@infrastructure/date.factory';
import { Week } from '@heartsteps/weekly-survey/week.model';
import { ActivityPlanService } from '@heartsteps/activity-plans/activity-plan.service';
import { ParticipantInformationService } from '@heartsteps/participants/participant-information.service';

@Component({
    selector: 'heartsteps-weekly-plan',
    templateUrl: 'weekly-plan.component.html',
    providers: [DateFactory],
    inputs: ['week']
})
export class WeeklyPlanComponent {

    public dates:Array<Date>

    constructor(
        private activityPlanService: ActivityPlanService,
        private participantInformationService: ParticipantInformationService
    ) {}

    @Input()
    set week(week:Week) {
        if(week) {
            this.participantInformationService.getDateEnrolled()
            .then((dateEnrolled) => {
                this.dates = week.getDays().filter((date) => {
                    if(date >= dateEnrolled) {
                        return true;
                    } else {
                        return false;
                    }
                });
                this.activityPlanService.getPlans(week.start, week.end);
            })
        }
    }
}
