import { NgModule } from "@angular/core";

import { DatePickerDialogController } from "./date-picker-dialog.controller";
import { SelectDialogController } from "./select-dialog.controller";
import { ModalDialogComponent } from "./modal-dialog.component";
import { IonicPageModule } from "ionic-angular";


@NgModule({
    imports: [
        IonicPageModule.forChild(ModalDialogComponent)
    ],
    declarations: [
        ModalDialogComponent
    ],
    exports: [
        ModalDialogComponent
    ],
    providers: [
        DatePickerDialogController,
        SelectDialogController
    ]
})
export class DialogsModule {}
