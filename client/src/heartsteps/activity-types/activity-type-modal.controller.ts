import { Injectable } from "@angular/core";
import { ModalDialogController } from "@infrastructure/dialogs/modal-dialog.controller";
import { ActivityType } from "./activity-type.service";
import { ActivityTypeModalComponent } from "./activity-type-modal.component";

@Injectable()
export class ActivityTypeModalController extends ModalDialogController {

    public pick(): Promise<ActivityType> {
        return this.createModal(ActivityTypeModalComponent)
        .then((activityType) => {
            if(activityType) {
                return Promise.resolve(activityType);
            } else {
                return Promise.reject('No activity type chosen');
            }
        })
    }

}
