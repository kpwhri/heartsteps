import { Component, forwardRef, ElementRef, Renderer2 } from "@angular/core";
import { AbstractField } from "@infrastructure/form/abstract-field";
import { NG_VALUE_ACCESSOR, FormGroup, FormControl, Validators, FormGroupDirective } from "@angular/forms";
import { ActivityPlan } from "@heartsteps/activity-plans/activity-plan.model";
import { Subscription } from "rxjs";
import { DateFactory } from "@infrastructure/date.factory";
import { DailyTimeService, DailyTime } from "@heartsteps/daily-times/daily-times.service";
import { SelectOption } from "@infrastructure/dialogs/select-dialog.controller";

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

    private planFormSubscription:Subscription;

    public isFormField: boolean = false;

    constructor(
        formGroup: FormGroupDirective,
        element: ElementRef,
        renderer: Renderer2,
        private dateFactory: DateFactory,
        private dailyTimeService: DailyTimeService
    ) {
        super(formGroup, element, renderer)

        this.dailyTimes = [];
        this.dailyTimeService.times.value.forEach((dailyTime) => {
            this.dailyTimes.push({
                name: dailyTime.name,
                value: dailyTime.key
            });
        });
    }

    public writeValue(activityPlan:ActivityPlan) {
        this.planForm = new FormGroup({
            activity: new FormControl(activityPlan.type, Validators.required),
            duration: new FormControl(activityPlan.duration || 30, Validators.required),
            date: new FormControl(activityPlan.date, Validators.required),
            timeOfDay: new FormControl(activityPlan.timeOfDay, Validators.required),
            vigorous: new FormControl(activityPlan.vigorous, Validators.required)
        });

        this.availableDates = this.dateFactory.getWeek(activityPlan.date);

        this.planFormSubscription = this.planForm.valueChanges.subscribe((values:any) => {
            const plan = new ActivityPlan();
            plan.id = activityPlan.id;
            plan.date = values.date;
            plan.timeOfDay = values.timeOfDay;
            plan.type = values.activity;
            plan.duration = values.duration;
            plan.vigorous = values.vigorous;
            this.onChange(plan);
        });

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
    }


}
