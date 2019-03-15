import { Component, Input, ElementRef, Renderer2, OnInit } from '@angular/core';
import { ActivityPlan } from '@heartsteps/activity-plans/activity-plan.model';
import { ActivityTypeService } from '@heartsteps/activity-types/activity-type.service';
import { Router } from '@angular/router';

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
        this.timeOfDay = this.plan.timeOfDay;
        this.duration = String(this.plan.duration);
        this.complete = this.plan.complete;
        if(this.complete) {
            this.renderer.addClass(this.element.nativeElement, 'is-complete');
        }

        this.renderer.listen(this.element.nativeElement, 'click', (event) => {
            event.preventDefault();
            if(event.target.nodeName === "BUTTON") {
                this.router.navigate(['plans', this.plan.id, 'complete']);
            } else {
                this.router.navigate(['plans', this.plan.id]);
            }
        })
    }
}
