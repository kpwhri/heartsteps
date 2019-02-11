import { Component, ViewChild } from "@angular/core";
import { FormComponent } from "@infrastructure/form/form.component";
import { ModalDialogComponent } from "@infrastructure/dialogs/modal-dialog.component";
import { ActivityLogService } from "./activity-log.service";
import { FormGroup, FormControl, Validators } from "@angular/forms";
import { LoadingService } from "@infrastructure/loading.service";


@Component({
    templateUrl: './activity-enjoyed-modal.component.html'
})
export class ActivityEnjoyedModalComponent {

    @ViewChild(FormComponent) private formCtrl: FormComponent
    @ViewChild(ModalDialogComponent) private modalCtrl: ModalDialogComponent

    public form: FormGroup;

    constructor(
        private activityLogService: ActivityLogService,
        private loadingService: LoadingService
    ) {
        this.form = new FormGroup({
            enjoyed: new FormControl(undefined, Validators.required)
        });
    }

    public save() {
        this.formCtrl.submit()
        .then(() => {
            this.loadingService.show('Saving activity');
            // save activity log
        })
        .catch(() => {
            console.log('Errors');
        })
        .then(() => {
            this.loadingService.dismiss();
            this.modalCtrl.dismiss();
        });
    }

    public skip() {
        this.modalCtrl.dismiss();
    }

}

