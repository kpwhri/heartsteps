import { NgModule } from "@angular/core";
import { DurationFieldComponent } from "./duration-field.component";
import { FormsModule } from "@angular/forms";
import { BrowserModule } from "@angular/platform-browser";
import { TextFieldComponent } from "./text-field.component";
import { YearFieldComponent } from "./year-field.component";


@NgModule({
    imports: [
        BrowserModule,
        FormsModule
    ],
    declarations: [
        DurationFieldComponent,
        TextFieldComponent,
        YearFieldComponent
    ],
    exports: [
        DurationFieldComponent,
        TextFieldComponent,
        YearFieldComponent
    ]
})
export class FormModule {}
