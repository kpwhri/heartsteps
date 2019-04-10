import { Component, ViewChild } from "@angular/core";
import { ModalDialogComponent } from "@infrastructure/dialogs/modal-dialog.component";
import { ActivityTypeService } from "./activity-type.service";
import { FormGroup, FormControl, Validators } from "@angular/forms";
import { FormComponent } from "@infrastructure/form/form.component";
import { LoadingService } from "@infrastructure/loading.service";


@Component({
    templateUrl: './activity-type-create-modal.component.html'
})
export class ActivityTypeCreateModalComponent {
    @ViewChild(ModalDialogComponent) modal: ModalDialogComponent;
    @ViewChild(FormComponent) form: FormComponent;

    public createForm: FormGroup

    constructor(
        private activityTypeService: ActivityTypeService,
        private loadingService: LoadingService
    ) {
        this.createForm = new FormGroup({
            name: new FormControl('', Validators.required)
        });
    }

    public save() {
        this.loadingService.show('Creating activity type')
        const name = this.createForm.get('name');
        return this.activityTypeService.create(name.value)
        .then((activityType) => {
            this.modal.dismiss(activityType);
        })
        .catch((error) => {
            this.form.setError(error);
        })
        .then(() => {
            this.loadingService.dismiss();
        });
    }

    public delete() {

    }

    public dismiss() {
        this.modal.dismiss();
    }

}
