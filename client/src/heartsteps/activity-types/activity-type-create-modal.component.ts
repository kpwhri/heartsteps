import { Component, ViewChild } from "@angular/core";
import { ModalDialogComponent } from "@infrastructure/dialogs/modal-dialog.component";
import { ActivityTypeService } from "./activity-type.service";
import { FormGroup, FormControl, Validators } from "@angular/forms";
import { FormComponent } from "@infrastructure/form/form.component";


@Component({
    templateUrl: './activity-type-create-modal.component.html'
})
export class ActivityTypeCreateModalComponent {
    @ViewChild(ModalDialogComponent) modal: ModalDialogComponent;
    @ViewChild(FormComponent) form: FormComponent;

    public createForm: FormGroup

    constructor(
        private activityTypeService: ActivityTypeService
    ) {
        this.createForm = new FormGroup({
            name: new FormControl('', Validators.required)
        });
    }

    public save() {
        this.form.submit()
        .then(() => {
            const name = this.createForm.get('name');
            return this.activityTypeService.create(name.value);
        })
        .then((activityType) => {
            this.modal.dismiss(activityType);
        });
    }

    public delete() {

    }

    public dismiss() {
        this.modal.dismiss();
    }

}
