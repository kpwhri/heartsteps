import { Component, Input, Output, EventEmitter } from "@angular/core";
import { ActivityLog } from "@heartsteps/activity-logs/activity-log.model";
import { FormGroup, FormControl, Validators } from "@angular/forms";
import { DateFactory } from "@infrastructure/date.factory";
import { SelectOption } from "@infrastructure/dialogs/select-dialog.controller";


@Component({
    selector: 'activity-log-form',
    templateUrl: './activity-log-form.component.html'
})
export class ActivityLogFormComponent {

    public form: FormGroup;
    public availableDates: Array<Date>;
    public effortOptions: Array<SelectOption> = [
        {
            name: "No effort",
            value: 0
        },
        {
            name: "Some effort",
            value: 0.25
        },
        {
            name: "Moderate effort",
            value: 0.5
        },
        {
            name: "Significant effort",
            value: 0.75
        },
        {
            name: "Maximum effort",
            value: 1
        }
    ]

    @Output('onSubmit') submitted: EventEmitter<ActivityLog> = new EventEmitter();

    constructor(
        private dateFactory: DateFactory
    ) {}

    @Input('activityLog')
    set setActivityLog(activityLog: ActivityLog) {
        if(activityLog) {
            this.updateForm(activityLog);
        }
    }

    private updateForm(activityLog: ActivityLog) {
        this.availableDates = this.dateFactory.getWeek(activityLog.start);

        this.form = new FormGroup({
            activity: new FormControl(activityLog.type, Validators.required),
            duration: new FormControl(activityLog.duration || 30, Validators.required),
            date: new FormControl(activityLog.start, Validators.required),
            time: new FormControl(activityLog.start, Validators.required),
            vigorous: new FormControl(activityLog.vigorous),
            enjoyed: new FormControl(activityLog.enjoyed),
            effort: new FormControl(activityLog.effort)
        })
    }

    public submit() {
        const values:any = Object.assign({}, this.form.value);

        const activityLog = new ActivityLog();
        activityLog.type = values.activity;
        activityLog.duration = values.duration;
        activityLog.vigorous = values.vigorous;
        activityLog.effort = values.effort;
        activityLog.enjoyed = values.enjoyed;

        const updatedStart:Date = new Date();
        updatedStart.setFullYear(values.date.getFullYear());
        updatedStart.setMonth(values.date.getMonth());
        updatedStart.setDate(values.date.getDate());
        updatedStart.setHours(values.time.getHours());
        updatedStart.setMinutes(values.time.getMinutes());
        activityLog.start = updatedStart;

        this.submitted.emit(activityLog);
    }

}

