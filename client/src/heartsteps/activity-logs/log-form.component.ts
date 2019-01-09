import { Component, Output, EventEmitter, Input } from "@angular/core";
import { ActivityLog } from "./activity-log.model";
import { FormGroup, FormControl, Validators } from "@angular/forms";
import { DateFactory } from "@infrastructure/date.factory";
import * as moment from 'moment';
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
    public availableDates:Array<string> = [];

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
        this.availableDates = this.dateFactory.getCurrentWeek().map((date) => {
            return this.formatDate(date);
        })
    }

    private formatDate(date:Date):string {
        return moment(date).format('dddd, M/D');
    }

    private parseDate(str:string):Date {
        return moment(str, 'dddd, M/D').toDate();
    }

    private createForm() {
        this.form = new FormGroup({
            activity: new FormControl(this.activityLog.type, Validators.required),
            duration: new FormControl(this.activityLog.duration, Validators.required),
            date: new FormControl(this.activityLog.getStartDate(), Validators.required),
            time: new FormControl(this.activityLog.getStartTime(), Validators.required),
            vigorous: new FormControl(this.activityLog.vigorous, Validators.required)
        })
    }

    public save() {
        if(this.form.valid) {
            this.activityLog.type = this.form.value.activity;
            this.activityLog.duration = this.form.value.duration;
            this.activityLog.updateStartDate(this.parseDate(this.form.value.date));
            this.activityLog.updateStartTime(this.form.value.time);
            
            this.activityLogService.save(this.activityLog)
            .then(() => {
                this.saved.emit();
            })
        } else {
            // show error messages.
        }
    }

    public delete() {
        this.activityLogService.delete(this.activityLog)
        .then(() => {
            this.saved.emit();
        });
    }

}
