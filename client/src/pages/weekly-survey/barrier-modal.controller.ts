import { Injectable } from "@angular/core";
import { ModalDialogController } from "@infrastructure/dialogs/modal-dialog.controller";
import { BarrierModalComponent } from "./barrier-modal.component";


@Injectable()
export class BarrierModalController extends ModalDialogController {

    public newBarrier(): Promise<string> {
        return this.createModal(BarrierModalComponent)
        .then((response) => {
            if(response && typeof(response) === 'string' && response !== '') {
                return Promise.resolve(response);
            } else {
                return Promise.reject('No string returned')
            }
        });
    }

}
