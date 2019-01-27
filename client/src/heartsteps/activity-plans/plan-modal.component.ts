import { Component, ViewChild } from "@angular/core";
import { NavParams, ViewController } from "ionic-angular";
import { ActivityPlan } from "./activity-plan.model";
import { ModalDialogComponent } from "@infrastructure/dialogs/modal-dialog.component";


@Component({
    templateUrl: './plan-modal.component.html'
})
export class PlanModalComponent {

    @ViewChild(ModalDialogComponent) modal: ModalDialogComponent;

    public activityPlan:ActivityPlan

    constructor(
        params:NavParams,
        private viewCtrl:ViewController,
    ) {
        this.activityPlan = params.get('activityPlan');
    }

    dismiss() {
        this.modal.dismiss();
    }

}