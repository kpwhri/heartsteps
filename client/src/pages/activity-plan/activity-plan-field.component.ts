import { Component, forwardRef, ElementRef, Renderer2 } from "@angular/core";
import { AbstractField } from "@infrastructure/form/abstract-field";
import { NG_VALUE_ACCESSOR, FormGroup, FormControl, Validators, FormGroupDirective } from "@angular/forms";
import { ActivityPlan } from "@heartsteps/activity-plans/activity-plan.model";
import { Subscription } from "rxjs";
import { DateFactory } from "@infrastructure/date.factory";
import { DailyTimeService } from "@heartsteps/daily-times/daily-times.service";
import { SelectOption } from "@infrastructure/dialogs/select-dialog.controller";
import { ActivityType } from "@heartsteps/activity-types/activity-type.service";
import { ActivityPlanService } from "@heartsteps/activity-plans/activity-plan.service";

@Component({
    selector: 'activity-plan-field',
    templateUrl: './activity-plan-field.component.html',
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            multi: true,
            useExisting: forwardRef(() => ActivityPlanField)
        }
    ]
})
export class ActivityPlanField extends AbstractField {
    public planForm: FormGroup;
    public availableDates: Array<Date>;
    public dailyTimes: Array<SelectOption>;
    public activityTypes: Array<ActivityType>;

    private activityPlan: ActivityPlan;
    private planFormSubscription:Subscription;
    private planFormStatusSubscription: Subscription;
    private activityTypeSubscription: Subscription;

    public isFormField: boolean = false;

    constructor(
        formGroup: FormGroupDirective,
        element: ElementRef,
        renderer: Renderer2,
        private dateFactory: DateFactory,
        private dailyTimeService: DailyTimeService,
        private activityPlanService: ActivityPlanService
    ) {
        super(formGroup, element, renderer)

        this.dailyTimes = [];
        this.dailyTimeService.times.value.forEach((dailyTime) => {
            this.dailyTimes.push({
                name: dailyTime.name,
                value: dailyTime.key
            });
        });
        this.activityPlanService.watchActivityTypes()
        .subscribe((activityTypes) => {
            this.activityTypes = activityTypes;
        });
    }

    public writeValue(activityPlan:ActivityPlan) {
        if(activityPlan) {
            this.activityPlan = activityPlan;
            this.initializeForm();
        }

    }

    private initializeForm() {
        this.availableDates = this.dateFactory.getWeek(this.activityPlan.date);

        this.planForm = new FormGroup({
            activity: new FormControl(this.activityPlan.type, Validators.required),
            duration: new FormControl(this.activityPlan.duration || 30, Validators.required),
            date: new FormControl(this.activityPlan.date, Validators.required),
            timeOfDay: new FormControl(this.activityPlan.timeOfDay, Validators.required),
            vigorous: new FormControl(this.activityPlan.vigorous, Validators.required)
        });

        this.formGroup.ngSubmit.subscribe(() => {
            Object.keys(this.planForm.controls).forEach((key) => {
                this.planForm.controls[key].markAsDirty();
                this.planForm.controls[key].updateValueAndValidity();
            });
        });

        setTimeout(() => {
            this.updatePlanErrors();
        }, 100);

        this.planFormStatusSubscription = this.planForm.statusChanges.subscribe(() => {
            this.updatePlanErrors();
            this.updatePlanTouched();
        });

        this.planFormSubscription = this.planForm.valueChanges.subscribe((values:any) => {
            this.updatePlan();
        });
    }

    private updatePlanErrors() {
        if(this.planForm.valid) {
            this.control.setErrors(null);
        } else {
            this.control.setErrors({
                'invalidPlan': true
            });
        }
    }

    private updatePlanTouched() {
        if(this.planForm.touched) {
            this.control.markAsTouched();
        } else {
            this.control.markAsUntouched();
        }
    }

    private updatePlan() {
        const values:any = Object.assign({}, this.planForm.value);

        const plan = new ActivityPlan();
        plan.id = this.activityPlan.id;
        plan.date = values.date;
        plan.timeOfDay = values.timeOfDay;
        plan.type = values.activity;
        plan.duration = values.duration;
        plan.vigorous = values.vigorous;

        this.onChange(plan);
    }

    setDisabledState(isDisabled: boolean): void {
        this.disabled = isDisabled;
        if(this.disabled) {
            this.planForm.disable();
        } else {
            this.planForm.enable();
        }
    }

    ngOnDestroy() {
        super.ngOnDestroy();
        if(this.planFormSubscription) {
            this.planFormSubscription.unsubscribe();
        }
        if(this.planFormStatusSubscription) {
            this.planFormStatusSubscription.unsubscribe();
        }
        if (this.activityTypeSubscription) {
            this.activityTypeSubscription.unsubscribe();
        }
    }


}
