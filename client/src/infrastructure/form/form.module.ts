import { NgModule } from "@angular/core";
import { DurationFieldComponent } from "./duration-field.component";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import { BrowserModule } from "@angular/platform-browser";

import { TextFieldComponent } from "./text-field.component";
import { YearFieldComponent } from "./year-field.component";
import { DateFieldComponent } from "./date-field.component";
import { TimeFieldComponent } from "./time-field.component";
import { DialogsModule } from "@infrastructure/dialogs/dialogs.module";
import { EmailFieldComponent } from "./email-field.component";
import { PhoneFieldComponent } from "./phone-field.component";
import { FormComponent } from "./form.component";
import { AbstractField } from "./abstract-field";
import { SelectFieldComponent } from "./select-field.component";


@NgModule({
    imports: [
        BrowserModule,
        FormsModule,
        ReactiveFormsModule,
        DialogsModule
    ],
    declarations: [
        AbstractField,
        DateFieldComponent,
        DurationFieldComponent,
        EmailFieldComponent,
        FormComponent,
        PhoneFieldComponent,
        SelectFieldComponent,
        TextFieldComponent,
        TimeFieldComponent,
        YearFieldComponent
    ],
    exports: [
        DateFieldComponent,
        DurationFieldComponent,
        EmailFieldComponent,
        FormComponent,
        PhoneFieldComponent,
        TextFieldComponent,
        TimeFieldComponent,
        YearFieldComponent
    ]
})
export class FormModule {}
