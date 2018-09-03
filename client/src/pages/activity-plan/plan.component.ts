import { Component, OnInit, Input } from '@angular/core';
import { ModalController } from 'ionic-angular';
import { PlanModal } from '@pages/activity-plan/plan.modal';

@Component({
    selector: 'activity-plan',
    templateUrl: './plan.component.html',
    inputs: ['plan']
})
export class PlanComponent implements OnInit {

    @Input() plan:any

    public activity:string
    public duration:string
    public intensity:string
    public time:string

    constructor(
        private modalCtrl:ModalController
    ) {}

    ngOnInit(){
        if(this.plan) {
            this.activity = this.plan.activity
            this.duration = this.plan.duration
            this.intensity = this.plan.intensity
            this.time = this.plan.time
        } else {
            this.activity = "Not set"
            this.duration = "Not set"
            this.intensity = "Not set"
            this.time = "Not set"
        }
    }
    
    openPlan() {
        let modal = this.modalCtrl.create(PlanModal);

        modal.onDidDismiss((plan:any) => {
            if(plan) {
                this.activity = plan.activity
                this.duration = plan.duration
                this.intensity = plan.intensity
                this.time = plan.time
            }
        });

        modal.present()
    }
}
