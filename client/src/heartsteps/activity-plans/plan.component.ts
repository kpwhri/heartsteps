import { Component, Input } from '@angular/core';
import { ActivityPlan } from './activity-plan.model';
import { PlanModalController } from './plan-modal.controller';

@Component({
    selector: 'activity-plan',
    templateUrl: './plan.component.html',
    inputs: ['plan']
})
export class PlanComponent {

    @Input() plan:ActivityPlan

    constructor(
        private planModal: PlanModalController
    ) {}
    
    openPlan() {
        this.planModal.show(this.plan);
    }
}
