import { Component } from '@angular/core';
import { ViewController, NavParams } from 'ionic-angular';
import { ActivityPlanService } from '@heartsteps/activity-plan.service';
import { FormGroup, FormControl, Validators } from '@angular/forms';

@Component({
    selector: 'activity-plan-modal',
    templateUrl: 'plan.modal.html'
})
export class PlanModal {

    private durationChoices: Array<number> = [
        5, 10, 15, 20, 25, 30, 
    ]

    private planForm:FormGroup

    constructor(
        params:NavParams,
        private viewCtrl:ViewController,
        private activityPlanService:ActivityPlanService,
    ) {
        this.planForm = new FormGroup({
            duration: new FormControl('', Validators.required),
            time: new FormControl('', Validators.required),
            intensity: new FormControl('', Validators.required)
        })
    }

    dismiss() {
        this.viewCtrl.dismiss()
    }

    save() {
        if (this.planForm.valid) {
            this.activityPlanService.createPlan(this.planForm.value)
            .then((plan) => {
                this.viewCtrl.dismiss(plan)
            })
            .catch(() => {
                console.log("Error!")
            })
        }
    }

}