import { Component } from "@angular/core";
import { NavParams, ViewController } from "ionic-angular";
import { ActivityPlan } from "./activity-plan.model";


@Component({
    templateUrl: './plan-modal.component.html'
})
export class PlanModalComponent {

    public activityPlan:ActivityPlan

    constructor(
        params:NavParams,
        private viewCtrl:ViewController,
    ) {
        this.activityPlan = params.get('activityPlan');
    }

    dismiss() {
        this.viewCtrl.dismiss();
    }

}