import { NgModule } from "@angular/core";
import { FormModule } from "@infrastructure/form/form.module";
import { ActivityTypeFieldComponent } from "./activity-type-field.component";
import { ActivityTypeService } from "./activity-type.service";
import { BrowserModule } from "@angular/platform-browser";
import { DialogsModule } from "@infrastructure/dialogs/dialogs.module";
import { ActivityTypeModalComponent } from "./activity-type-modal.component";
import { IonicPageModule } from "ionic-angular";
import { ActivityIntensityFieldComponent } from "./activity-intensity-field.component";

@NgModule({
    imports: [
        BrowserModule,
        DialogsModule,
        FormModule,
        IonicPageModule.forChild(ActivityTypeModalComponent)
    ],
    declarations: [
        ActivityTypeFieldComponent,
        ActivityTypeModalComponent,
        ActivityIntensityFieldComponent
    ],
    entryComponents: [
        ActivityTypeModalComponent
    ],
    exports: [
        ActivityTypeFieldComponent,
        ActivityIntensityFieldComponent
    ],
    providers: [
        ActivityTypeService
    ]
})
export class ActivityTypeModule {}
