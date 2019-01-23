import { NgModule } from "@angular/core";
import { DurationFieldComponent } from "./duration-field.component";
import { FormsModule } from "@angular/forms";
import { BrowserModule } from "@angular/platform-browser";

import { TextFieldComponent } from "./text-field.component";
import { YearFieldComponent } from "./year-field.component";
import { DateFieldComponent } from "./date-field.component";
import { TimeFieldComponent } from "./time-field.component";
import { DialogsModule } from "@infrastructure/dialogs/dialogs.module";


@NgModule({
    imports: [
        BrowserModule,
        FormsModule,
        DialogsModule
    ],
    declarations: [
        DateFieldComponent,
        DurationFieldComponent,
        TextFieldComponent,
        TimeFieldComponent,
        YearFieldComponent
    ],
    exports: [
        DateFieldComponent,
        DurationFieldComponent,
        TextFieldComponent,
        TimeFieldComponent,
        YearFieldComponent
    ]
})
export class FormModule {}
