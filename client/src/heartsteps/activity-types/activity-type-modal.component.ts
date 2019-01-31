import { Component, ViewChild } from "@angular/core";
import { ActivityTypeService, ActivityType } from "./activity-type.service";
import { AlertDialogController } from "@infrastructure/alert-dialog.controller";
import { ModalDialogComponent } from "@infrastructure/dialogs/modal-dialog.component";

@Component({
    templateUrl: './activity-type-modal.component.html'
})
export class ActivityTypeModalComponent {
    @ViewChild(ModalDialogComponent) modal: ModalDialogComponent;

    public activityTypes: Array<ActivityType> = [];

    constructor(
        private activityTypeService: ActivityTypeService,
        private alertDialog: AlertDialogController
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
        this.alertDialog.show('Not implemented');
    }

    public dismiss() {
        this.modal.dismiss();
    }

}
