import { Component, Output, EventEmitter, Input } from "@angular/core";
import { ActivityLog } from "./activity-log.model";
import { FormGroup, FormControl, Validators } from "@angular/forms";
import { DateFactory } from "@infrastructure/date.factory";
import { ActivityLogService } from "./activity-log.service";

@Component({
    selector: 'heartsteps-activity-log-form',
    templateUrl: './log-form.component.html',
    inputs: ['activity-log'],
    providers: [DateFactory]
})
export class LogFormComponent {

    public activityLog:ActivityLog
    public form:FormGroup
    public availableDates:Array<Date> = [];

    @Output('saved') saved:EventEmitter<boolean> = new EventEmitter();

    constructor(
        private dateFactory:DateFactory,
        private activityLogService: ActivityLogService
    ){}

    @Input('activity-log')
    set asetActivityLog(log:ActivityLog) {
        if (log) {
            this.activityLog = log;
            this.setAvailableDates();
            this.createForm();
        }
    }

    private setAvailableDates() {
        this.availableDates = this.dateFactory.getCurrentWeek();
    }

    private createForm() {
        this.form = new FormGroup({
            activity: new FormControl(this.activityLog.type, Validators.required),
            duration: new FormControl(this.activityLog.duration, Validators.required),
            date: new FormControl(this.activityLog.start, Validators.required),
            time: new FormControl(this.activityLog.start, Validators.required),
            vigorous: new FormControl(this.activityLog.vigorous, Validators.required)
        })
    }

    public save() {
        this.activityLog.type = this.form.value.activity;
        this.activityLog.duration = this.form.value.duration;
        this.activityLog.vigorous = this.form.value.vigorous;
        this.activityLog.start.setFullYear(this.form.value.date.getFullYear());
        this.activityLog.start.setMonth(this.form.value.date.getMonth());
        this.activityLog.start.setDate(this.form.value.date.getDate());
        this.activityLog.start.setHours(this.form.value.time.getHours());
        this.activityLog.start.setMinutes(this.form.value.time.getMinutes());
        
        this.activityLogService.save(this.activityLog)
        .then(() => {
            this.saved.emit();
        });
    }

    public delete() {
        this.activityLogService.delete(this.activityLog)
        .then(() => {
            this.saved.emit();
        });
    }

}
