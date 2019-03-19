import { Component, OnInit, Input, ElementRef, Renderer2 } from "@angular/core";
import { ActivityLog } from "./activity-log.model";
import { ActivityTypeService } from "@heartsteps/activity-types/activity-type.service";


@Component({
    'selector': 'heartsteps-activity-log',
    templateUrl: './activity-log.component.html',
    inputs: ['activityLog']
})
export class ActivityLogComponent implements OnInit {
    @Input() activityLog:ActivityLog;

    type:string;
    activityLevel:string;
    start:string;
    end:string;

    earnedMinutes:number;

    constructor(
        private activityTypeService: ActivityTypeService,
        private element: ElementRef,
        private renderer: Renderer2
    ) {}

    ngOnInit() {
        if(this.activityLog.type) {
            this.activityTypeService.get(this.activityLog.type)
            .then((activityType) => {
                this.type = activityType.title;
                this.setActivityTypeClass(activityType.name);
            })
        }

        this.start = this.activityLog.formatStartTime();
        this.end = this.activityLog.formatEndTime();
        this.activityLevel = this.activityLog.vigorous ? 'vigorous': 'moderate';
        this.earnedMinutes = this.activityLog.earnedMinutes;

    }

    private setActivityTypeClass(type:string) {
        this.renderer.addClass(this.element.nativeElement, 'activity-type-'+type);
    }
}