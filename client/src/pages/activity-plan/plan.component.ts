import { Component, OnInit, Input } from '@angular/core';
import { ModalController } from 'ionic-angular';
import { PlanModal } from '@pages/activity-plan/plan.modal';
import { Activity } from '@heartsteps/activity.model';

@Component({
    selector: 'activity-plan',
    templateUrl: './plan.component.html',
    inputs: ['activity']
})
export class PlanComponent {

    @Input() activity:Activity

    constructor(
        private modalCtrl:ModalController
    ) {}
    
    openPlan() {
        let modal = this.modalCtrl.create(PlanModal, {
            activity: this.activity
        });

        modal.onDidDismiss((activity:Activity) => {
            if(activity) {
                this.activity = activity
            }
        });

        modal.present()
    }
}
