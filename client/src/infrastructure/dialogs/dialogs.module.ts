import { NgModule } from "@angular/core";

import { DatePickerDialogController } from "./date-picker-dialog.controller";
import { SelectDialogController } from "./select-dialog.controller";


@NgModule({
    providers: [
        DatePickerDialogController,
        SelectDialogController
    ]
})
export class DialogsModule {}
