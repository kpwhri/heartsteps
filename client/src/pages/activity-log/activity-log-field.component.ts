import { Component, forwardRef, ElementRef, Renderer2 } from "@angular/core";
import { AbstractField } from "@infrastructure/form/abstract-field";
import { NG_VALUE_ACCESSOR, FormGroup, FormControl, Validators, FormGroupDirective } from "@angular/forms";
import { Subscription } from "rxjs";
import { DateFactory } from "@infrastructure/date.factory";
import { ActivityLog } from "@heartsteps/activity-logs/activity-log.model";

@Component({
    selector: 'activity-log-field',
    templateUrl: './activity-log-field.component.html',
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            multi: true,
            useExisting: forwardRef(() => ActivityLogFieldComponent)
        }
    ]
})
export class ActivityLogFieldComponent extends AbstractField {
    public form: FormGroup;
    public availableDates: Array<Date>;

    private activityLog: ActivityLog;

    private ngFormSubmitSubscription:Subscription;
    private formSubscription:Subscription;
    private formStatusSubscription: Subscription;

    constructor(
        formGroup: FormGroupDirective,
        element: ElementRef,
        renderer: Renderer2,
        private dateFactory: DateFactory
    ) {
        super(formGroup, element, renderer)
    }

    public writeValue(activityLog:ActivityLog) {
        if(activityLog) {
            this.activityLog = activityLog;
            this.initializeForm();
        }

    }

    private initializeForm() {
        this.availableDates = this.dateFactory.getWeek(this.activityLog.start);

        this.form = new FormGroup({
            activity: new FormControl(this.activityLog.type, Validators.required),
            duration: new FormControl(this.activityLog.duration || 30, Validators.required),
            date: new FormControl(this.activityLog.start, Validators.required),
            time: new FormControl(this.activityLog.start, Validators.required),
            vigorous: new FormControl(this.activityLog.vigorous, Validators.required)
        });

        this.ngFormSubmitSubscription = this.formGroup.ngSubmit
        .subscribe(() => {
            Object.keys(this.form.controls).forEach((key) => {
                this.form.controls[key].markAsDirty();
                this.form.controls[key].updateValueAndValidity();
            });
        });

        setTimeout(() => {
            this.updateFormErrors();
        }, 100);

        this.formStatusSubscription = this.form.statusChanges.subscribe(() => {
            this.updateFormErrors();
            this.updateFormTouched();
        });

        this.formSubscription = this.form.valueChanges.subscribe((values:any) => {
            this.updateLog();
        });
    }

    private updateFormErrors() {
        if(this.form.valid) {
            this.control.setErrors(null);
        } else {
            this.control.setErrors({
                'invalid': true
            });
        }
    }

    private updateFormTouched() {
        if(this.form.touched) {
            this.control.markAsTouched();
        } else {
            this.control.markAsUntouched();
        }
    }

    private updateLog() {
        const values:any = Object.assign({}, this.form.value);

        const log = new ActivityLog();
        log.id = this.activityLog.id;
        log.type = values.activity;
        log.duration = values.duration;
        log.vigorous = values.vigorous;

        const updatedStart:Date = new Date();
        updatedStart.setDate(values.date.getDate());
        updatedStart.setMonth(values.date.getMonth());
        updatedStart.setFullYear(values.date.getFullYear());
        updatedStart.setHours(values.date.getHours());
        updatedStart.setMinutes(values.date.getMinutes());

        log.start = updatedStart;
        
        this.onChange(log);
    }

    setDisabledState(isDisabled: boolean): void {
        this.disabled = isDisabled;
        if(this.disabled) {
            this.form.disable();
        } else {
            this.form.enable();
        }
    }

    ngOnDestroy() {
        super.ngOnDestroy();
        if(this.formSubscription) {
            this.formSubscription.unsubscribe();
        }
        if(this.formStatusSubscription) {
            this.formStatusSubscription.unsubscribe();
        }
        if(this.ngFormSubmitSubscription) {
            this.ngFormSubmitSubscription.unsubscribe();
        }
    }


}
