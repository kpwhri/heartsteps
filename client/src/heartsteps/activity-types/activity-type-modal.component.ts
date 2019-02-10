import { Component, ViewChild } from "@angular/core";
import { ActivityTypeService, ActivityType } from "./activity-type.service";
import { ModalDialogComponent } from "@infrastructure/dialogs/modal-dialog.component";
import { ModalDialogController } from "@infrastructure/dialogs/modal-dialog.controller";
import { ActivityTypeCreateModalComponent } from "./activity-type-create-modal.component";

@Component({
    templateUrl: './activity-type-modal.component.html',
    providers: [
        ModalDialogController
    ]
})
export class ActivityTypeModalComponent {
    @ViewChild(ModalDialogComponent) modal: ModalDialogComponent;

    public activityTypes: Array<ActivityType> = [];

    constructor(
        private activityTypeService: ActivityTypeService,
        private modalDialogController: ModalDialogController
    ) {
        this.activityTypeService.load();
        this.activityTypeService.activityTypes.subscribe((activityTypes) => {
            this.activityTypes = activityTypes;
        });
    }

    public select(activityType: ActivityType) {
        this.modal.dismiss(activityType);
    }

    public create() {
        this.modalDialogController.createModal(ActivityTypeCreateModalComponent)
        .then((activityType) => {
            if(activityType) {
                this.modal.dismiss(activityType);
            }
        })
        .catch(() => {
            console.log('Create modal closed');
        })
    }

    public dismiss() {
        this.modal.dismiss();
    }

}
