import { Injectable } from "@angular/core";
import { ActivityPlan } from "./activity-plan.model";
import { PlanModalComponent } from "./plan-modal.component";
import { ModalDialogController } from "@infrastructure/dialogs/modal-dialog.controller";


@Injectable()
export class PlanModalController extends ModalDialogController {

    public show(plan:ActivityPlan):Promise<boolean> {
        return this.createModal(PlanModalComponent, {
            activityPlan: plan
        });
    }
}
