import { Component, forwardRef } from "@angular/core";
import { AbstractField } from "@infrastructure/form/abstract-field";
import { NG_VALUE_ACCESSOR, FormGroup, FormControl, Validators } from "@angular/forms";
import { ActivityPlan } from "@heartsteps/activity-plans/activity-plan.model";
import { Subscription } from "rxjs";

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

    public activityPlan:ActivityPlan;
    public planForm: FormGroup;

    private planFormSubscription:Subscription;

    public isFormField: boolean = false;

    public writeValue(activityPlan:ActivityPlan) {
        this.activityPlan = activityPlan;

        this.planForm = new FormGroup({
            activity: new FormControl(this.activityPlan.type, Validators.required),
            duration: new FormControl(this.activityPlan.duration || 30, Validators.required),
            date: new FormControl(this.activityPlan.date, Validators.required),
            timeOfDay: new FormControl(null, Validators.required),
            vigorous: new FormControl(this.activityPlan.vigorous, Validators.required)
        });

        this.planFormSubscription = this.planForm.valueChanges.subscribe((values:any) => {
            const plan = new ActivityPlan();
            plan.id = this.activityPlan.id;
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
