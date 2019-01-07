import { Injectable } from "@angular/core";
import { ActivityPlan } from "./activity-plan.model";
import { ModalController } from "ionic-angular";
import { PlanModalComponent } from "./plan-modal.component";


@Injectable()
export class PlanModalController {

    constructor(
        private modalCtrl: ModalController
    ) {}

    public show(plan:ActivityPlan):Promise<boolean> {
        return new Promise((resolve) => {
            const modal = this.modalCtrl.create(PlanModalComponent, {
                activityPlan: plan
            });
            modal.onDidDismiss(() => {
                resolve(true);
            });
            modal.present()
        })
    }
}
