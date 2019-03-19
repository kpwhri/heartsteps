import { Component } from "@angular/core";
import { PlanFormComponent } from "./plan-form.component";
import { FormControl } from "@angular/forms";

@Component({
    selector: 'activity-plan-complete-form',
    templateUrl: './complete-plan-form.component.html'
})
export class CompletePlanForm extends PlanFormComponent {

    public setPlanForm(activityPlan) {
        super.setPlanForm(activityPlan);
        this.planForm.addControl('enjoyed', new FormControl());
        this.planForm.addControl('effort', new FormControl());
    }

}
