import { Component, Input, ElementRef, Renderer2, OnInit } from '@angular/core';
import { ActivityPlan } from '@heartsteps/activity-plans/activity-plan.model';
import { ActivityTypeService } from '@heartsteps/activity-types/activity-type.service';
import { Router } from '@angular/router';
import { DailyTimeService, DailyTime } from '@heartsteps/daily-times/daily-times.service';

@Component({
    selector: 'heartsteps-activity-plan',
    templateUrl: './plan.component.html',
    inputs: ['plan']
})
export class PlanComponent implements OnInit {

    @Input() plan:ActivityPlan

    public activityType:string;
    public activityLevel:string;

    public timeOfDay:string;

    public complete: boolean;
    public duration: string;

    constructor(
        private activityTypeService: ActivityTypeService,
        private dailyTimeService: DailyTimeService,
        private element:ElementRef,
        private renderer:Renderer2,
        private router: Router
    ) {}

    ngOnInit() {
        this.activityTypeService.get(this.plan.type)
        .then((activityType) => {
            this.activityType = activityType.title;
            this.renderer.addClass(this.element.nativeElement, 'activity-type-'+activityType.name);
        });
        
        if(this.plan.vigorous) {
            this.activityLevel = "vigorous";
        } else {
            this.activityLevel = "moderate";
        }

        let timeOfDay: DailyTime = this.dailyTimeService.times.value.find((value) => {
            return value.key === this.plan.timeOfDay;
        });
        this.timeOfDay = timeOfDay.name;
        
        if(this.plan.complete) {
            this.duration = String(this.plan.duration) + ' minutes complete';
        } else {
            this.duration = String(this.plan.duration) + ' minutes planned';
        }
        
        this.complete = this.plan.complete;
        if(this.complete) {
            this.renderer.addClass(this.element.nativeElement, 'is-complete');
        }

        this.renderer.listen(this.element.nativeElement, 'click', (event) => {
            event.preventDefault();
            if(event.target.nodeName === "BUTTON") {
                this.router.navigate([{outlets: {
                    modal: ['plans', this.plan.id].join('/')
                }}]);
            } else {
                this.router.navigate([{outlets: {
                    modal: ['plans', this.plan.id, 'complete'].join('/')
                }}]);
            }
        })
    }
}
