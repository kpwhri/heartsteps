import { Component, ViewChild } from "@angular/core";
import { ModalDialogComponent } from "@infrastructure/dialogs/modal-dialog.component";
import { FormGroup, FormControl, Validators } from "@angular/forms";

@Component({
    templateUrl: './barrier-modal.component.html'
})
export class BarrierModalComponent {
    @ViewChild(ModalDialogComponent) modal: ModalDialogComponent;

    public form: FormGroup;

    constructor() {
        this.form = new FormGroup({
            name: new FormControl('', [
                Validators.required,
                Validators.minLength(3),
                Validators.maxLength(150)
            ])
        })
    }

    public save() {
        const barrier = this.form.get('name').value;
        this.modal.dismiss(barrier);
    }

    public dismiss() {
        this.modal.dismiss();
    }

}
